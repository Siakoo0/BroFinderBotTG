from source.models.BaseModel import BaseModel
from peewee import IntegerField, BigIntegerField

class User(BaseModel):
    id = BigIntegerField(primary_key=True)
    role = IntegerField(null=False)
    status = IntegerField(null=False)