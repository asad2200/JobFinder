from employer.models import Job
from jobs.models import Application
from django.shortcuts import render
from .models import ChatMessage, Profile
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test

# Create your views here.


@login_required(login_url="/auth/login/")
def index(request):
    # if request.session.get("role") is None:
    try:
        profile = Profile.objects.get(user_id=request.user.id)
        if profile.role == 0:
            return HttpResponseRedirect("/employer/")
    except Profile.DoesNotExist:
        return HttpResponseRedirect("/complete-register/")
    # elif int(request.session.get("role")) == 0:
    #     print("outside")
    #     return HttpResponseRedirect("/employer/")
    return HttpResponse("Welcome To dashboard")


@login_required(login_url="/auth/login/")
def complete_register(request):
    if request.method == 'POST':
        role = int(request.POST["role"])
        name = request.POST["name"]

        Profile(user_id=request.user.id, role=role, name=name).save()

        # request.session["role"] = role
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
