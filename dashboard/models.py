from django.core.checks import messages
from django.db import models

# Create your models here.


class Profile(models.Model):
    user_id = models.IntegerField()
    role = models.IntegerField()  # 0:Employer/HR, 1:Job Seeker
    name = models.CharField(max_length=255)
    zoom_auth_token = models.TextField(default='')
    zoom_refresh_token = models.TextField(default='')

    def __str__(self):
        return self.name


class ChatMessage(models.Model):
    from_id = models.IntegerField()
    to_id = models.IntegerField()
    application_id = models.IntegerField()
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now=True)
    public = models.BooleanField(default=True)
