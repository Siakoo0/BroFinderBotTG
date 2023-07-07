from pyrogram import Client

from json import load
from importlib import import_module
from inspect import isabstract
from glob import glob

class Bot:
    def __init__(self) -> None:
        with open("bot.json", "r") as fp:
            self.cnf = load(fp)
            
        self.client = Client(**self.cnf)
        self.loadHandlers()
        
    
    def loadHandlers(self):
        for fname in glob("./source/handlers/commands/**/*.py", recursive=True):
            # Costruisco il percorso per importare il modulo
            class_name_string = fname.replace(".py", "") \
                                     .replace("\\", ".") \
                                     .replace("/", ".") \
                                     .strip(".")

            # Importo il modulo
            module = import_module(class_name_string)

            # Prelevo la classe dal modulo e la istanzio se non è astratta
            handlers = getattr(module, class_name_string.split(".")[-1])

            # Se non è una classe astratta
            if  not isabstract(handlers) and \
                "__" not in fname:
                
                class_instance = handlers()

                self.client.add_handler(class_instance)

    def run(self):
        self.client.run()