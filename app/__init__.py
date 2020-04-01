from config import SmartCalenderConfig
from flask import Flask
from mongoengine import *


app = Flask(__name__)
app.config.from_object(SmartCalenderConfig)
db = connect(app.config["MONGO_DB_NAME"])
