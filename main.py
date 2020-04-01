#!/usr/bin/python3.7
from app import app
from app.api.user_service import UserRegistrationService, UserLoginService
from flask_restful import Api

if __name__ == "main":
    try:
        api = Api(app)
        api.add_resource(UserRegistrationService, '/api/user_service/user_registration')
        api.add_resource(UserLoginService, '/api/user_service/login')
    except Exception as e:
        print(e)