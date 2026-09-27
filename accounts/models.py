from django.conf import settings
from django.db import models


class Profile(models.Model):
    ROLE_CHOICES = [('user', 'User'), ('moderator', 'Moderator'), ('admin', 'Admin')]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=120, blank=True)
    website = models.URLField(max_length=200, blank=True)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png')
    cover_image = models.ImageField(upload_to='covers/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} profile'
