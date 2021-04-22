from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("complete-register/", views.complete_register, name="complete-register"),
]
