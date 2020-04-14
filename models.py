import mongoengine as db

class User(db.Document):
    meta = {'allow_inheritance': True}
    username = db.StringField(required=True)
    email = db.EmailField(required=True, unique=True)
    password = db.StringField(required=True)

class Post(db.Document):
    meta = {'allow_inheritance': True}
    text = db.StringField()
    author = db.EmailField(required=True)
