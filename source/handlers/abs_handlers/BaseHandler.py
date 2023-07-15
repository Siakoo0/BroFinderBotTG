from pyrogram.handlers.handler import Handler
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton 
from pyrogram.types import Message as MessagePyrogram
from pyrogram.types import CallbackQuery
from pyrogram.client import Client

from typing import List
import base64
from json import dumps, loads

from source.enums.User import UserRole, UserStatus
from source.models.User import User


from abc import ABCMeta, abstractmethod

class BaseHandler(Handler, metaclass=ABCMeta):
    async def action(self):
        print(self.bot, self.update)
        
    @abstractmethod
    def filters(self):
        pass
    
    def createKeyboard(self, kbd : List[List[InlineKeyboardButton]]):
        _kbd = []
        
        for rows in kbd:
            row = []
            for button in rows:
                row.append(InlineKeyboardButton(**button))
                
            _kbd.append(row)
        
        return InlineKeyboardMarkup(_kbd)
    
    def user(self):
        update = self.update
        
        user, _ = User.get_or_create(
            id=update.from_user.id,
            defaults={
                "role" : UserRole.USER.value,
                "status" : UserStatus.NORMAL.value
            }
        )

        return user 
    
    async def send(self, **data):
        update = self.update
        
        if "reply_markup" in data.keys() and not isinstance(data["reply_markup"], InlineKeyboardMarkup):
            data["reply_markup"] = self.createKeyboard(data["reply_markup"])
        
        if isinstance(update, MessagePyrogram):
            return await update.reply(**data)
        else:
            return await update.edit_message_text(**data)
           
    def text(self):
        return self.update.text if  self.is_message() else self.update.data
     
    def is_callback_data(self):
        return isinstance(self.update, CallbackQuery)
     
    def is_message(self):
         return isinstance(self.update, MessagePyrogram)
    
    async def guard(self, bot, update):
        self.update = update
        self.bot = bot 
        
        user = self.user()
        
        if user.role != UserRole.BANNED.value: 
            await self.action()
        else: 
            await self.send(
                **{
                    "text" : "🤖 Sei attualmente stato bannato dal bot, quindi non potrai interagire con il bot."
                }
            )
            
    def __init__(self):
        self.bot : Client = None

        super().__init__(self.guard, self.filters())