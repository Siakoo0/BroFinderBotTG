from source.Bot import Bot

from source.models.BaseModel import db

from source.models.Channel import Channel
from source.models.User import User
from source.models.Chat import Chat

if __name__ == "__main__":
    # db.create_tables([
    #     User, 
    #     Channel,
    #     Chat, 
    #     Channel.users.get_through_model()
    # ])

    bot : Bot = Bot()
    bot.run()