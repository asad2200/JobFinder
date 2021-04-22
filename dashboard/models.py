from django.db import models

# Create your models here.


class Profile(models.Model):
    user_id = models.IntegerField()
    role = models.IntegerField()  # 0:Employer/HR, 1:Job Seeker
    name = models.CharField(max_length=255)
