from init import db, ma

from marshmallow import fields
from marshmallow.validate import Length, Regexp 

class User(db.Model):
    # name of table
    __tablename__ = "users"

    # attributes of table
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    firstname = db.Column(db.String)
    lastname = db.Column(db.String)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    exercises = db.relationship("Exercise", back_populates="created_by")
    routines = db.relationship("Routine", back_populates="user")
    likes = db.relationship("Like", back_populates="user", cascade="all, delete")

class UserSchema(ma.Schema):
    username = fields.String(required=True, validate=Regexp(r"^(?=.{4,20}$)(?!.*[_.]{2})[a-zA-Z0-9._]+$", error="Username must be 4-20 characters long (no spaces). It can only contain letters, digits, periods(.) and or underscores(_). Consecutive periods or underscores are not permitted."))
    email = fields.String(required=True, validate=Regexp(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", error="Invalid Email Format"))
    password = fields.String(required=True, validate=Regexp(r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{6,20}$", error="Password must be 6-20 characters long and must include at least one letter (a-z, A-Z), one number (0-9) & one special character (@$!%*#?&)"))
    firstname = fields.String(validate=Length(max=50), error="Cannot exceed 50 characters")
    lastname = fields.String(validate=Length(max=50), error="Cannot exceed 50 characters")

    class Meta:
        fields = ("id", "username", "firstname", "lastname", "email", "is_admin", "password")

# to handle a single user object
user_schema = UserSchema(exclude=["password"])
# to hand a list of user objects
users_schema = UserSchema(many=True, exclude=["password"])