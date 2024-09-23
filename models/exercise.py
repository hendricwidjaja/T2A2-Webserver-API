from init import db, ma
from sqlalchemy import func

from marshmallow import fields

class Exercise(db.Model):
    # name of table
    __tablename__ = "exercises"

    # attributes of table
    id = db.Column(db.Integer, primary_key=True)
    exercise_name = db.Column(db.String, nullable=False, unique=True)
    description = db.Column(db.String)
    public = db.Column(db.Boolean, default=False, nullable=False)
    created = db.Column(db.Date, server_default=func.current_date(), nullable=False)
    # Foreign Key (users.id = tablename.primarykey attribute)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    user = db.relationship("User", back_populates="exercises")

class ExerciseSchema(ma.Schema):
    created_by = fields.Nested("UserSchema", only=["username"], attribute="user")

    class Meta:
        fields = ("id", "exercise_name", "description", "public", "created", "created_by")

# to handle a single user object
exercise_schema = ExerciseSchema()
# to hand a list of user objects
exercises_schema = ExerciseSchema(many=True)