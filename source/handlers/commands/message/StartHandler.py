from source.handlers.Message import Message

from pyrogram import filters

from source.enums.User import UserRole, UserStatus
from source.models.User import User


class StartHandler(Message):

    def filters(self):
        return filters.command("start") & filters.private

    async def execute(self, bot, message):
        user, created = User.get_or_create(
            id=message.from_user.id,
            defaults={
                "role" : UserRole.USER.value,
                "status" : UserStatus.NORMAL.value
            }
        )
        
        keyboad = [
            [
                {"text" : "🔎 Ricerca prodotto", "callback_data" : "product"}
            ],
            [
                {"text" : "📣 Gestione canali", "callback_data" : "channels"}
            ],
            [
                {"text" : "💬 Contatta amministratore", "callback_data" : "administrator"}
            ],
            [
                {"text" : "ℹ️ Informazioni", "callback_data" : "info"}
            ]
        ]
        
        if user.role == UserRole.ADMIN.value:
            keyboad.append([{"text" : "⚙️ Amministrazione Bot", "callback_data" : "adm_settings"}])

        user_name = message.from_user.first_name
        await message.reply(
            text=f"Benvenuto {user_name} in questo bellissimo bot!!",
            quote=True,
            reply_markup=self.createKeyboard(keyboad)
        )