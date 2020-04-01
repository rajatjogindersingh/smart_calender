from config import SmartCalenderConfig
from flask import Flask
from flask_restful import Api
from mongoengine import *
from app.api.user_service import UserRegistrationService

app = Flask(__name__)
app.config.from_object(SmartCalenderConfig)
db = connect(app.config["MONGO_DB_NAME"])
api = Api(app)

api.add_resource(UserRegistrationService, '/api/user_service/user_registration')