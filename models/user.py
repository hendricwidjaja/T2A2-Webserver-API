from init import db, ma

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

    exercises = db.relationship("Exercise", back_populates="user")

class UserSchema(ma.Schema):
    class Meta:
        fields = ("id", "username", "firstname", "lastname", "email", "password")

# to handle a single user object
user_schema = UserSchema(exclude=["password"])
# to hand a list of user objects
users_schema = UserSchema(many=True, exclude=["password"])