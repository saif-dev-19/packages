from django.db import models

# Create your models here.
class Notification(models.Model):
    user_id = models.IntegerField()

    title = models.CharField(max_length=255)
    message = models.TextField()

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)