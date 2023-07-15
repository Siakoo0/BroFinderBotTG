from peewee import MySQLDatabase, Model

db = MySQLDatabase(
    "brofinder_db", 
    host='localhost',
    port=3306, 
    user='root', 
    password='password'
)

class BaseModel(Model):
    class Meta:
        loaded_entities = False
        database = db
