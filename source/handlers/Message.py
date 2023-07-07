from typing import Callable
from pyrogram.handlers.message_handler import MessageHandler
from source.handlers.BaseHandler import BaseHandler
 
from abc import ABCMeta, abstractmethod
 
class Message(BaseHandler, MessageHandler, metaclass=ABCMeta): 

    def __init__(self):
        super().__init__()