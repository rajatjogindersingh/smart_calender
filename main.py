#!/usr/bin/python3.7
from app import app
from app.api.user_service import UserRegistrationService, UserLoginService,UserAvailabilityService, CheckUserSlot
from flask_restful import Api

if __name__ == "main":
    try:
        api = Api(app)
        api.add_resource(UserRegistrationService, '/api/user_service/user_registration')
        api.add_resource(UserLoginService, '/api/user_service/login')
        api.add_resource(UserAvailabilityService, '/api/user_service/mark_available_slots')
        api.add_resource(CheckUserSlot, '/api/user_service/check_available_slots')
    except Exception as e:
        print(e)