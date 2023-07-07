from source.models.BaseModel import BaseModel
from source.models.User import User


import datetime

from peewee import AutoField, ForeignKeyField, DateTimeField, CharField


class Chat(BaseModel):
    id = AutoField()
    sender = ForeignKeyField(User, to_field="id") 
    receiver = ForeignKeyField(User, to_field="id", null=True) 
    open_date = DateTimeField(default=datetime.datetime.utcnow())
    closed_date = DateTimeField(null=True)