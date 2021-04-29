from employer.models import Job
from jobs.models import Application
from django.shortcuts import render
from .models import ChatMessage, Profile
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test

import requests
import json

# Create your views here.


def base64_encode(message):
    import base64
    message_bytes = message.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('ascii')
    return base64_message


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
    code = request.GET["code"]
    data = requests.post(
        f"https://zoom.us/oauth/token?grant_type=authorization_code&code={code}&redirect_uri=http://127.0.0.1:8000/zoom/callback/", headers={
            "Authorization": "Basic" + base64_encode("26iWoBzaQwqVWKgEFifiGw:L5en759Rdz64uEpxn3P8wAOeXCN4BhQk")
        })
    request.session["zoom_access_token"] = data.json()["access_token"]
    return HttpResponse("You successfully login in zoom. now you can schedule metting go to <a href='/'>Dashboard</a>")


def dashboard(request):
    applications = Application.objects.filter(applicant_id=request.user.id)
    applied = []
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
