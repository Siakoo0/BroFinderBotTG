from pyrogram import filters
from pyrogram.errors.exceptions.bad_request_400 import MessageNotModified

from source.enums.User import UserStatus

from source.handlers.abs_handlers.Callback import Callback

class AdministratorPanel(Callback): 
    def filters(self):
        return filters.regex("^adm_settings$")

    async def action(self):
        user = self.user()
        
        if user.status != UserStatus.NORMAL.value:
            user.status = UserStatus.NORMAL.value
            user.save()
        
        kbd = [
            [
                {"text" : "👤 Gestione utenti", "callback_data" : "users_mng - page - 0"}
            ],
            [
                {"text" : "💬 Richieste di supporto", "callback_data" : "supp_req"}
            ],
            [
                {"text" : "🌐 Messaggio globale", "callback_data" : "global_msg - 4"}
            ],
            [
                {"text" : "🔙 Torna indietro", "callback_data" : "/start"}
            ]
        ]
        
        await self.send(
            text="🤖 Pannello di amministrazione\n\n👉 In questa sezione potrai eseguire operazioni consentite solo agli amministratori.",
            reply_markup=kbd
        )