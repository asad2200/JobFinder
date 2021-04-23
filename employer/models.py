from django.db import models
import uuid
# Create your models here.


class Job(models.Model):
    profile = models.IntegerField()
    title = models.CharField(max_length=100)
    description = models.TextField()
    min_salary = models.FloatField()
    max_salary = models.FloatField()
    freq = models.CharField(max_length=10)
    location = models.CharField(max_length=255)
    code = models.UUIDField(default=uuid.uuid4, unique=True)

    def __str__(self):
        return self.title


class Qualification(models.Model):
    job_id = models.IntegerField()
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name
