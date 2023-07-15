from pyrogram.types import CallbackQuery, Message
from pyrogram import filters

from source.handlers.abs_handlers.Common import Common
from source.enums.User import UserStatus, UserRole

from source.filters.UpdateFilter import regex, update_check
from source.filters.UserFilter import status

from source.models.User import User
from source.models.Chat import Chat

from datetime import datetime

import re

class ChatHandler(Common):

    def filters(self):
        return regex("^chat", CallbackQuery) | (update_check(Message) & status(UserStatus.CHAT))

    async def handle_chat(self):
        kbd = [
            [{"text" : "✖️ Termina chat", "callback_data" : "chat - op - CLOSE"}]
        ]   

        user : User = self.user()

        chat : Chat = Chat.get_or_none(
            ((Chat.sender == user.id) | (Chat.receiver == user.id)) 
            & 
            (Chat.closed_date.is_null()))

        if chat is None: 
            await self.send(
                text="La chat non esiste, è già stata chiusa.", 
                reply_markup=[
                    [
                        {"text" : "Torna indietro", "callback_data" : "/start"}
                    ]
                ]
            )
            return

        destinatario = chat.receiver if user.role == UserRole.USER.value else chat.sender

        role = ["Utente", "Amministratore"]

        name = " "

        if self.update.from_user.first_name is not None:
            name += self.update.from_user.first_name + " "
        elif self.update.from_user.last_name is not None:
            name += self.update.from_user.last_name
        else: name=""
        name = name.rstrip()

        data = {
            "chat_id" : destinatario.id, 
            "reply_markup" : self.createKeyboard(kbd)
        }

        text = f"⭐️ {role[user.role - 1]}{name}"
        send = True

        try:
            word_list = ["cazzo", "dio", "madonna", "cristo", "negro", "puttana", "frocio"]
            regex_pattern = r"\b(" + "|".join(word_list) + r")\b"
            
            if re.search(regex_pattern, self.text(), re.IGNORECASE):
                await self.update.delete()
                await self.update.reply("❌ Hai utilizzato delle parole bandite. ❌")
                send = False

            self.update.text = text + " ha inviato:\n\n" + self.update.text
        except: 
            data["caption"] = text + " ha inoltrato questo media" + (
                ("\n\n" + self.update.caption) if self.update.caption is not None else "."
            )

        if send: await self.update.copy(**data)

    async def accept(self):
        chat_id = self.text().split(" - ")[1]

        chat = Chat.get_or_none(Chat.id == chat_id)

        if chat is None:
            await self.send(
                text="La chat non esiste, è già stata chiusa.", 
                reply_markup=[
                    [
                        {"text" : "Torna indietro", "callback_data" : "/start"}
                    ]
                ]
            )
            return

        if chat.receiver is None:
            chat.receiver = self.user()
            chat.save()

            admin : User = self.user()
            admin.status = UserStatus.CHAT.value
            admin.save()

            chat.sender.status = UserStatus.CHAT.value
            chat.sender.save()

            await self.bot.send_message(
                chat_id=chat.sender.id,
                text=f"🤖 Sei stato messo in contatto con un amministratore, descrivi il tuo problema."
            )

            await self.send(
                text=f"🤖 La chat è stata avviata, a momenti ti verrà recapitato un messaggio con il problema descritto dall'utente."
            )
        else:
            await self.update.answer(
                text="La richiesta di chat è già stata accettata da un altro amministratore 😝",
            )
            await self.update.message.delete()
            return

    async def send_request(self):
        chat = Chat.get_or_create(
            sender=self.user(),
            closed_date=None
        )

        created = chat[1]
        chat = chat[0]

        if chat.receiver is None:
            text = "🤖 Supporto\n\n⭐️ Gli Amministratori sono stati contattati, riceverai una risposta al più presto."
        else:
            text = "🤖 Supporto\n\n⭐️ Sei già stato messo in contatto con un'amministratore, descrivi il tuo problema affinchè possa risolverlo."

        if created:
            kbd = [
                [
                    {"text" : "✅ Accetta richiesta", "callback_data" : f"chat - {chat.id}"}
                ]
            ]

            users = User.select().where((User.role == UserRole.ADMIN.value) & (User.status == UserStatus.NORMAL.value))
            users = list(users)

            for user in users:
                await self.bot.send_message(
                    chat_id=user.id,
                    text=f"L'utente {self.update.from_user.first_name} sta cercando di contattarti, accetta la richiesta di supporto.",
                    reply_markup=self.createKeyboard(kbd)
                )

        await self.send(text=text, reply_markup=[
            [
                {"text" : "✖️ Annulla richiesta", "callback_data" : "/start"}
            ]
        ])

    async def close(self):
        user = self.user()
        chat : Chat = Chat.get_or_none((Chat.sender == user) | (Chat.receiver == user))
        
        if chat is None:
            await self.send(
                text="La chat non esiste, è già stata chiusa.", 
                reply_markup=[
                    [
                        {"text" : "Torna indietro", "callback_data" : "/start"}
                    ]
                ]
            )
            return

        chat.sender.status = UserStatus.NORMAL.value
        chat.sender.save()
        
        chat.receiver.status = UserStatus.NORMAL.value
        chat.receiver.save()

        chat.closed_date = datetime.now()
        chat.save()

        role = ["Utente", "Amministratore"]

        destinatario = chat.sender if user.role == UserRole.ADMIN.value else chat.receiver

        kbd = [
            [
                {"text" : "Torna indietro", "callback_data" : "/start"}
            ]
        ]

        await self.bot.send_message(
            chat_id=destinatario.id,
            text=f"🤖 L' {role[user.role - 1].capitalize()} ha chiuso la chat.",
            reply_markup=self.createKeyboard(kbd)
        )

        await self.bot.send_message(
            chat_id=user.id,
            text="✅ La chat è stata chiusa correttamente!",
            reply_markup=self.createKeyboard(kbd)
        )

    async def action(self):
        user : User = self.user()

        if self.is_callback_data():
            cbdata = self.text().split(" - ")
            if len(cbdata) > 2:
                op = cbdata[2]
                
                if op.lower() == "close":
                    await self.close()
            else:
                if user.role == UserRole.USER.value:
                    await self.send_request()
                elif user.role == UserRole.ADMIN.value:
                    await self.accept()
        elif self.is_message() and user.status == UserStatus.CHAT.value:
            await self.handle_chat()