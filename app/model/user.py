import mongoengine as db
import marshmallow_mongoengine as ma


class User(db.Document):
    name = db.StringField(null=False, min_length=3, required=True)
    email = db.EmailField(required=True)
    phone_no = db.StringField(min_length=10, max_length=10)
    password = db.StringField(required=True, null=False)


class UserSchema(ma.ModelSchema):
    class Meta:
        model = User

    password = ma.fields.String(load_only=True)


class Slots(db.EmbeddedDocument):
    start_time = db.DateTimeField(required=True)
    end_time = db.DateTimeField(required=True)


class SlotsSchema(ma.ModelSchema):
    class Meta:
        model = Slots

    start_time = ma.fields.Method(serialize="change_start_datetime_format")
    end_time = ma.fields.Method(serialize="change_end_datetime_format")

    def change_start_datetime_format(self, obj):
        date_time = (obj.start_time).time()
        return str(date_time)

    def change_end_datetime_format(self, obj):
        date_time = (obj.end_time).time()
        return str(date_time)


class UserAvailableSlots(db.Document):
    user_id = db.ReferenceField(User, required=True)
    availability_date = db.DateTimeField(required=True, unique_with='user_id')
    available_slots = db.EmbeddedDocumentListField(Slots)


class UserAvailableSlotsSchema(ma.ModelSchema):
    class Meta:
        model = UserAvailableSlots
