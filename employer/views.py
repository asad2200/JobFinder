from jobs.models import Application
from django.shortcuts import render
from django.http import HttpResponseRedirect

from dashboard.models import Profile, ChatMessage
from .models import Job, Qualification

# Create your views here.


def index(request):
    unread_response = []
    profile = Profile.objects.get(user_id=request.user.id)
    jobs = Job.objects.filter(profile=profile.id).order_by("-id")
    status = {
        0: 'waiting',
        1: 'viewed',
        2: 'accepted',
        3: 'rejected',
    }
    for job in jobs:
        applications = Application.objects.filter(
            status__in=[0, 1], job_id=job.id)
        for application in applications:
            name = Profile.objects.get(user_id=application.applicant_id).name
            email = request.user.email
            unread_response.append(
                [f"{name}({email}) appliad to {job.title} on {application.timestamp}", application.id, status[application.status]])
    return render(request, "employer/index.html", {
        'unread_response': unread_response,
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

        return HttpResponseRedirect("/employer/jobs/")

    return render(request, 'employer/new-job.html', {
        'name': profile.name,
    })


def view_all_jobs(request):
    profile = Profile.objects.get(user_id=request.user.id)
    jobs = Job.objects.filter(profile=profile.id).order_by("-id")

    return render(request, "employer/alljobs.html", {
        'jobs': jobs,
    })


def view_all_application(request):
    response = []
    profile = Profile.objects.get(user_id=request.user.id)
    jobs = Job.objects.filter(profile=profile.id).order_by("-id")
    status = {
        0: 'waiting',
        1: 'viewed',
        2: 'accepted',
        3: 'rejected',
    }
    for job in jobs:
        applications = Application.objects.filter(job_id=job.id)
        for application in applications:
            name = Profile.objects.get(user_id=application.applicant_id).name
            email = request.user.email
            response.append(
                [f"{name}({email}) appliad to {job.title} on {application.timestamp}", application.id, status[application.status]])
    return render(request, "employer/allapplication.html", {
        'response': response,
    })


def view_application(request, id):
    application = Application.objects.get(id=id)
    job = Job.objects.get(id=application.job_id)
    profile = Profile.objects.get(user_id=application.applicant_id)
    application.status = 1
    application.save()
    return render(request, "employer/application.html", {
        'profile': profile,
        'job': job,
        'application': application,
    })


def chat_with_candidate(request, application_id):
    application = Application.objects.get(id=application_id)

    if request.method == 'POST':
        message = request.POST['message']
        from_id = request.user.id
        to_id = application.id
        ChatMessage(from_id=from_id, to_id=to_id, message=message,
                    application_id=application_id).save()

        return HttpResponseRedirect(f"/employer/chat/{application_id}/")
    else:
        messages = ChatMessage.objects.filter(application_id=application_id)
        job = Job.objects.get(id=application.job_id)
        profile = Profile.objects.get(user_id=application.applicant_id)
        return render(request, "employer/chat.html", {
            'messages': messages,
            'application': application,
            'job': job,
            'profile': profile,
        })


def schedule_interview(request, application_id):
    if request.method == 'POST':
        time = request.POST["time"]
        pass
    else:
        app = Application.objects.get(id=application_id)
        profile = Profile.objects.get(user_id=app.applicant_id)
        job = Job.objects.get(id=app.job_id)
        print(request.session["zoom_access_token"])
        return render(request, "employer/schedule-interview.html", {
            'profile': profile,
            'job': job,
        })
