# chat/urls.py
from django.urls import path

from . import views

urlpatterns = [
    path("<str:room_name>/", views.room, name="room"),
    path("dock", views.dock, name="dock"),
    path("index", views.index, name="index"),
    path("studioheld", views.studioheld, name="studioheld"),
]
