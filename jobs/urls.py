from django.urls import path
from . import views

urlpatterns = [
    path("", views.view_jobs, name="view_jobs"),
    path("search/", views.search_job, name="search_job"),
    path("<uuid:code>/", views.view_job, name="view_job"),
    path("apply/<uuid:code>/", views.apply_job, name="apply_job"),
    path("resume/<str:code>/", views.view_resume, name="view_resume"),
]
