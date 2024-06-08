import json
from channels.generic.websocket import AsyncWebsocketConsumer
from multiprocessing import Process,Queue
from bots.bots_helper.teamsbot import run_teamsbot
from bots.bots_helper.zoombot import run_zoombot
from bots.bots_helper.teamsbot_v2 import run_teamsbot as run_teamsbot_v2
import psutil

def killtree(pid, including_parent=True):
    parent = psutil.Process(pid)
    for child in parent.children(recursive=True):
        child.kill()

    if including_parent:
        parent.kill()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope["url_route"]["kwargs"]["user_id"]
        self.room_group_name = f"{self.user_id}"
        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        self.filtered = ""
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json:dict = json.loads(text_data)
        if "message" in text_data_json.keys():
            message = json.loads(text_data_json["message"])
            command:str = ""
            if message["chatmessage"][0] == "!" and self.q != None:
                command = message["chatmessage"][1:]
                # removes ! and puts in into the queue
                self.q.put(command.rstrip())
        # force kill the bot
        if text_data_json['type'] == 'bot.kill' and hasattr(self,"botprocess") :
            if self.botprocess != None and self.botprocess.is_alive():
                killtree(self.botprocess.pid)
                await self.channel_layer.group_send(
                    self.room_group_name, {"type":"bot.status","status":"Bot killed forcefully"}
                )
            return
        # Send message to room group
        if text_data_json["type"] == "bot.start":
            self.q = Queue()
            url = text_data_json["url"]
            bot_timeout = int(text_data_json["timeout"] if text_data_json["timeout"] != "" else 0) #timeout in number of hours
            if hasattr(self, 'botprocess'):
                if self.botprocess != None and self.botprocess.is_alive():
                    killtree(self.botprocess.pid)
                    self.botprocess = None
            if "teams.live.com"in url or "teams.microsoft.com" in url:
                if "meetup-join" in url:
                    self.botprocess = Process(target=run_teamsbot_v2, args=(url,self.user_id,bot_timeout if bot_timeout > 0 else 12,self.q))
                    self.botprocess.start()
                else:
                    self.botprocess = Process(target=run_teamsbot, args=(url,self.user_id,bot_timeout if bot_timeout > 0 else 12,self.q))
                    self.botprocess.start()
            if "zoom.us" in url:
                self.botprocess = Process(target=run_zoombot, args=(url,self.user_id,bot_timeout if bot_timeout > 0 else 12,self.q))
                self.botprocess.start()
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "bot.status", "status": "Bot process launched"}
            )
            return

        await self.channel_layer.group_send(
            self.room_group_name, text_data_json
        )

    # async def 
    # Receive message from room group
    async def filtered_name(self, event):
        self.filtered = event['name']

    async def chat_message(self, event):
        message = json.loads(event["message"])
        message['filtered_name']  = self.filtered
        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": json.dumps(message)}))

    async def bot_status(self,event):
        await self.send(text_data=json.dumps(event))
