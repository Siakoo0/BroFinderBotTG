from source.Bot import Bot

from source.models.BaseModel import db

from source.models.Channel import Channel
from source.models.User import User
from source.models.Chat import Chat

if __name__ == "__main__":
    bot : Bot = Bot()
    bot.run()