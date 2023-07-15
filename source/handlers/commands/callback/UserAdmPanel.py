from pyrogram import filters
from pyrogram.errors.exceptions.bad_request_400 import MessageNotModified

from source.enums.User import UserStatus, UserRole
from source.handlers.abs_handlers.Callback import Callback
from source.models.User import User

from source.api.SearchApi import SearchApiHelper


grouper = lambda lista, n : [lista[i:i+n] for i in range(0, len(lista), n)]

class UserAdmPanel(Callback): 
    def filters(self):
        return filters.regex("^users_mng") 

    async def menu(self):
        page = int(self.text().split(" - ")[2])
        
        admin = self.user()
        
        if admin.status != UserStatus.NORMAL.value:
            admin.status = UserStatus.NORMAL.value
            admin.save()
        
        kbd = []
        users_models = list(User.select().where(User.id != admin.id & User.id))

        users = list(grouper(users_models, 5))
        
        for user in users[page]: 
            user_bot = await self.bot.get_chat(user.id)
            
            kbd.append(
                [
                    {
                        "text" : f"{user_bot.first_name} [{user.id}] - {UserRole(user.role).name.capitalize()}",
                        "callback_data" : f"users_mng - {user.id} - {page}"
                    }
                ]
            )
            
        control_ui = []
        
        bck_panel_btn = {"text" : "🔙 Torna indietro", "callback_data" : "adm_settings"}
        
        if page > 0:
            bck_btn = {"text" : "🔙 Pagina precedente", "callback_data" : "users_mng - page - {}".format(page-1)}
        else:
            bck_btn = bck_panel_btn
            
        control_ui.append(bck_btn)
        
        if (page+1) < len(users):
            forward_btn = {"text" : "🔜 Prossima pagina", "callback_data" : "users_mng - page - {}".format(page+1)}
            
            control_ui.append(forward_btn)

        kbd.append(control_ui)
        
        await self.send(
            text="🤖 Pannello di gestione utente\n\n👉 Seleziona un'utente per cambiarne il ruolo.",
            reply_markup=kbd
        )

    async def get_user(self, text):
        user_id  = int(text[1])
        page = int(text[2])
        
        user : User = User.get(User.id == user_id)
        user_chat = await self.bot.get_chat(user.id)
        
        if len(text) > 3:
            role = text[3]
            user.role = int(role)
            user.save()
            
        next_role = UserRole.USER.value if user.role == UserRole.ADMIN.value else UserRole.ADMIN.value
        to_ban = UserRole.BANNED.value if user.role != UserRole.BANNED.value else UserRole.USER.value
        
        kbd = [
            [
                {
                    "text" : f"🚫 Disattiva utente" if user.role != UserRole.BANNED.value else "📛 Attiva utente",
                    "callback_data" : f"users_mng - {user.id} - {page} - {to_ban}"
                }
            ],
            [
                {
                    "text" : "🔙 Torna indietro", 
                    "callback_data" : "users_mng - page - {}".format(page)
                }
            ]
        ]
        
        if user.role != UserRole.BANNED.value:
            kbd.insert(
                0, 
                [
                    {
                        "text" : f"🌟 Ruolo {UserRole(user.role).name.capitalize()}",
                        "callback_data" : f"users_mng - {user.id} - {page} - {next_role}"
                    }
                ]
            )
        
        user_str = ""
        
        if user_chat.first_name is not None:
            user_str += user_chat.first_name + " "
        
        if user_chat.last_name is not None:
            user_str += user_chat.last_name + " "
        
        if user_chat.username is not None:
            user_str += f"[ @{user_chat.username} ]"
            
        user_str = user_str.strip()
        helper = SearchApiHelper()
        
        resp = await helper.get({"user": user.id})
        
        await self.send(
            text=f"🤖 Pannello gestione utente.\n\n👤 Utente: {user_str}\n\n🆔 {user.id}\n⭐️ <b>Ruolo:</b> {UserRole(user.role).name.capitalize()}\n\n🔎 Ricerche effettuate: {len(resp)}",
            reply_markup=kbd
        )

    async def action(self):
        text = self.text().split(" - ")
        
        if len(text) > 1 and text[1] != "page": 
            await self.get_user(text)
        else:
            await self.menu()