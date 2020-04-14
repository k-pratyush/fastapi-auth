from fastapi.testclient import TestClient
from models import User
import jwt
from main import app
import os
import mongoengine

client = TestClient(app)
mongoengine.connect('test1').drop_database('test1')


def test_home():
    response = client.get('/')
    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "secret": os.environ.get('secret'),
    }


def test_protected_route_unauthenticated():
    response = client.post(
        '/protected-route',
        json={"text": "this wont get saved"}
    )
    assert response.status_code == 400
    assert response.json() == {
        "detail": "You are not authenticated"
    }


def test_signup():
    response = client.post(
        '/signup',
        json={"username": "test", "email": "test@123.com", "password": "abc"}
    )
    assert response.status_code == 201
    token = jwt.encode({"email": "test@123.com"}, os.environ.get(
        'secret'), algorithm='HS256').decode("utf-8")
    assert response.json() == {
        "success": True,
        "token": token
    }


def test_login():
    response = client.post(
        '/login',
        json={"username": "test", "email": "test@123.com", "password": "abc"}
    )
    assert response.status_code == 200
    token = jwt.encode({"email": "test@123.com"}, os.environ.get(
        'secret'), algorithm='HS256').decode("utf-8")
    assert response.json() == {
        "success": True,
        "token": token
    }


def test_protected_route():
    text = 'this is a test'
    response = client.post(
        '/protected-route',
        json={"text": text}
    )
    assert response.status_code == 201
    assert response.json() == {
        "success": True,
        "message": "You are authenticated",
        "text": "this is a test"
    }


def test_signup_duplicate_email():
    mongoengine.connect('test1').drop_database('test1')
    user = User(username="test", email="test@123.com", password="abc")
    user.save()
    response = client.post(
        '/signup',
        json={"username": "test", "email": "test@123.com", "password": "abc"}
    )
    assert response.status_code == 412
    assert response.json() == {
        "detail": "Email already exists"
    }


def test_signup_incomplete_form():
    response = client.post(
        '/signup',
        json={"username": "abc"}
    )
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Incomplete request form"
    }


def test_login_incorrect_password():
    response = client.post(
        '/login',
        json={
            "username": "test",
            "email": "test@123.com",
            "password": "incorrect password"})
    assert response.status_code == 403
    assert response.json() == {
        "detail": "Incorrect password"
    }


def test_login_incorrect_email():
    response = client.post(
        '/login',
        json={
            "username": "test",
            "email": "wrong@email.com",
            "password": "abc"})
    assert response.status_code == 403
    assert response.json() == {
        "detail": "User not found"
    }


def test_login_incomplete():
    response = client.post(
        '/login',
        json={"email": "wrong@email.com"}
    )
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Incomplete form"
    }
