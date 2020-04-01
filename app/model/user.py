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
