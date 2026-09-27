from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'image', 'video')
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'placeholder': "What's on your mind?"}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Write a comment...'}),
        }
