from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response, HTTPException
import mongoengine as db
import bcrypt
import jwt
from models import User, Post
import json
import os

load_dotenv()

app = FastAPI()


@app.on_event('startup')
def startup():
    datab = db.connect('test1')


@app.on_event('shutdown')
def shutdown():
    db.connect('test1').drop_database('test1')
    db.disconnect()


@app.get('/')
async def home():
    return {
        "success": True,
        "secret": os.environ.get('secret'),
    }


@app.post('/signup', status_code=201)
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
            raise HTTPException(
                status_code=412, detail="Email already exists")
    except KeyError:
        raise HTTPException(
            status_code=400, detail="Incomplete request form")


@app.post('/login')
async def login(request: Request, response: Response):
    data = json.loads(await request.body())
    try:
        username = data['username']
        password = data['password']
        email = data['email']
        user = User.objects(email=email)
        if user:
            try:
                if bcrypt.checkpw(password.encode('utf-8'),
                                  user[0].password.encode('utf-8')):
                    token = jwt.encode({"email": email}, os.environ.get(
                        'secret'), algorithm='HS256').decode("utf-8")
                    response.set_cookie(
                        key="token", value=f"Bearer {token}", httponly=True)
                    return {
                        "success": True,
                        "token": token
                    }
            except ValueError:
                raise HTTPException(
                    status_code=403, detail="Incorrect password")
        else:
            raise HTTPException(status_code=403, detail="User not found")
    except KeyError:
        raise HTTPException(status_code=400, detail='Incomplete form')


@app.post('/protected-route', status_code=201)
async def protected_route(request: Request):
    try:
        text = json.loads(await request.body())
        token = request.cookies.get('token')
        token = token.split(" ")[1]
        data = jwt.decode(
            token,
            os.environ.get('secret'),
            algorithms=['HS256'])
        user = User.objects(email=data['email'])
        if user:
            try:
                newPost = Post(text=text['text'], author=user[0].email)
                newPost.save()
                return {
                    "success": True,
                    "message": "You are authenticated",
                    "text": text['text']
                }
            except BaseException:
                return {
                    "success": False,
                    "message": "there was an error posting"
                }
        else:
            raise HTTPException(
                status_code=403,
                detail="You are not authenticated")
    except KeyError:
        raise HTTPException(status_code=400, detail="Incomplete form")
    except AttributeError:
        raise HTTPException(
            status_code=400,
            detail="You are not authenticated")
