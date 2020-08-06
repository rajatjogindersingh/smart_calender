# Smart Calender

Using Flask to build Restful API's for Smart Calender. Using these API's you can register, login, check ,mark and book availability depending on schedule of other person. Also have integrated with JWT token based Authentication.

# Setup
The pre-requisite for this is Python 3.6 or above should be available in your machine.
 
To setup these application in your local environment (Windows), you can following commands - 
```
python3 -m venv virtual_env
virtual_env/Scripts/activate
pip install -r requirements.txt
```
These commands will make a virtual environment and install all the required libraries there.

Then we need to setup the environment variables which the application will need - 
```
set flask_app = main
set flask_env = development
set db_user_name = <name>
set db_password = <password>
set secret_key = some-randon-string
```
Note: Since for development I am using Remote Mongo DB we need to create an account there and get account details.

To set up integration with Google Calender you need to enable support from [Google Calender Quickstart](https://developers.google.com/calendar/quickstart/python). It will give you a JSON file and from those you need to set the variables below-
```
set client_id = some-unique-id
set project_id = some-unique-id
set redirect_uri = url + api/register_credentials
``` 

While Deploying on any of the cloud servers we have to take care of all these variables.

# Running the Test
The unit test cases are available in `unit_test/`.

To run unit test cases and check it's coverage, after setting environment variables following command can be used-
```
coverage run -m unittest unit_test\test_setup.py
coverage report -m
``` 

# Running the application
For running the application you just need to type-
```
flask run
```
To test the application you can use the postman collection given in the [github](https://github.com/rajatjogindersingh/smart_calender).

The Procfile given is to handle deployment on Heroku and as per the cloud providers it needs to be updated.
