from source.handlers.abs_handlers.Message import Message
from source.handlers.abs_handlers.Callback import Callback


from pyrogram.types.messages_and_media.message import Message as MessagePyrogram

class Common(Message, Callback): pass