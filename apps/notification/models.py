from django.db import models
from django.conf import settings
from django.utils.text import slugify
import hashlib

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True, blank=True, null=True, max_length=255)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return self.message
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = hashlib.sha256(self.message.encode()).hexdigest()[:15]
        super().save(*args, **kwargs)