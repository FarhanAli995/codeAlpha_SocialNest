from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from notifications.models import Notification
from posts.models import Follow

from .forms import ProfileForm, SignUpForm
from .models import Profile


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True


class CustomLogoutView(LogoutView):
    next_page = 'accounts:login'


def register(request):
    if request.user.is_authenticated:
        return redirect('posts:feed')
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)
            login(request, user)
            messages.success(request, 'Welcome to SocialNest!')
            return redirect('posts:feed')
    else:
        form = SignUpForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def own_profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    posts = request.user.posts.all()
    return render(request, 'accounts/profile.html', {
        'profile': profile,
        'profile_user': request.user,
        'posts': posts,
        'is_own_profile': True,
    })


@login_required
def profile_detail(request, username):
    profile_user = get_object_or_404(User, username=username)
    profile, _ = Profile.objects.get_or_create(user=profile_user)
    is_following = Follow.objects.filter(follower=request.user, following=profile_user).exists()
    return render(request, 'accounts/profile.html', {
        'profile': profile,
        'profile_user': profile_user,
        'posts': profile_user.posts.all(),
        'is_own_profile': profile_user == request.user,
        'is_following': is_following,
        'followers_count': profile_user.followers.count(),
        'following_count': profile_user.following.count(),
    })


@login_required
def edit_profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)

            # Remove the current avatar if the user asked to clear it
            # and did not upload a replacement in the same request.
            if request.POST.get('avatar-clear') and not request.FILES.get('avatar'):
                if profile.avatar:
                    profile.avatar.delete(save=False)
                profile.avatar = ''

            profile.save()
            messages.success(request, 'Profile updated.')
            return redirect('accounts:own_profile')
        messages.error(request, 'Please fix the errors below.')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'accounts/edit_profile.html', {'form': form})


@login_required
@require_POST
def follow_toggle(request, username):
    target = get_object_or_404(User, username=username)
    if target == request.user:
        messages.error(request, 'You cannot follow yourself.')
        return HttpResponseRedirect(reverse('accounts:profile_detail', args=[username]))

    follow, created = Follow.objects.get_or_create(follower=request.user, following=target)
    if not created:
        follow.delete()
        messages.info(request, f'Unfollowed {target.username}.')
    else:
        Notification.objects.create(
            recipient=target,
            sender=request.user,
            notif_type='follow',
        )
        messages.success(request, f'Now following {target.username}.')
    return HttpResponseRedirect(reverse('accounts:profile_detail', args=[username]))
