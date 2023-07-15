from pyrogram import filters
from pyrogram.errors.exceptions.bad_request_400 import MessageNotModified

import psutil, os, time
from json import load


from source.api.SearchApi import SearchApiHelper
from source.enums.User import UserRole
from source.handlers.abs_handlers.Callback import Callback


class InformationHandler(Callback): 
    def filters(self):
        return filters.regex("^info$")

    async def action(self):
        kbd : list = [
            [
                {"text" : "🔄 Aggiorna", "callback_data":"info"}
            ],
            [
                {"text" : "🔙 Torna indietro", "callback_data":"/start"}
            ]
        ]
        
        user = ""

        if self.update.from_user.first_name is not None:
            user+=self.update.from_user.first_name.strip() + " "
            
        if self.update.from_user.last_name is not None:
            user+=self.update.from_user.last_name.strip() + " "
            
        user = user.strip()
        username = self.update.from_user.username

        helper = SearchApiHelper()
        resp = await helper.get({"user": self.update.from_user.id} if self.user().role != UserRole.ADMIN.value else {})
                
        process = psutil.Process(os.getpid())
        
        up_time = time.strftime("%d/%m/%Y %H:%M:%S", time.localtime(process.create_time()))
        
        with open("bot.json", "r") as fp:
            config = load(fp)
        
        text =  "👤 <b>Informazioni utente</b>\n\n"+\
                f"🌐  {user}{f' ( @{username.strip()} )' if username is not None else ''}"+\
                f"\n#️⃣ {self.update.from_user.id}" +\
                f"\n🌟 Ruolo: {UserRole(self.user().role).name.lower().capitalize()}" +\
                f"\n💠 Ricerche effettuate: {len(resp)}" +\
                f"\n\n🤖 <b>Informazioni Bot</b>" +\
                f"\n\n🌐  @BroFinder" +\
                f"\n🆙  Attivo dal {up_time}" +\
                f"\n👉 Versione {config['version']}"
                 
        if self.user().role == UserRole.ADMIN.value:
            _, __, load15 = psutil.getloadavg()
            cpu_tot = os.cpu_count()
            
            # Carico sul sistema ogni 15 minuti diviso il numero di cpu a cui viene assegnato il lavoro 
            cpu_usage = "{:.2f}%".format((load15/cpu_tot) * 100)
            
            memory_used_perc = "{:02.2f}".format(psutil.virtual_memory()[2]) #Memoria utilizzata in perc
            memory_used_gb = "{:.2f}G".format(round(psutil.virtual_memory()[3]/1000000000, 2)) # Memoria usata in GB
            
            text+=f"\n\nℹ️ Informazioni sul sistema\n\n🖥 Carico della CPU: {cpu_usage} ( {cpu_tot} CPU ) \n💾 Memoria utilizzata: {memory_used_perc}% ({memory_used_gb})"
                
                
        text += f"\n\n🧑‍💻 Powered by Antonio Lauro & Emanuele Pannuccio"
        
        try:
            await self.send(text=text, reply_markup=kbd)
        except MessageNotModified: pass