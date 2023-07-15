from pyrogram import filters
from pyrogram.types import Message


def update_check(type):
    async def update_test(param, __, update):
        return bool(isinstance(update, param.type))
        
    return filters.create(update_test, type=type)

def regex(regex, type=Message):
    return  update_check(type) & filters.regex(regex)