# Import sqlalchemy and marshmallow
from init import db, ma

# Import marshmallow modules for validation of fields
from marshmallow import fields
from marshmallow.validate import Length, Regexp 

# Table for User Model
class User(db.Model):
    # Name of table
    __tablename__ = "users"

    # Attributes of table
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    firstname = db.Column(db.String)
    lastname = db.Column(db.String)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    # Define relationships with exercise, routine and like tables
    exercises = db.relationship("Exercise", back_populates="user")
    routines = db.relationship("Routine", back_populates="user")
    # All associated likes belonging to a user are to be deleted when user is deleted.
    likes = db.relationship("Like", back_populates="user", cascade="all, delete")

class UserSchema(ma.Schema):
    # Reason for validation are as per error messages provided. Generally ensure that any inputs from the user are not too long and are easy to read within the app. E.g. prevent multiple consecutive underscores in username, etc.
    username = fields.String(required=True, validate=Regexp(r"^(?=.{4,20}$)(?!.*[_.]{2})[a-zA-Z0-9._]+$", error="Username must be 4-20 characters long (no spaces). It can only contain letters, digits, periods(.) and or underscores(_). Consecutive periods or underscores are not permitted."))
    email = fields.String(required=True, validate=Regexp(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", error="Invalid Email Format"))
    password = fields.String(required=True, validate=Regexp(r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{6,20}$", error="Password must be 6-20 characters long and must include at least one letter (a-z, A-Z), one number (0-9) & one special character (@$!%*#?&)"))
    firstname = fields.String(required=False, validate=Length(max=50, min=1), error="Cannot exceed 50 characters")
    lastname = fields.String(required=False, validate=Length(max=50, min=1), error="Cannot exceed 50 characters")

    # Confirms which fields can be visible
    class Meta:
        fields = ("id", "username", "firstname", "lastname", "email", "is_admin", "password")

# to hand a single user object (excludes password from being dumped to users)
user_schema = UserSchema(exclude=["password"])
# to hand a list of user objects (excludes password from being dumped to users)
users_schema = UserSchema(many=True, exclude=["password"])