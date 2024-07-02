# chat/views.py
from django.shortcuts import render


def room(request, room_name):
    return render(request, "botroom/room.html", {"room_name": room_name})

def dock(request,*args,**kwargs):
    return render(request, "botroom/dock_original.html")

def index(request,*args,**kwargs):
    return render(request, "botroom/index_original.html")
    
def studioheld(request,*args,**kwargs):
    return render(request, "botroom/studioheld.html")
