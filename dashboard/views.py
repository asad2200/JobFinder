from django.shortcuts import render
from .models import Profile
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test

# Create your views here.


@login_required(login_url="/auth/login/")
def index(request):
    if request.session.get("role") is None:
        try:
            Profile.objects.get(user_id=request.user.id)
        except Profile.DoesNotExist:
            return HttpResponseRedirect("/complete-register/")
    elif int(request.session.get("role")) == 0:
        return HttpResponseRedirect("/employer/")
    return HttpResponse("Welcome To dashboard")


@login_required(login_url="/auth/login/")
def complete_register(request):
    if request.method == 'POST':
        role = int(request.POST["role"])
        name = request.POST["name"]

        Profile(user_id=request.user.id, role=role, name=name).save()

        request.session["role"] = role
        return HttpResponseRedirect('/')

    return render(request, "dashboard/complete-register.html")
