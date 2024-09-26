from init import db, ma
from sqlalchemy import func

from marshmallow import fields, Method
from marshmallow.validate import OneOf

VALID_TARGET = ("Full Body", "Upper Body", "Lower Body", "Push Workout", "Pull Workout", "Chest", "Shoulders", "Back", "Legs", "Arms", "Core", "Cardio")

class Routine(db.Model):
    # name of table
    __tablename__ = "routines"

    # attributes of table
    id = db.Column(db.Integer, primary_key=True)
    routine_title = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    target = db.Column(db.String, nullable=False)
    public = db.Column(db.Boolean, default=False, nullable=False)
    created = db.Column(db.Date, server_default=func.current_date(), nullable=False)
    # Foreign Key (users.id = tablename.primarykey attribute)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    user = db.relationship("User", back_populates="routines")
    routine_exercises = db.relationship("RoutineExercise", back_populates="routine", cascade="all, delete")
    likes = db.relationship("Like", back_populates="routine", cascade="all, delete")

    def likes_count(self):
        return len(self.likes)

class RoutineSchema(ma.Schema):
    target = fields.String(validate=OneOf(VALID_TARGET))
    created_by = fields.Nested("UserSchema", only=["username"], attribute="user")
    routine_exercises = fields.List(fields.Nested('RoutineExerciseSchema'))

    likes_count = ma.Method("get_likes_count")

    def get_likes_count(self, obj):
        return obj.likes_count()

    class Meta:
        fields = ("id", "routine_title", "description", "target", "public", "created", "created_by", "routine_exercises", "likes_count")

# to handle a single user object
routine_schema = RoutineSchema()
# to hand a list of user objects
routines_schema = RoutineSchema(many=True)