#!/usr/bin/python3.7
from app import app
from flask_restful import Api
from urls import bind_url

if __name__ == "main":
    try:
        api = Api(app)
        bind_url(api)
    except Exception as e:
        print(e)