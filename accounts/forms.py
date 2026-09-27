from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Profile


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('bio', 'location', 'website', 'avatar', 'cover_image')
        widgets = {
            'bio': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Tell people about yourself',
                'class': 'field-input',
            }),
            'location': forms.TextInput(attrs={
                'placeholder': 'San Francisco, CA',
                'class': 'field-input',
            }),
            'website': forms.URLInput(attrs={
                'placeholder': 'https://example.com',
                'class': 'field-input',
            }),
            'avatar': forms.ClearableFileInput(attrs={
                'class': 'visually-hidden',
                'accept': 'image/*',
            }),
            'cover_image': forms.ClearableFileInput(attrs={
                'class': 'visually-hidden',
                'accept': 'image/*',
            }),
        }

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        # Keep the existing/default avatar if no new file was uploaded.
        if not avatar and self.instance.pk:
            return self.instance.avatar
        return avatar

    def clean_cover_image(self):
        cover = self.cleaned_data.get('cover_image')
        if not cover and self.instance.pk:
            return self.instance.cover_image
        return cover
