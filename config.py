class SmartCalenderConfig:
    APP_NAME = "smart_calender"
    HOST = 'mongodb+srv://{}:{}@cluster0-2cppb.mongodb.net/calender?retryWrites=true&w=majority'
    GOOGLE_JSON = {
                    "web": {
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs"}
                }


class SmartCalenderTestConfig(SmartCalenderConfig):
    HOST = 'mongodb+srv://{}:{}@cluster0-2cppb.mongodb.net/test_calender?retryWrites=true&w=majority'
