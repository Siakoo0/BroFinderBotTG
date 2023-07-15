from source.handlers.abs_handlers.Callback import Callback
from source.api.SearchApi import SearchApiHelper 
from source.api.ProductApi import ProductApiHelper 

from pyrogram import filters
from json import dumps


class NotificationSearchHandler(Callback):
    def filters(self):
        return filters.regex("^ntfc - ")

    async def action(self):
        search_helper = SearchApiHelper()
        product_helper = ProductApiHelper()

        split = self.text().split(" - ")
        text = split[1]
        check_url = len(split) > 2

        if check_url:            
            resp = await product_helper.get_one(text)
            text=resp["url"].lower()

        field = self.update.message.reply_markup.inline_keyboard[0][0].text
        
        arr = ["🔔 Attiva notifiche", "🔕 Disattiva notifiche"]
        
        ind = arr.index(field)
        next_ind = (ind + 1) % len(arr)
        
        self.update.message.reply_markup.inline_keyboard[0][0].text = arr[next_ind]
            
        await search_helper.put({
            "text" : text,
            "user" : self.update.from_user.id,
            "forward" : next_ind == 1
        })

        await self.update.edit_message_reply_markup(reply_markup=self.update.message.reply_markup)
        
        await self.update.answer(text="🤖 Notifiche " + ("attivate" if next_ind == 1 else "disattivate") + ".")