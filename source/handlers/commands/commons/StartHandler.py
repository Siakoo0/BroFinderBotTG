from source.handlers.abs_handlers.Common import Common

from pyrogram import filters

from source.enums.User import UserRole, UserStatus
from source.models.User import User
from source.models.Chat import Chat

from pyrogram.types.messages_and_media.message import Message as Msg

from datetime import datetime


class StartHandler(Common):

    def filters(self):
        return filters.regex("/start")

    async def action(self):
        user : User = self.user()
        
        user.status = UserStatus.NORMAL.value
        user.save()
        
        keyboard = [
            [
                {"text" : "🔎 Ricerca prodotto", "callback_data" : "product"}
            ],
            [
                {"text" : "ℹ️ Informazioni", "callback_data" : "info"}
            ]
        ]
        
        chat = Chat.get_or_none(Chat.sender == user.id)
        if chat is not None:
            chat.closed_date = datetime.now()
            chat.save()
        

        if user.role == UserRole.ADMIN.value:
            keyboard.insert(1, [{"text" : "⚙️ Amministrazione Bot", "callback_data" : "adm_settings"}])
        else:
            keyboard.insert(1, [{"text" : "💬 Contatta amministratore", "callback_data" : "chat"}])
            
        user_name = self.update.from_user.first_name
        text = f"""👤 Ciao {user_name} e benvenuto in BroFinder!

🤖 Sono un bot utente progettato per aiutarti a esplorare e scoprire prodotti interessanti. Il mio obiettivo è fornirti informazioni dettagliate sui vari prodotti disponibili e aiutarti nella ricerca di ciò che desideri.

🎉 Buona esplorazione dei prodotti e buoni acquisti!"""
        await self.send(text=text, reply_markup=keyboard)