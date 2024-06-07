# chat/views.py
from django.shortcuts import render


def start_bot(request):
    return render(request, "botroom/index.html")


def room(request, room_name):
    return render(request, "botroom/room.html", {"room_name": room_name})

def dock(request,):
    return render(request, "botroom/dock_original.html")

def index(request):
    return render(request, "botroom/index_original.html")
    
def studioheld(request):
    return render(request, "botroom/studioheld.html")