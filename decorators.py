from dashboard.models import Profile
from django.http import HttpResponse


def checkrole(role):
    def inner(func):
        def wrapper(*args, **kwargs):
            profile_role = Profile.objects.get(user_id=args[0].user.id).role
            if profile_role != role:
                return HttpResponse("You are not authorized for this page <a href='/'> Go to homepage </a>")
            return func(*args, **kwargs)
        return wrapper
    return inner
