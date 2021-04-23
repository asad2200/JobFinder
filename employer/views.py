from django.shortcuts import render
from django.http import HttpResponseRedirect

from dashboard.models import Profile
from .models import Job, Qualification

# Create your views here.


def index(request):
    profile = Profile.objects.get(user_id=request.user.id)
    return render(request, "employer/index.html", {
        'name': profile.name,
    })


def post_job(request):
    profile = Profile.objects.get(user_id=request.user.id)

    if request.method == 'POST':
        title = request.POST["title"]
        description = request.POST["decription"]
        qualification = request.POST["qualification"]
        min_salary = request.POST["min salary"]
        max_salary = request.POST["max salary"]
        rate = request.POST["rate"]
        location = request.POST["location"]

        job = Job.objects.create(
            profile=profile.id, title=title, description=description,
            min_salary=min_salary, max_salary=max_salary, freq=rate, location=location)

        qs = qualification.split(',')
        for q in qs:
            Qualification(job_id=job.id, name=q).save()

        return HttpResponseRedirect(f"/jobs/{job.code}")

    return render(request, 'employer/new-job.html', {
        'name': profile.name,
    })
