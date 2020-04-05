class SmartCalenderConfig:
    APP_NAME = "smart_calender"
    HOST = 'mongodb+srv://{}:{}@cluster0-2cppb.mongodb.net/calender?retryWrites=true&w=majority'


class SmartCalenderTestConfig(SmartCalenderConfig):
    HOST = 'mongodb+srv://{}:{}@cluster0-2cppb.mongodb.net/test_calender?retryWrites=true&w=majority'
