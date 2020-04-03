import mongoengine as db
import marshmallow_mongoengine as ma
import datetime


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
    user = db.ReferenceField(User, default=None)
    booked_by = db.ReferenceField(User)


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
    user = db.ReferenceField(User, required=True)
    availability_date = db.DateTimeField(required=True, unique_with='user')
    available_slots = db.EmbeddedDocumentListField(Slots)

    def save(self, force_insert=False, validate=True, clean=True,
             write_concern=None, cascade=None, cascade_kwargs=None,
             _refs=None, save_condition=None, signal_kwargs=None, **kwargs):

        curr = datetime.datetime.now()
        if not getattr(self, id) and self.availability_date.date() < curr.date():
            raise Exception('Expired availability_date')

        if getattr(self, 'available_slots') and self.available_slots:
            for slot in self.available_slots:
                if slot.start_time >= slot.end_time:
                    raise Exception('Start time has to be less than end time')

        super(UserAvailableSlots, self).save()


class UserAvailableSlotsSchema(ma.ModelSchema):
    class Meta:
        model = UserAvailableSlots
