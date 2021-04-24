from django.urls import path
from . import views

urlpatterns = [
    path("<uuid:code>/", views.view_job, name="view_job"),
    path("apply/<uuid:code>/", views.apply_job, name="apply_job"),
    path("resume/<str:code>/", views.view_resume, name="view_resume"),
]
