from source.handlers.abs_handlers.BaseHandler import BaseHandler
from pyrogram.handlers.callback_query_handler import CallbackQueryHandler

class Callback(BaseHandler, CallbackQueryHandler): pass