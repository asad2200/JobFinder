from django.db import models

# Create your models here.


class Job(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    min_salary = models.FloatField()
    max_salary = models.FloatField()
    freq = models.CharField(max_length=10)
    location = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class Qualification(models.Model):
    Job_id = models.IntegerField()
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name