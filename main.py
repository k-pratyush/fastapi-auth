from dotenv import load_dotenv
from fastapi import FastAPI
import uvicorn
import mongoengine as db
import bcrypt
import jwt
import json
import os

load_dotenv()

app = FastAPI()

class User(db.Document):
    meta = {'allow_inheritance': True}
    username = db.StringField(required=True)
    email = db.EmailField(required=True, unique=True)
    password = db.StringField(required=True)

@app.on_event('startup')
def startup():
    db.connect('test1')

@app.on_event('shutdown')
def shutdown():
    db.disconnect()

@app.get('/')
async def home():
    return {
        "success": True,
        "secret": os.environ.get('secret'),
        }

@app.post('/signup')
def signup(user_data):
    try:
        data = json.loads(user_data)
        password = data['password'].encode('utf8')
        username = data['username']
        email = data['email']
        hashed = bcrypt.hashpw(password, bcrypt.gensalt())
        try:
            user = User(username=username, password=hashed, email=email)
            user.save()
            token = jwt.encode({"email": email}, os.environ.get('secret'), algorithm='HS256')
            return {
                "success": True
            }
        except db.errors.NotUniqueError:
            return {
                "success": False,
                "message": "Email already exists"
            }
    except KeyError:
        return {
            "success": False,
            "message": "Incomplete form"
            }

@app.post('/login')
def login(user_data):
    data = json.loads(user_data)
    try:
        username = data['username']
        password = data['password']
        email = data['email']
        user = User.objects(email=email)
        if user:
            if bcrypt.checkpw(password.encode('utf-8'),
                                user[0].password.encode('utf-8')):
                token = jwt.encode({"email": email},
                                   os.environ.get('secret'), algorithm='HS256')
                return {
                    "success": True,
                    "token": token
                }
            else:
                return {
                    "success": False,
                    "message": "Incorrect password"
                }
        else:
            return {
                "success": False,
                "message": "No user found"
            }
    except KeyError:
        print('Incomplete form')
