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

        response = self.app.post('/api/user_service/login',
                                 data=json.dumps(dict(email="abc@gmail.com", password="qwerty")),
                                 follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.get('/api/user_service/check_available_slots',
                                follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message'], 'Authorization token missing')

        response = self.app.get('/api/user_service/check_available_slots', headers={'Authorization': "dummy"},
                                follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message'], 'Invalid token. Please log in again.')


if __name__ == "__main__":
    unittest.main()
