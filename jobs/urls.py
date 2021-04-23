from django.urls import path
from . import views

urlpatterns = [
    path("<uuid:code>", views.view_job, name="view_job"),
]
