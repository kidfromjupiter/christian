# chat/urls.py
from django.urls import path,re_path
from . import views

urlpatterns = [
    re_path(r"^dock(?P<parameters>.*)$", views.dock, name="dock"),
    re_path(r"^index(?P<parameters>.*)$", views.index, name="index"),
    re_path(r"^studioheld(?P<parameters>.*)$", views.studioheld, name="studioheld"),
]
