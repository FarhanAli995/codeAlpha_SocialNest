from django.conf import settings
from django.db import models

from posts.models import Post


class Notification(models.Model):
    NOTIF_TYPES = [('like', 'Like'), ('comment', 'Comment'), ('follow', 'Follow')]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='notifications', on_delete=models.CASCADE
    )
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    notif_type = models.CharField(max_length=20, choices=NOTIF_TYPES)
    post = models.ForeignKey(Post, null=True, blank=True, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.notif_type} from {self.sender} to {self.recipient}'
