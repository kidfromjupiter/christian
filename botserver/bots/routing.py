# chat/routing.py
from django.urls import re_path
from bots import consumers

websocket_urlpatterns = [
    re_path(r"ws/bots/(?P<user_id>\w+)/$", consumers.ChatConsumer.as_asgi()),
]
