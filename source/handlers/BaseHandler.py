from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton 

from typing import List 

from abc import ABCMeta, abstractproperty, abstractmethod

class BaseHandler(metaclass=ABCMeta):
    def createKeyboard(self, kbd : List[List[InlineKeyboardButton]]):
        _kbd = []
        
        for rows in kbd:
            row = []
            for button in rows:
                row.append(InlineKeyboardButton(**button))
                
            _kbd.append(row)
        
        return InlineKeyboardMarkup(_kbd)
    
    @abstractmethod
    def filters(self):
        pass
    
    @abstractmethod
    async def execute(self, bot, message):
        pass
    
    
    
    def __init__(self):
        super().__init__(self.execute, self.filters())
    