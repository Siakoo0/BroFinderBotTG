from pyrogram import Client

from json import load
from importlib import import_module
from inspect import isabstract
from glob import glob

class Bot:
    def __init__(self) -> None:
        with open("bot.json", "r") as fp:
            self.cnf = load(fp)
            del self.cnf["version"]
            
        self.client = Client(**self.cnf)
        self.loadHandlers()
        
    def loadHandlers(self):
        handlers = glob("./source/handlers/commands/**/*.py", recursive=True)
        for fname in handlers:
            # Costruisco il percorso per importare il modulo
            class_name_string = fname.replace(".py", "") \
                                     .replace("\\", ".") \
                                     .replace("/", ".") \
                                     .strip(".")

            try:
                # Importo il modulo
                module = import_module(class_name_string)
                # Prelevo la classe dal modulo e la istanzio se non è astratta
                handler = getattr(module, class_name_string.split(".")[-1])

                # Se non è una classe astratta
                if  not isabstract(handler) and "__" not in fname:
                    class_instance = handler()
                    self.client.add_handler(class_instance)
            except Exception as e:
                print("Errore avvenuto durante il caricamento della classe {}: ".format(class_name_string), e)

    def run(self):
        self.client.run()