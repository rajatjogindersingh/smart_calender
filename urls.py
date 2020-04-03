from app.api.user_service import UserRegistrationService, UserLoginService,UserAvailabilityService, CheckUserSlot, \
    BookUserSlot


def bind_url(api):
    api.add_resource(UserRegistrationService, '/api/user_service/register')
    api.add_resource(UserLoginService, '/api/user_service/login')
    api.add_resource(UserAvailabilityService, '/api/user_service/mark_available_slots')
    api.add_resource(CheckUserSlot, '/api/user_service/check_available_slots')
    api.add_resource(BookUserSlot, '/api/user_service/book_slot')