from pyrogram import filters
from pyrogram.errors.exceptions.bad_request_400 import MessageNotModified
from pyrogram.types import CallbackQuery, Message
from pyrogram.enums.parse_mode import ParseMode

from source.enums.User import UserRole, UserStatus
from source.enums.User import UserStatus

from source.filters.UpdateFilter import regex, update_check
from source.filters.UserFilter import status, role

from source.handlers.abs_handlers.AdminHandler import AdminHandler

from source.models.User import User

class GlobalMessageAdmin(AdminHandler): 
    
    def filters(self):
        phases = [
            UserStatus.GLOBAL_MSG_CONFIRM, 
            UserStatus.GLOBAL_MSG_SEND
        ]
        
        filts = (update_check(Message) & status(UserStatus.GLOBAL_MSG))
        
        for phase in phases:
            filts |= (update_check(Message) & status(phase))
        
        return (
            (
                filts |
                (regex("^global_msg", CallbackQuery))
            )
        ) & (super().filters())

    def phases(self):
        return {
            UserStatus.GLOBAL_MSG: {
                "text": f"🤖 Modalità Inoltro Globale\n\n👉 Inoltrami il messaggio che vuoi inviare a tutti gli utenti, prima di essere inviato verrà richiesta una conferma.",
                "reply_markup" : [
                    [
                        {
                            "text" : "🔙 Torna indietro",
                            "callback_data" : "adm_settings" 
                        }
                    ]
                ],
                "next" : UserStatus.GLOBAL_MSG_CONFIRM,
                "callback" : None 
            },
            UserStatus.GLOBAL_MSG_CONFIRM : {
                "text": f"📣 Il messaggio che vuoi inoltrare a tutti gli utenti è questo, confermi?\n\n🗯 Messaggioㅤ\n\n{self.text()}",
                "reply_markup" : [
                    [
                        {
                            "text" : "✔️ Inoltra messaggio",
                            "callback_data" : "global_msg - {}".format(UserStatus.GLOBAL_MSG_SEND.value) 
                        },
                        {
                            "text" : "✖️ Annulla inoltro",
                            "callback_data" : "adm_settings" 
                        }
                    ]
                ],
                "next" : None,
                "callback" : None,
                "parse_mode" : ParseMode.DISABLED
            },
            UserStatus.GLOBAL_MSG_SEND : {
                "text": f"🤖 Operazione eseguita con successo.\n\n📣 Il messaggio è stato inoltrato a tutti gli utenti, adesso puoi tornare indietro.",
                "reply_markup" : [
                    [
                        {
                            "text" : "🔙 Torna indietro",
                            "callback_data" : "adm_settings" 
                        },
                    ]
                ],
                "next" : UserStatus.GLOBAL_MSG.value,
                "callback" : self.send_global
            }
        }
    
    async def send_global(self, update):
        text = update.message
        
        users = User.select().where(User.role == UserRole.USER.value)

        text="".join(text.text.split("ㅤ")[1:])

        for user in users:
            print(user.id)
            try:
                await self.bot.send_message(
                    chat_id=user.id,
                    text="🌐 <b>Comunicazione di servizio</b>\n\n" + text.strip("\n"),
                    parse_mode=ParseMode.DEFAULT
                )
            except:
                admin : User = self.user()
                admin.status = UserStatus.GLOBAL_MSG
                admin.save()
                
                await text.reply("🤖 Il messaggio non è stato formattato correttamente, si prega di controllare il testo inserito.\n\n👉 Appena finito di controllare, inoltra il nuovo messaggio.")
                break                
    
    async def action(self):
        user : User = self.user()
        
        if self.is_callback_data():
            status = UserStatus(int(self.text().split(" - ")[1]))
        else:
            status = UserStatus(user.status)
        
        phase = self.phases()[status]
            
        if phase["next"] is not None: 
            status = UserStatus(phase["next"])
            
        if phase["callback"] is not None:
            await phase["callback"](self.update)

        user.status = status.value
        user.save()
            
        del phase["callback"]
        del phase["next"]
        
        await self.send(**phase)    
            
        