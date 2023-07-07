from peewee import MySQLDatabase, Model

db = MySQLDatabase(
    "brofinder_db", 
    host='127.0.0.1', 
    port=3306, 
    user='root', 
    password='password'
)

class BaseModel(Model):
    class Meta:
        loaded_entities = False
        database = db