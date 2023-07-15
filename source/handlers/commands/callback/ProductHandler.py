from source.handlers.abs_handlers.Callback import Callback

from source.models.User import User
from source.enums.User import UserStatus

from source.filters.UpdateFilter import  regex

from pyrogram.types import CallbackQuery

class ProductHandler(Callback): 
    
    def filters(self):
        return regex("^product$", CallbackQuery)

    async def action(self):
        kbd = [
            [{"text" : "🔙 Torna indietro", "callback_data" : "/start"}]
        ]
        
        text = "🔎 Modalità ricerca prodotto\n\n👉 Benvenuto nella <b>modalità ricerca</b>, scrivi nella chat il prodotto che cerchi e il bot lo cercherà per te su diversi siti contemporaneamente!"
        
        user : User = self.user()
        user.status = UserStatus.SEARCH.value
        user.save()
        
        await self.send(text=text, reply_markup=kbd)