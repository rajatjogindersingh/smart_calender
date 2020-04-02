from flask_restful import Resource
from app.model.user import User, UserSchema, UserAvailableSlots, UserAvailableSlotsSchema, Slots
from flask import request, Response, g
from werkzeug.security import generate_password_hash, check_password_hash
import json
import jwt
import datetime
from app import app


class UserRegistrationService(Resource):
    """
    The Base class used for registration of user
    """
    def post(self):
        """
        This function is used to register a user
        :return: Flask Response
        """
        try:
            post_data = json.loads(request.data)
            user_schema = UserSchema()
            user, err_msg = user_schema.load(post_data)

            if not err_msg:
                # To check duplication of user
                if User.objects(email=user.email):
                    raise Exception("User Already exists")
                setattr(user, 'password', generate_password_hash(getattr(user, 'password')))
                user.save()

        except Exception as e:
            return Response(response=json.dumps({"message": str(e)}), status=400, content_type="application/json")

        msg = err_msg if err_msg else {"message": "Added Successfully"}
        status = 400 if err_msg else 201

        return Response(response=json.dumps(msg), status=status, content_type="application/json")


class UserLoginService(Resource):
    """
    The Base class used for login by user
    """
    def post(self):
        """
        This function is used to login a user
        :return: Flask Response
        """
        try:
            post_data = json.loads(request.data)

            # To check for mandatory login fields
            mandatory_fields = ["email", "password"]
            if not all(i in post_data for i in mandatory_fields):
                raise Exception("Please enter email and password for processing")

            # To check if user record exists in database
            if not User.objects(email=post_data['email']):
                raise Exception("User does not exists. Please Sign Up")

            user_data = User.objects.get(email=post_data['email'])
            if not check_password_hash(user_data.password, post_data["password"]):
                raise Exception("Invalid password")

            token = jwt.encode({'email': post_data['email'],
                                "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},
                               key=app.config.get('SECRET_KEY'))
        except Exception as e:
            return Response(response=json.dumps({"message": str(e)}), status=400, content_type="application/json")

        msg = {"token": token.decode('UTF-8')}
        status = 200

        return Response(response=json.dumps(msg), status=status, content_type="application/json")


class UserAvailabilityService(Resource):
    """
    The Base class used for by user to set the availability slots
    """
    def post(self):
        """
        This function is used to mark all available slots user
        :return: Flask Response
        """
        try:
            post_data = json.loads(request.data)

            # To check for mandatory login fields
            mandatory_fields = ["user_id", "availability_date", "available_slots"]
            if not all(i in post_data for i in mandatory_fields):
                raise Exception("Please enter {} for processing".format(','.join(mandatory_fields)))

            slot_schema = UserAvailableSlotsSchema()
            post_data['id'] = post_data['user_id']
            slots, err_msg = slot_schema.load(post_data)
            if not err_msg:
                slots.save()

        except Exception as e:
            return Response(response=json.dumps({"message": str(e)}), status=400, content_type="application/json")

        msg = {"message": "Added Successfully"}
        status = 201

        return Response(response=json.dumps(msg), status=status, content_type="application/json")
