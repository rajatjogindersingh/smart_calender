import unittest
from main import app
import json
from config import SmartCalenderTestConfig
import mongoengine as mongo


class BasicTests(unittest.TestCase):

    ############################
    #### setup and teardown ####
    ############################

    # executed prior to each test
    def setUp(self):
        app.config.from_object(SmartCalenderTestConfig)
        mongo.connection.disconnect()
        self.db = mongo.connect(app.config["MONGO_DB_NAME"])
        self.app = app.test_client()
        self.assertEqual(app.debug, False)

    # executed after each test
    def tearDown(self):
        print("tearing down")
        mongo.connection.disconnect()
        self.db.drop_database(app.config["MONGO_DB_NAME"])

    ###############
    #### tests ####
    ###############

    def test_registration(self):
        response = self.app.post('/api/user_service/register',
                                 data=json.dumps(dict(email="abc@gmail.com", password="qwerty")),
                                 follow_redirects=True)
        self.assertEqual(response.status_code, 400)

        response = self.app.post('/api/user_service/register',
                                 data=json.dumps(dict(name="ABC", password="qwerty")),
                                 follow_redirects=True)
        self.assertEqual(response.status_code, 400)

        response = self.app.post('/api/user_service/register',
                                 data=json.dumps(dict(email="abc@gmail.com", password="qwerty", name="ABC")),
                                 follow_redirects=True)
        self.assertEqual(response.status_code, 201)

        response = self.app.post('/api/user_service/register',
                                 data=json.dumps(dict(email="abc@gmail.com", password="qwerty", name="ABC")),
                                 follow_redirects=True)
        self.assertEqual(response.status_code, 400)

    def test_login(self):
        response = self.app.post('/api/user_service/register',
                                 data=json.dumps(dict(email="abc@gmail.com", password="qwerty", name="ABC")),
                                 follow_redirects=True)
        self.assertEqual(response.status_code, 201)

        response = self.app.post('/api/user_service/register',
                                 data=json.dumps(dict(email="xyz@gmail.com", password="qwerty", name="XYZ")),
                                 follow_redirects=True)
        self.assertEqual(response.status_code, 201)

        response = self.app.post('/api/user_service/login',
                                 data=json.dumps(dict(email="abc@gmail.com", password="qwerty")),
                                 follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.post('/api/user_service/login',
                                 data=json.dumps(dict(email="xyz@gmail.com", password="qwerty")),
                                 follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.post('/api/user_service/login',
                                 data=json.dumps(dict(email="abcxyz@gmail.com", password="qwerty")),
                                 follow_redirects=True)
        self.assertEqual(response.status_code, 400)

        response = self.app.post('/api/user_service/login',
                                 data=json.dumps(dict(email="abc@gmail.com")),
                                 follow_redirects=True)
        self.assertEqual(response.status_code, 400)

    def test_jwt_verification(self):
        response = self.app.post('/api/user_service/register',
                                 data=json.dumps(dict(email="abc@gmail.com", password="qwerty", name="ABC")),
                                 follow_redirects=True)
        self.assertEqual(response.status_code, 201)

        response = self.app.post('/api/user_service/register',
                                 data=json.dumps(dict(email="xyz@gmail.com", password="qwerty", name="XYZ")),
                                 follow_redirects=True)
        self.assertEqual(response.status_code, 201)

        # Without jwt token
        response = self.app.get('/api/user_service/check_available_slots',
                                follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message'], 'Authorization token missing')

        # Invalid jwt token
        response = self.app.get('/api/user_service/check_available_slots', headers={'Authorization': "dummy"},
                                follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message'], 'Invalid token. Please log in again.')

    def test_mark_availability_service(self):
        response = self.app.post('/api/user_service/register',
                                 data=json.dumps(dict(email="abc@gmail.com", password="qwerty", name="ABC")),
                                 follow_redirects=True)
        self.assertEqual(response.status_code, 201)

        response = self.app.post('/api/user_service/login',
                                 data=json.dumps(dict(email="abc@gmail.com", password="qwerty")),
                                 follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        jwt = response.json['token']
        response = self.app.post('/api/user_service/mark_available_slots',
                                 data=json.dumps(dict(availability_date="2020-04-05",
                                                      available_slots=[{"start_time": "13:00:00","end_time": "14:00:00"}])),
                                 follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message'], 'Authorization token missing')

        response = self.app.post('/api/user_service/mark_available_slots',
                                 data=json.dumps(dict(availability_date="2020-04-05",
                                                      available_slots=[
                                                          {"start_time": "13:00:00", "end_time": "14:00:00"}])),
                                 headers={'Authorization': jwt},
                                 follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Overlapping range
        response = self.app.post('/api/user_service/mark_available_slots',
                                 data=json.dumps(dict(availability_date="2020-04-05",
                                                      available_slots=[
                                                          {"start_time": "13:00:00", "end_time": "14:00:00"}])),
                                 headers={'Authorization': jwt},
                                 follow_redirects=True)
        self.assertEqual(response.status_code, 400)

        # Expired dates
        response = self.app.post('/api/user_service/mark_available_slots',
                                 data=json.dumps(dict(availability_date="2020-04-03",
                                                      available_slots=[
                                                          {"start_time": "13:00:00", "end_time": "14:00:00"}])),
                                 headers={'Authorization': jwt},
                                 follow_redirects=True)
        self.assertEqual(response.status_code, 400)

    def test_check_availability_service(self):
        response = self.app.post('/api/user_service/register',
                                 data=json.dumps(dict(email="abc@gmail.com", password="qwerty", name="ABC")),
                                 follow_redirects=True)
        self.assertEqual(response.status_code, 201)

        response = self.app.post('/api/user_service/login',
                                 data=json.dumps(dict(email="abc@gmail.com", password="qwerty")),
                                 follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        jwt = response.json['token']

        response = self.app.post('/api/user_service/mark_available_slots',
                                 data=json.dumps(dict(availability_date="2020-04-05",
                                                      available_slots=[
                                                          {"start_time": "13:00:00", "end_time": "14:00:00"}])),
                                 headers={'Authorization': jwt},
                                 follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Missing token
        response = self.app.get(
            '/api/user_service/check_available_slots?email=abc@gmail.com&date=2020-04-05',
            follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message'], 'Authorization token missing')

        response = self.app.get(
            '/api/user_service/check_available_slots?email=abc@gmail.com&date=2020-04-05',
            headers={'Authorization': jwt}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [{"start_time": "13:00:00", "end_time": "14:00:00"}])

        response = self.app.get(
            '/api/user_service/check_available_slots?email=abc@gmail.com',
            headers={'Authorization': jwt}, follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"message": "Please enter email,date for processing"})

    def test_check_booking_service(self):
        response = self.app.post('/api/user_service/register',
                                 data=json.dumps(dict(email="abc@gmail.com", password="qwerty", name="ABC")),
                                 follow_redirects=True)
        self.assertEqual(response.status_code, 201)

        response = self.app.post('/api/user_service/register',
                                 data=json.dumps(dict(email="xyz@gmail.com", password="qwerty", name="XYZ")),
                                 follow_redirects=True)
        self.assertEqual(response.status_code, 201)

        response = self.app.post('/api/user_service/login',
                                 data=json.dumps(dict(email="abc@gmail.com", password="qwerty")),
                                 follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        jwt = response.json['token']

        response = self.app.post('/api/user_service/mark_available_slots',
                                 data=json.dumps(dict(availability_date="2020-04-05",
                                                      available_slots=[
                                                          {"start_time": "19:00:00", "end_time": "20:00:00"}])),
                                 headers={'Authorization': jwt},
                                 follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.post('/api/user_service/login',
                                 data=json.dumps(dict(email="abc@gmail.com", password="qwerty")),
                                 follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        jwt = response.json['token']               # new token

        response = self.app.get(
            '/api/user_service/check_available_slots?email=abc@gmail.com&date=2020-04-05',
            headers={'Authorization': jwt}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [{"start_time": "19:00:00", "end_time": "20:00:00"}])

        response = self.app.post('/api/user_service/book_slot',
                                 data=json.dumps(dict(date="2020-04-05",
                                                      slot={"start_time": "19:00:00", "end_time": "20:00:00"},
                                                      email='abc@gmail.com',
                                                      summary="Meet up", description="Hello")),
                                 headers={'Authorization': jwt},
                                 follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Tried to book an unavailable slot
        response = self.app.post('/api/user_service/book_slot',
                                 data=json.dumps(dict(date="2020-04-05",
                                                      slot={"start_time": "13:00:00", "end_time": "14:00:00"},
                                                      email='abc@gmail.com')),
                                 headers={'Authorization': jwt},
                                 follow_redirects=True)
        self.assertEqual(response.status_code, 400)

        response = self.app.post('/api/user_service/book_slot',
                                 data=json.dumps(dict(date="2020-04-05",
                                                      slot={"start_time": "19:00:00", "end_time": "20:00:00"},
                                                      email='abc@gmail.com')),
                                 headers={'Authorization': jwt},
                                 follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json,{'message': 'Please enter email,date,slot,summary,description for processing'})


if __name__ == "__main__":
    unittest.main()
