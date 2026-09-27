from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from accounts.models import Profile
from notifications.models import Notification

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Like, Post


def feed(request):
    query = request.GET.get('q', '').strip()

    if request.user.is_authenticated:
        following_ids = Follow.objects.filter(
            follower=request.user
        ).values_list('following_id', flat=True)
        posts = Post.objects.filter(
            Q(author=request.user) | Q(author_id__in=following_ids)
        ).select_related('author')
    else:
        posts = Post.objects.all().select_related('author')

    if query:
        posts = posts.filter(
            Q(text__icontains=query)
            | Q(author__username__icontains=query)
        )

    liked_ids = set()
    suggested_users = []
    if request.user.is_authenticated:
        liked_ids = set(
            Like.objects.filter(user=request.user).values_list('post_id', flat=True)
        )
        following_ids = set(
            Follow.objects.filter(follower=request.user).values_list('following_id', flat=True)
        )
        suggested_users = (
            User.objects.exclude(pk=request.user.pk)
            .exclude(pk__in=following_ids)
            .select_related('profile')[:4]
        )

    return render(request, 'posts/feed.html', {
        'posts': posts,
        'liked_ids': liked_ids,
        'suggested_users': suggested_users,
        'comment_form': CommentForm(),
        'query': query,
    })


def explore(request):
    query = request.GET.get('q', '').strip()

    posts = Post.objects.all().select_related('author')
    people = User.objects.select_related('profile').exclude(pk=request.user.pk if request.user.is_authenticated else None)

    if query:
        posts = posts.filter(
            Q(text__icontains=query)
            | Q(author__username__icontains=query)
        )
        people = people.filter(
            Q(username__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
        )

    liked_ids = set()
    if request.user.is_authenticated:
        liked_ids = set(
            Like.objects.filter(user=request.user).values_list('post_id', flat=True)
        )

    return render(request, 'posts/explore.html', {
        'posts': posts[:30],
        'people': people[:12],
        'liked_ids': liked_ids,
        'query': query,
    })


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Post created.')
            return redirect('posts:feed')
    else:
        form = PostForm()
    return render(request, 'posts/post_form.html', {'form': form})


def post_detail(request, pk):
    post = get_object_or_404(Post.objects.select_related('author'), pk=pk)
    liked = False
    if request.user.is_authenticated:
        liked = Like.objects.filter(post=post, user=request.user).exists()
    return render(request, 'posts/post_detail.html', {
        'post': post,
        'liked': liked,
        'comments': post.comments.select_related('author'),
        'comment_form': CommentForm(),
    })


@login_required
@require_POST
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        messages.error(request, 'You can only delete your own posts.')
        return redirect('posts:post_detail', pk=pk)
    post.delete()
    messages.success(request, 'Post deleted.')
    return redirect('posts:feed')


@login_required
@require_POST
def like_toggle(request, pk):
    post = get_object_or_404(Post, pk=pk)
    like, created = Like.objects.get_or_create(post=post, user=request.user)
    if created:
        Post.objects.filter(pk=post.pk).update(likes_count=post.likes.count())
        if post.author != request.user:
            Notification.objects.create(
                recipient=post.author,
                sender=request.user,
                notif_type='like',
                post=post,
            )
    else:
        like.delete()
        Post.objects.filter(pk=post.pk).update(likes_count=post.likes.count())
    return HttpResponseRedirect(reverse('posts:post_detail', args=[pk]))


@login_required
@require_POST
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
        Post.objects.filter(pk=post.pk).update(comments_count=post.comments.count())
        if post.author != request.user:
            Notification.objects.create(
                recipient=post.author,
                sender=request.user,
                notif_type='comment',
                post=post,
            )
        messages.success(request, 'Comment added.')
    else:
        messages.error(request, 'Comment cannot be empty.')
    return HttpResponseRedirect(reverse('posts:post_detail', args=[pk]))
