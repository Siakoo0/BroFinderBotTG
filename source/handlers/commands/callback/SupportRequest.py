# supp_req
from source.handlers.abs_handlers.Callback import Callback

from source.models.User import User
from source.enums.User import UserStatus
from source.models.Chat import Chat

from source.filters.UpdateFilter import  regex

from pyrogram.types import CallbackQuery

grouper = lambda lista, n : [lista[i:i+n] for i in range(0, len(lista), n)]

class SupportRequest(Callback): 
    def filters(self):
        return regex("^supp_req", CallbackQuery)

    async def action(self):
        model_chats = Chat.select().where(
            (Chat.closed_date.is_null()) 
            & 
            (Chat.receiver.is_null())
        ).execute()

        group_chats = list(model_chats)
        group_chats = list(grouper(group_chats, 6))

        data = self.text().split(" - ")
        page = 0 if len(data) == 1 else int(data[1])

        chats = group_chats[page] if len(group_chats) > 0 and page < len(group_chats)  else []


        kbd = [
            [{"text" : "🔄 Aggiorna", "callback_data" : f"supp_req - {page}"}],
        ]

        kbd += [
            [
                {
                    "text" : f"Chat {chat.id} con {chat.sender.id}",
                    "callback_data" : f"chat - {chat.id}"
                }
            ] for chat in chats
        ]

        next_page = {
            "text" : "Pagina successiva 🔜", "callback_data" : f"supp_req - {page+1}"
        }

        control_ui = []

        if (page+1) < len(group_chats): control_ui.append(next_page)

        if page > 0:
            bck_page = {
                "text" : "🔙 Pagina precedente", "callback_data" : f"supp_req - {page-1}"
            }
        else:
            bck_page = {
                "text" : "🔙 Menu principale", "callback_data" : f"adm_settings"
            }
            

        kbd.append(control_ui)
        
        control_ui.insert(0, bck_page)

        text = "🔎 Benvenuto nella modalità chat\n\n👉 Qui potrai selezionare tutte le chat aperte!"
        
        try:
            await self.send(text=text, reply_markup=kbd)
        except: pass