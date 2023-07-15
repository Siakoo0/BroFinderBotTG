from source.handlers.abs_handlers.BaseHandler import BaseHandler

from pyrogram.handlers.message_handler import MessageHandler

class Message(BaseHandler, MessageHandler): pass