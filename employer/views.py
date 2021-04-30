from django.http.response import HttpResponse
from jobs.models import Application
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from credentials import ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET
from decorators import checkrole
from dashboard.models import Profile, ChatMessage
from .models import Job, Qualification
from helpers import base64_encode
import requests
import json

# Create your views here.


@login_required(login_url='/auth/login')
@checkrole(0)
def index(request):
    unread_response = []
    profile = Profile.objects.get(user_id=request.user.id)
    jobs = Job.objects.filter(profile=profile.id).order_by("-id")
    status = {
        0: "waiting",
        1: "viewed",
        2: "accepted",
        3: "rejected",
    }
    if request.GET.get("job") != "Select Job" and request.GET.get("job") != None:
        job = Job.objects.get(title=request.GET.get("job"))
        applications = Application.objects.filter(
            status__in=[0, 1], job_id=job.id)
        for application in applications:
            name = Profile.objects.get(user_id=application.applicant_id).name
            email = User.objects.get(id=application.applicant_id).email
            unread_response.append(
                [
                    f"{name}({email}) appliad to {job.title} on {application.timestamp}",
                    application.id,
                    status[application.status],
                ]
            )
    return render(
        request,
        "employer/index.html",
        {
            "unread_response": unread_response,
            "jobs": jobs,
        },
    )


@login_required(login_url='/auth/login')
@checkrole(0)
def post_job(request):
    profile = Profile.objects.get(user_id=request.user.id)

    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["decription"]
        qualification = request.POST["qualification"]
        min_salary = request.POST["min salary"]
        max_salary = request.POST["max salary"]
        rate = request.POST["rate"]
        location = request.POST["location"]

        job = Job.objects.create(
            profile=profile.id,
            title=title,
            description=description,
            min_salary=min_salary,
            max_salary=max_salary,
            freq=rate,
            location=location,
        )

        qs = qualification.split(",")
        for q in qs:
            Qualification(job_id=job.id, name=q).save()

        return HttpResponseRedirect("/employer/jobs/")

    return render(
        request,
        "employer/new-job.html",
        {
            "name": profile.name,
        },
    )


@login_required(login_url='/auth/login')
@checkrole(0)
def view_all_jobs(request):
    profile = Profile.objects.get(user_id=request.user.id)
    jobs = Job.objects.filter(profile=profile.id).order_by("-id")

    return render(
        request,
        "employer/alljobs.html",
        {
            "jobs": jobs,
        },
    )


@login_required(login_url='/auth/login')
@checkrole(0)
def view_all_application(request):
    response = []
    profile = Profile.objects.get(user_id=request.user.id)
    jobs = Job.objects.filter(profile=profile.id).order_by("-id")
    status = {
        0: "waiting",
        1: "viewed",
        2: "accepted",
        3: "rejected",
    }
    if request.GET.get("job") != "Select Job" and request.GET.get("job") != None:
        job = Job.objects.get(title=request.GET.get("job"))
        applications = Application.objects.filter(job_id=job.id)
        for application in applications:
            name = Profile.objects.get(user_id=application.applicant_id).name
            email = User.objects.get(id=application.applicant_id).email
            response.append(
                [
                    f"{name}({email}) appliad to {job.title} on {application.timestamp}",
                    application.id,
                    status[application.status],
                ]
            )
    return render(
        request,
        "employer/allapplication.html",
        {
            "response": response,
            "jobs": jobs,
        },
    )


@login_required(login_url='/auth/login')
@checkrole(0)
def view_application(request, id):
    application = Application.objects.get(id=id)
    job = Job.objects.get(id=application.job_id)
    profile = Profile.objects.get(user_id=application.applicant_id)
    application.status = 1
    application.save()
    return render(
        request,
        "employer/application.html",
        {
            "profile": profile,
            "job": job,
            "application": application,
        },
    )


@login_required(login_url='/auth/login')
@checkrole(0)
def chat_with_candidate(request, application_id):
    application = Application.objects.get(id=application_id)

    if request.method == "POST":
        message = request.POST["message"]
        from_id = request.user.id
        to_id = application.id
        ChatMessage(
            from_id=from_id, to_id=to_id, message=message, application_id=application_id
        ).save()

        return HttpResponseRedirect(f"/employer/chat/{application_id}/")
    else:
        messages = ChatMessage.objects.filter(application_id=application_id)
        job = Job.objects.get(id=application.job_id)
        profile = Profile.objects.get(user_id=application.applicant_id)
        return render(
            request,
            "employer/chat.html",
            {
                "messages": messages,
                "application": application,
                "job": job,
                "profile": profile,
            },
        )


def schedule_interview(request, application_id):
    app = Application.objects.get(id=application_id)
    candidate = Profile.objects.get(user_id=app.applicant_id)
    job = Job.objects.get(id=app.job_id)
    profile = Profile.objects.get(user_id=request.user.id)
    if profile.zoom_auth_token == '':
        request.session['applicaion_id'] = application_id
        return HttpResponseRedirect(f'https://zoom.us/oauth/authorize?response_type=code&client_id={ZOOM_CLIENT_ID}&redirect_uri=http%3A%2F%2F127.0.0.1%3A8000%2Fzoom%2Fcallback/')

    if request.method == "POST":
        time = request.POST["time"]
        data = ''
        try:
            data = requests.post("https://api.zoom.us/v2/users/me/meetings", headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer' + profile.zoom_auth_token
            }, data=json.dumps({
                "topic": f"Interview with {profile.name}",
                "start_time": time,
                "duration": 45,
                "type": 2
            }))
            if data.json()['start_url']:
                pass
        except:
            print('a', data.json())
            if data.json()['message'] == 'Invalid access token.':
                request.session['applicaion_id'] = application_id
                return HttpResponseRedirect(f'https://zoom.us/oauth/authorize?response_type=code&client_id={ZOOM_CLIENT_ID}&redirect_uri=http%3A%2F%2F127.0.0.1%3A8000%2Fzoom%2Fcallback/')
            if data.json()["message"] == 'Access token is expired.':
                data = requests.post(
                    f"https://zoom.us/oauth/token?grant_type=refresh_token&refresh_token={profile.zoom_refresh_token}", headers={
                        "Authorization": "Basic" + base64_encode(f"{ZOOM_CLIENT_ID}:{ZOOM_CLIENT_SECRET}")
                    })
                profile.zoom_auth_token = data.json()["access_token"]
                profile.zoom_refresh_token = data.json()["refresh_token"]
                data = requests.post("https://api.zoom.us/v2/users/me/meetings", headers={
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer' + profile.zoom_auth_token
                }, data=json.dumps({
                    "topic": f"Interview with {profile.name}",
                    "start_time": time,
                    "duration": 45,
                    "type": 2
                }))
        ChatMessage(from_id=request.user.id, to_id=candidate.id, application_id=application_id,
                    message=f"Your Interview is schedule on {data.json()['start_time']}. <a href='{data.json()['join_url']}'>Join ZOOM MEETING</a>. Good luck!!").save()
        ChatMessage(from_id=request.user.id, to_id=candidate.id, application_id=application_id,
                    message=f"(only viewable for you) Start the metting on {data.json()['start_time']}. <a href='{data.json()['start_url']}'>Start ZOOM MEETING</a>. both links valid for 90 days", public=False).save()
        return HttpResponseRedirect(f"/employer/chat/{application_id}")
    else:

        return render(
            request,
            "employer/schedule-interview.html",
            {
                "candidate": candidate,
                "job": job,
            },
        )


@login_required(login_url='/auth/login')
@checkrole(0)
def reject_candidate(request, id):
    app = Application.objects.get(id=id)
    app.status = 3
    app.save()
    return HttpResponse(
        "<div class='alert alert-success' role='alert'>Candidate Rejected Successfully !! <a href='/employer/'> Go to dashboard </a></div>"
    )


@login_required(login_url='/auth/login')
@checkrole(0)
def hire_candidate(request, id):
    app = Application.objects.get(id=id)
    app.status = 2
    app.save()
    return HttpResponse(
        "<div class='alert alert-success' role='alert'>Candidate Hired Successfully !!<a href='/employer/'> Go to dashboard </a></div>"
    )
