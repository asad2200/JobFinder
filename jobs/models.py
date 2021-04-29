from django.db import models

# Create your models here.


class Application(models.Model):
    class Status(models.IntegerChoices):
        waiting = 0
        viewed = 1
        accepted = 2
        rejected = 3
    applicant_id = models.IntegerField(default=0)
    job_id = models.IntegerField()
    resume = models.CharField(max_length=30)
    cover_letter = models.TextField()
    timestamp = models.DateTimeField(auto_now=True)
    status = models.IntegerField(choices=Status.choices)

    # def __str__(self):
    #     return self.applicant_id + "" + self.job_id
