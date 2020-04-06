from flask import request, g, Response
import jwt
import json
from app.model.user import User


exception_from_jwt = ['login', 'register', 'register_credentials']


def validate_jwt(app):
    @app.before_request
    def validate():
        # To give exemption to login and register from jwt token verification
        if any(i in request.url for i in exception_from_jwt):
            return
        else:
            msg = None
            auth_token = request.headers.get('Authorization')
            if auth_token is None:
                msg = 'Authorization token missing'

            if not msg:

                try:
                    payload = jwt.decode(auth_token, app.config['SECRET_KEY'])
                    email = payload['email']
                    user = User.objects(email=email)

                    # Invalid email id in token
                    if not user:
                        msg = 'Token is corrupt'
                    else:
                        g.user_info = user[0]

                except jwt.ExpiredSignatureError:
                    msg = 'Signature expired. Please log in again.'
                except jwt.InvalidTokenError:
                    msg = 'Invalid token. Please log in again.'

            if msg:
                return Response(response=json.dumps({"message": msg}), status=400, content_type="application/json")
            return
