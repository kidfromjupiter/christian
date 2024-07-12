import datetime
import json
from asgiref.sync import async_to_sync

class Message():
    def __init__(self,type:str,name:str,message:str,chatimg:str,contentid:str) -> None:
        self.chatname = name
        self.chatbadges = ""
        self.backgroundColor = ""
        self.textColor = ""
        self.chatmessage = message
        self.chatimg = chatimg
        self.hasDonation = ""
        self.membership = ""
        self.contentimg = ""
        self.type = type
        self.contentId = contentid

    def stringify(self):
        dict_copy = self.__dict__.copy()
        dict_copy.pop('contentId', None)

        return json.dumps(dict_copy)
    
    def __eq__(self, other) -> bool:
        return  self.contentId == other.contentId
    
def send_message(userid:str, message:str,channel_layer):
    async_to_sync(channel_layer.group_send)(userid,{"type":"chat.message","message":message})   

def send_message_base(userid:str, message:str,channel_layer,type:str):
    async_to_sync(channel_layer.group_send)(userid,{"type":type,"message":message}) 

def send_status(userid:str, status:str,channel_layer):
    async_to_sync(channel_layer.group_send)(userid,{"type":"bot.status","status":status})
