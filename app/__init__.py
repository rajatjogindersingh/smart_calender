from config import SmartCalenderConfig
from flask import Flask
from mongoengine import *
import os
from app.utililty.middleware import validate_jwt
from pathlib import Path
import json


app = Flask(__name__)
app.config.from_object(SmartCalenderConfig)
with app.app_context():
    app.secret_key = os.urandom(24)

validate_jwt(app)

my_file = Path("credentials.json")
if not my_file.is_file():
    file = open("credentials.json", "w")
    cred = app.config['GOOGLE_JSON']
    cred['web']['client_id'] = os.environ.get('client_id')
    cred['web']['project_id'] = os.environ.get('project_id')
    cred['web']['client_secret'] = os.environ.get('client_secret')
    cred['web']['redirect_uris'] = [os.environ.get('redirect_uris')]
    file.write(json.dumps(cred))
    file.close()

host = (app.config['HOST']).format(os.environ.get('db_user_name'), os.environ.get('db_password'))
db = connect(username=os.environ.get('db_user_name'), password=os.environ.get('db_password'), host=host)