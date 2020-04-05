from config import SmartCalenderConfig
from flask import Flask
from mongoengine import *
import os
from app.utililty.middleware import validate_jwt


app = Flask(__name__)
app.config.from_object(SmartCalenderConfig)
app.config['SECRET_KEY'] = os.urandom(24)
host = (app.config['HOST']).format(os.getenv('db_user_name'), os.getenv('db_password'))
db = connect(user=os.getenv('db_user_name'), password=os.getenv('db_password'), host=host)
validate_jwt(app)
