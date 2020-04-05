from config import SmartCalenderConfig
from flask import Flask
from mongoengine import *
import os
from app.utililty.middleware import validate_jwt


app = Flask(__name__)
app.config.from_object(SmartCalenderConfig)
app.config['SECRET_KEY'] = os.urandom(24)
host = (app.config['HOST']).format(os.environ.get('db_user_name'), os.environ.get('db_password'))
db = connect(username=os.environ.get('db_user_name'), password=os.environ.get('db_password'), host=host)
validate_jwt(app)
