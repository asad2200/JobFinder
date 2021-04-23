from django.shortcuts import render
from employer.models import Job, Qualification
from dashboard.models import Profile

# Create your views here.


def view_job(request, code):
    profile = Profile.objects.get(user_id=request.user.id)

    job = Job.objects.get(code=code)
    qualifications = Qualification.objects.filter(job_id=job.id)

    return render(request, "jobs/job.html", {
        'name': profile.name,
        'job': job,
        'qualifications': qualifications,
    })
