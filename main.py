from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response
import uvicorn
import mongoengine as db
import bcrypt
import jwt
from http.cookies import SimpleCookie
import json
import os

load_dotenv()

app = FastAPI()

class User(db.Document):
    meta = {'allow_inheritance': True}
    username = db.StringField(required=True)
    email = db.EmailField(required=True, unique=True)
    password = db.StringField(required=True)

class Post(db.Document):
    meta = {'allow_inheritance': True}
    text = db.StringField()
    author = db.EmailField(required=True)

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
async def signup(request: Request, response: Response):
    try:
        data = json.loads(await request.body())
        password = data['password'].encode('utf8')
        username = data['username']
        email = data['email']
        hashed = bcrypt.hashpw(password, bcrypt.gensalt())
        try:
            user = User(username=username, password=hashed, email=email)
            user.save()
            token = jwt.encode({"email": email}, os.environ.get(
                'secret'), algorithm='HS256').decode("utf-8")
            response.set_cookie(
                key="token", value=f"Bearer {token}", httponly=True)
            return {
                "success": True,
                "token": token
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
async def login(request: Request, response: Response):
    data = json.loads(await request.body())
    try:
        username = data['username']
        password = data['password']
        email = data['email']
        user = User.objects(email=email)
        if user:
            if bcrypt.checkpw(password.encode('utf-8'),
                                user[0].password.encode('utf-8')):
                token = jwt.encode({"email": email},
                                   os.environ.get('secret'), algorithm='HS256').decode("utf-8")
                response.set_cookie(
                    key="token", value=f"Bearer {token}", httponly=True)
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


@app.post('/protected-route')
async def get_protected_route(request: Request):
    try:
        text = json.loads(await request.body())
        print(text)
        token = request.cookies.get('token')
        token = token.split(" ")[1]
        data = jwt.decode(token, os.environ.get('secret'), algorithms=['HS256'])
        user = User.objects(email = data['email'])
        if user:
            try:
                newPost = Post(text=text['text'], author=user[0].email)
                newPost.save()
                return {
                    "success": True,
                    "message": "You are authenticated",
                    "text": text['text']
                }
            except:
                return {
                    "success": False,
                    "message": "there was an error posting"
                }
        else:
            return {
                "success": False,
                "message": "You are not authenticated"
            }
    except KeyError:
        return {
            "success": False,
            "message": "Incomplete form"
        }
    except AttributeError:
        return {
            "success": False,
            "message": "You are not authenticated"
        }
