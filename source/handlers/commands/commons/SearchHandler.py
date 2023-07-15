from pyrogram import filters
from pyrogram.types import CallbackQuery, Message

from datetime import datetime
from enum import Enum

from source.handlers.abs_handlers.Common import Common
from source.enums.User import UserStatus

from source.filters.UpdateFilter import regex, update_check
from source.filters.UserFilter import status

from source.api.ProductApi import ProductApiHelper 
from source.api.SearchApi import SearchApiHelper 

from itertools import zip_longest

class SearchCommand(Enum):
    MENU=0
    PROD=1

class SearchHandler(Common):

    def filters(self):
        return (regex("^prdc - ", CallbackQuery) | update_check(Message)) & (status(UserStatus.SEARCH))

    def grouper(self, iterable, n):
        args = [iter(iterable)] * n
        return zip_longest(fillvalue=None, *args)

    async def menu(self, data_json, config):
        LIMIT_TEXT=50

        await SearchApiHelper().create(
            {
                "text" : config["keyword"],
                "user" : self.update.from_user.id,
                "forward" : False
            }
        )
        
        if data_json["total"] == 0 and isinstance(self.update, Message):
            kbd = [
                [
                    {"text" : "✖️ Annulla ricerca", "callback_data" : f"cncsearch - ({config['keyword']}"}
                ]
            ]
            
            update = await self.send(text="🤖 Attendi qualche secondo, il nostro bot sta lavorando per te.", reply_markup=kbd)
            
            await SearchApiHelper().create(
                {
                    "text" : config["keyword"],
                    "user" : self.update.from_user.id,
                    "forward" : False,
                    "msg_id" : update.id
                }
            )

            return
        
        
        search_check = await SearchApiHelper().get({"user" : self.update.from_user.id, "text" : config["keyword"]})
        
        activated_not = len(search_check) > 0 and search_check[0]["forward"]
        
        kbd = [
            [
                {
                    "text" : "🔔 Attiva notifiche" if not activated_not else "🔕 Disattiva notifiche", 
                    "callback_data" : f"ntfc - {config['keyword']}"
                },
            ],
            [
                {
                    "text" : "🔄 Aggiorna pagina", 
                    "callback_data" : f"prdc - ({config['page']}, {SearchCommand.MENU.value}, '{config['keyword']}')"
                }
            ]
        ]
        
        for prod in data_json["data"]:
            kbd.append(
                [
                    {
                        "text" : prod["name"][:LIMIT_TEXT].strip() + ("..." if len(prod["name"]) > (LIMIT_TEXT-1) else ""), 
                        "callback_data": f"prdc - ({config['page']},{SearchCommand.PROD.value},{prod['_id']},0,{config['keyword']})"
                    }
                ]
            )
            
        frw_pg_btn = {
            "text" : "Pagina successiva 🔜", 
            "callback_data": f"prdc - " + str(
                (
                    config['page'] + 1, 
                    SearchCommand.MENU.value, 
                    config["keyword"]
                )
            )
        }
        
        bck_pg_btn = {
            "text" : "🔙 Pagina precedente", 
            "callback_data": f"prdc - " + str(
                (
                    config['page'] - 1, 
                    SearchCommand.MENU.value, 
                    config["keyword"]
                )
            )
        }
        
        if config["page"] == 0:
            control_ui = [
                {"text" : "🔙 Torna indietro", "callback_data" : "/start"}
            ]
            kbd.append(control_ui)
        else:
            control_ui = [bck_pg_btn]
            kbd.append(control_ui)
            
            kbd.append(
                [
                    {"text" : "🔙 Torna alla prima pagina", "callback_data" : f"prdc - (0,{SearchCommand.MENU.value},{config['keyword']})"}            
                ]
            )
        
        
        if data_json["total"] > ((config['page']+1) * config['size']):
            control_ui.append(frw_pg_btn)
        
        
        text = f"""🔎 Modalità ricerca, risultati {data_json["total"]}
            
🌐 Abbiamo cercato su diversi siti la parola "<code>{config['keyword']}</code>". 

📚 <b>Pagina attuale:</b> {config['page']+1}

👉 <i>Per terminare la ricerca schiaccia il pulsante "Torna indietro" o invia il comando /start</i>"""
            
        try:
            await self.send(text=text, reply_markup=kbd)
        except Exception as e:
            if isinstance(self.update, Message):
                await self.send(text="🤖 Attualmente ci sono dei problemi con il bot, si prega di attenderne la risoluzione. Se l'errore persiste si prega di contattare l'amministratore.")
            else:
                await self.update.answer("🤖 Il contenuto risulta già aggiornato.")
        
    async def product(self, product, config):
        LIMIT_DESC=250
        NAME_LEN=150
        
        ind_image = int(config["image"]) or 0
        
        last_update = datetime.strptime(product['created_at'], "%Y-%m-%d %H:%M:%S.%f")
        
        if len(product["images"]) == 0:
            product["images"].append("https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/No-Image-Placeholder.svg/330px-No-Image-Placeholder.svg.png")
            
        for key, prod in product.items():
            product[key] = prod if prod is not None else "Non disponibile"
            
        price = '{0:.2f}'.format(product['price']) if isinstance(product['price'], float) else product['price']    
        prod_name = product['name']
        review_summ = product['reviews_summary']
        description = product['description']
        
        images = product['images']
        image = images[ind_image]
        
        prod = await SearchApiHelper().get({
            "text" : product["url"].lower(),
            "user" : self.update.from_user.id
        })
        
        btn_not = "🔔 Attiva notifiche" if len(prod) == 0 or not prod[0]["forward"] else "🔕 Disattiva notifiche"
        
        
        message =   f'<a href="{image}">‎</a>' + \
                    f"📙 {prod_name[:NAME_LEN]}{'...' if len(prod_name) > (NAME_LEN+1) else ''}\n\n" + \
                    f"🖼 <b>Immagine n. {config['image']+1} su {len(images)}\n\n" + \
                    f"⭐️ <b>Voto:</b> {review_summ}\n" + \
                    f"💰 <b>Prezzo:</b> {price}{'€' if str(price).lower() != 'non disponibile' else '.'}\n\n" + \
                    f"👉 <b>DESCRIZIONE</b> 👈\n\n" + \
                    f"{description[:LIMIT_DESC]}{'...' if len(description) > (LIMIT_DESC+1) else ''}\n" + \
                    f"\n📆 <i>Ultimo aggiornamento il {last_update.strftime('%d/%m/%Y %H:%M')}</i>"

        cb_bck = (config["page"], SearchCommand.MENU.value, config["search"])

        product_image_nxt = (config["page"], SearchCommand.PROD.value, config["keyword"], config["image"]+1, config["search"])
        product_image_prev = (config["page"], SearchCommand.PROD.value, config["keyword"], config["image"]-1, config["search"])
        
        control_ui = []
        
        if (ind_image+1) < len(product["images"]):
            control_ui.append(
                {"text" : "Immagine successiva 👉", "callback_data" : f"prdc - {str(product_image_nxt)}"}
            ) 
            
        if ind_image > 0:
            control_ui.insert(0,
                {"text" : "👈 Immagine precedente", "callback_data" : f"prdc - {str(product_image_prev)}"}
            ) 

        kbd = [
            [
              {
                  "text" : btn_not, 
                  "callback_data" : f"ntfc - {product['_id']} - 1"
              }  
            ],
            [
                {"text" : "🔗 Vai al prodotto", "url" : product["url"]}
            ],
            control_ui,
            [
                {"text":"🔙 Torna indietro", "callback_data" : f"prdc - {str(cb_bck)}"}
            ]
        ]
        
        
        await self.send(text=message, reply_markup=kbd)


    async def fetch(self, session, url):
        async with session.get(url) as resp:
            return await resp.json()

    async def action(self):
        LIMIT_HIGH = 30
        LIMIT_LOW = 3
         
        message = self.text()
        
        if isinstance(self.update, Message) and (len(message) > LIMIT_HIGH or len(message) < LIMIT_LOW):
            await self.send(
                text="🤖 Invia un numero maggiore di 3 e minore di 230 caratteri per effettuare la ricerca."
            )
            return
        
        
        config = {
            "size" : 10
        }
        
        params = {"size" : 10}
        
        api_prod = ProductApiHelper()
        api_search = SearchApiHelper()
        
        if isinstance(self.update, Message):
            # Modalità Testuale
            params["text"] = config["keyword"] = message
            params["filter"] = "keyword,name"
            
            config["page"] = params["page"] = 0
            config["action"] = SearchCommand.MENU
            
            data = await api_prod.search(**params)
        else:
            # Modalità esplorazione query data
            ops = [elem.strip() for elem in self.text().split(" - ")[1].strip("(").strip(")").split(",")]
            
            config |= {
                "page" : int(ops[0]),
                "action" : SearchCommand(int(ops[1])),
                "keyword" : ops[2].replace("'", "")
            }
                       
            params["page"] = config["page"]
            params["text"] = config["keyword"]
            
            if config["action"] == SearchCommand.MENU:
                params["filter"] = "keyword,name"
                data = await api_prod.search(**params)
            else:
                config["image"] = int(ops[3])
                config["search"] = ops[4].replace("'", "")
                
                data = await api_prod.get_one(config["keyword"])

        if config["action"] == SearchCommand.MENU: 
            await self.menu(data, config)
        else: 
            await self.product(data, config)
        
