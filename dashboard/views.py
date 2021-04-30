from helpers import base64_encode
from employer.models import Job
from jobs.models import Application
from django.shortcuts import render
from .models import ChatMessage, Profile
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from credentials import ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET
from decorators import checkrole
import requests

# Create your views here.


@login_required(login_url="/auth/login/")
def index(request):
    try:
        profile = Profile.objects.get(user_id=request.user.id)
        if profile.role == 0:
            return HttpResponseRedirect("/employer/")
        if profile.role == 1:
            return HttpResponseRedirect("/dashboard/")
    except Profile.DoesNotExist:
        return HttpResponseRedirect("/complete-register/")


@login_required(login_url="/auth/login/")
def complete_register(request):
    if request.method == 'POST':
        role = int(request.POST["role"])
        name = request.POST["name"]

        Profile(user_id=request.user.id, role=role, name=name).save()

        return HttpResponseRedirect('/')

    return render(request, "dashboard/complete-register.html")


@login_required(login_url="/auth/login/")
@checkrole(1)
def chat_with_employer(request, application_id):
    application = Application.objects.get(id=application_id)

    if request.method == 'POST':
        message = request.POST['message']
        from_id = request.user.id
        to_id = application.id
        ChatMessage(from_id=from_id, to_id=to_id, message=message,
                    application_id=application_id).save()

        return HttpResponseRedirect(f"/chat/{application_id}/")
    else:
        messages = ChatMessage.objects.filter(application_id=application_id)
        job = Job.objects.get(id=application.job_id)
        profile = Profile.objects.get(id=job.profile)
        return render(request, "dashboard/chat.html", {
            'messages': messages,
            'application': application,
            'job': job,
            'profile': profile,
        })


def zoom_callback(request):
    code = request.GET.get("code")
    data = requests.post(
        f"https://zoom.us/oauth/token?grant_type=authorization_code&code={code}&redirect_uri=http://127.0.0.1:8000/zoom/callback/", headers={
            "Authorization": "Basic" + base64_encode(f"{ZOOM_CLIENT_ID}:{ZOOM_CLIENT_SECRET}")
        })
    profile = Profile.objects.get(user_id=request.user.id)
    profile.zoom_auth_token = data.json()["access_token"]
    profile.zoom_refresh_token = data.json()["refresh_token"]
    profile.save()
    return HttpResponseRedirect(f"/employer/schedule-interview/{request.session['applicaion_id']}/")
    # return HttpResponse("You successfully login in zoom. now you can schedule metting go to <a href='/'>Dashboard</a>")


@login_required(login_url="/auth/login/")
@checkrole(1)
def dashboard(request):
    status = request.GET.get("status")
    applied = []

    if status != None and status != -1:
        applications = Application.objects.filter(
            applicant_id=request.user.id, status=status)
        status = {
            0: 'waiting',
            1: 'viewed',
            2: 'accepted',
            3: 'rejected',
        }
        for application in applications:
            job = Job.objects.get(id=application.job_id)
            applied.append([application, job, status[application.status]])
    return render(request, "dashboard/index.html", {
        'applications': applied,
    })
