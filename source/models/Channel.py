from source.models.BaseModel import BaseModel
from source.models.User import User

from peewee import BigIntegerField, ManyToManyField


class Channel(BaseModel):
    id = BigIntegerField(primary_key=True)
    users = ManyToManyField(User, backref="users")
