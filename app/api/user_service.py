from flask_restful import Resource
from app.model.user import User, UserSchema, UserAvailableSlots, UserAvailableSlotsSchema, SlotsSchema
from flask import request, Response, g
from werkzeug.security import generate_password_hash, check_password_hash
import json
import jwt
import datetime
from app import app
import threading
from app.utililty.calender_integration import send_mail


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
                               key=app.config['SECRET_KEY'])
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
            user_info = g.user_info

            post_data['user'] = str(user_info.id)
            # To check for mandatory login fields
            mandatory_fields = ["availability_date", "available_slots"]
            if not all(i in post_data for i in mandatory_fields):
                raise Exception("Please enter {} for processing".format(','.join(mandatory_fields)))

            for slot in post_data['available_slots']:
                slot['start_time'] = str(datetime.datetime.strptime(slot['start_time'], "%H:%M:%S"))
                slot['end_time'] = str(datetime.datetime.strptime(slot['end_time'], "%H:%M:%S"))

            post_data['availability_date'] = str(datetime.datetime.strptime(post_data['availability_date'], "%Y-%m-%d"))
            slot_schema = UserAvailableSlotsSchema()
            slots, err_msg = slot_schema.load(post_data)
            if not err_msg:
                if not UserAvailableSlots.objects(user=post_data['user'],
                                                  availability_date=slots.availability_date):
                    slots.save()
                else:
                    check_slots = UserAvailableSlots.objects.get(user=post_data['user'],
                                                                 availability_date=slots.availability_date)
                    for slot in check_slots.available_slots:
                        for new_slot in slots.available_slots:
                            if slot.start_time == new_slot.start_time:
                                raise Exception('{} overlapping start time'.format(str(new_slot.start_time)))
                    check_slots.available_slots += slots.available_slots
                    check_slots.save()

        except Exception as e:
            return Response(response=json.dumps({"message": str(e)}), status=400, content_type="application/json")

        msg = err_msg if err_msg else {"message": "Added Successfully"}
        status = 400 if err_msg else 200

        return Response(response=json.dumps(msg), status=status, content_type="application/json")


class CheckUserSlot(Resource):
    """
    This is base class for checking available slots
    """
    def get(self):
        try:
            query = request.args

            mandatory_fields = ["email", "date"]
            if not all(i in query for i in mandatory_fields):
                raise Exception("Please enter {} for processing".format(','.join(mandatory_fields)))

            # To check validity of the user
            check_user = User.objects(email=query['email'])
            if not check_user:
                raise Exception("No user with email id {} exists".format(query['email']))

            # To check if that user has marked available slots for that day
            availability_date = datetime.datetime.strptime(query['date'], "%Y-%m-%d")
            user_data = UserAvailableSlots.objects(user=str(check_user[0].id), availability_date=availability_date,
                                                   available_slots__exists=True)
            if not user_data:
                raise Exception("User has not marked availability for this date")

            user_data = user_data[0]
            slots = user_data.available_slots
            slots = [i for i in slots if not getattr(i, 'user')]

            # To check if any slot is available
            if not slots:
                raise Exception('No slots available')

            slots = sorted(slots, key=lambda slot_obj: slot_obj.start_time)
            slots_schema = SlotsSchema()
            slots, err_msg = slots_schema.dump(slots, many=True)

        except Exception as e:
            return Response(response=json.dumps({"message": str(e)}), status=400, content_type="application/json")

        msg = err_msg if err_msg else slots
        status = 400 if err_msg else 200
        return Response(response=json.dumps(msg), status=status, content_type="application/json")


class BookUserSlot(Resource):
    """
    This is base class for booking available slots of a user
    """
    def post(self):
        try:
            post_data = json.loads(request.data)
            user_info = g.user_info

            mandatory_fields = ["email", "date", "slot", "summary", "description"]
            if not all(i in post_data for i in mandatory_fields):
                raise Exception("Please enter {} for processing".format(','.join(mandatory_fields)))

            # To check validity of the user
            check_user = User.objects(email=post_data['email'])
            if not check_user:
                raise Exception("No user with email id {} exists".format(post_data['email']))

            # To check if that user has marked available slots for that day
            availability_date = datetime.datetime.strptime(post_data['date'], "%Y-%m-%d")
            user_data = UserAvailableSlots.objects(user=str(check_user[0].id), availability_date=availability_date,
                                                   available_slots__exists=True)
            if not user_data:
                raise Exception("User has not marked availability for this date")

            start_time = datetime.datetime.strptime(post_data['slot']['start_time'], "%H:%M:%S")
            end_time = datetime.datetime.strptime(post_data['slot']['end_time'], "%H:%M:%S")

            # To make sure booking happens only for future
            if availability_date.date() < datetime.datetime.now().date() or \
                    start_time.time() < datetime.datetime.now().time():
                raise Exception('You cannot go in past')

            # To avoid concurrency issue
            lo = threading.Lock()
            lo.acquire()

            # To check your own schedule at that time
            self_slot_check = UserAvailableSlots.objects(user=str(user_info.id), availability_date=availability_date,
                                                         available_slots__match={'start_time': start_time,
                                                                                 'end_time': end_time,
                                                                                 'user__ne': None})
            if self_slot_check:
                raise Exception("You already have a booking at that time")

            # To check if user has some schedule at that time
            slot_check = UserAvailableSlots.objects(user=str(check_user[0].id), availability_date=availability_date,
                                                    available_slots__match={'start_time': start_time,
                                                                            'end_time': end_time,
                                                                            'user': None})
            if not slot_check:
                raise Exception('Slot not available or already booked')

            all_slots = slot_check[0]

            # To find old slot in db and replace it with new one with user id in it
            old_obj = None
            new_obj = None
            for slot in all_slots.available_slots:
                if slot.start_time == start_time:
                    old_obj = slot
                    new_obj = slot
                    setattr(new_obj, 'user', user_info)
                    setattr(new_obj, 'booked_by', user_info)
                    setattr(new_obj, 'summary', post_data['summary'])
                    setattr(new_obj, 'description', post_data['description'])
                    break

            self_slots = UserAvailableSlots.objects(user=str(user_info.id), availability_date=availability_date)
            if self_slots:
                self_slots = self_slots[0]
            else:
                self_slots, err_msg = UserAvailableSlotsSchema().load({'user': str(user_info.id),
                                                                       'availability_date': str(availability_date)})
            if old_obj:
                all_slots.available_slots.remove(old_obj)
                all_slots.available_slots.append(new_obj)
                all_slots.save()

                new_obj.user = check_user[0]
                if getattr(self_slots, 'available_slots', None):
                    self_slots.available_slots = [i for i in self_slots.available_slots
                                                  if i.start_time != old_obj.start_time]
                self_slots.available_slots.append(new_obj)
                self_slots.save()
            lo.release()
            if not ('TESTING' in app.config and app.config['TESTING']):
                send_mail(new_obj, availability_date, [user_info.email, check_user[0].email])
        except Exception as e:
            return Response(response=json.dumps({"message": str(e)}), status=400, content_type="application/json")

        return Response(response=json.dumps({"message": "Booked Successfully"}), status=200,
                        content_type="application/json")
