from django.db import models

# Create your models here.


class Application(models.Model):
    applicant_id = models.IntegerField(default=0)
    job_id = models.IntegerField()
    resume = models.CharField(max_length=30)
    cover_letter = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(default=0)  # 0: waiting, 1: view, 2:rejected

    def __str__(self):
        return self.applicant_id + "" + self.job_id
