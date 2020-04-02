from config import SmartCalenderConfig
from flask import Flask
from mongoengine import *
import os
from app.utililty.middleware import validate_jwt


app = Flask(__name__)
app.config.from_object(SmartCalenderConfig)
app.config['SECRET_KEY'] = os.urandom(24)
db = connect(app.config["MONGO_DB_NAME"])
validate_jwt(app)
