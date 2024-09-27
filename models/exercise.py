from init import db, ma

from marshmallow import fields
from marshmallow.validate import OneOf, Length

VALID_BODYPARTS = ("Chest", "Shoulders", "Back", "Legs", "Triceps", "Biceps", "Core", "Cardio")

class Exercise(db.Model):
    # name of table
    __tablename__ = "exercises"

    # attributes of table
    id = db.Column(db.Integer, primary_key=True)
    exercise_name = db.Column(db.String, nullable=False, unique=True)
    description = db.Column(db.String)
    body_part = db.Column(db.String)
    # Foreign Key (users.id = tablename.primarykey attribute)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    created_by = db.relationship("User", back_populates="exercises")
    routine_exercises = db.relationship("RoutineExercise", back_populates="exercise")

class ExerciseSchema(ma.Schema):
    exercise_name = fields.String(required=True, validate=Length(max=50, min=1))
    description = fields.String(validate=Length(max=255))
    body_part = fields.String(required=True, validate=OneOf(VALID_BODYPARTS))
    created_by = fields.Nested('UserSchema', only=["username"])

    class Meta:
        fields = ("id", "exercise_name", "description", "body_part", "created_by")

# to handle a single user object
exercise_schema = ExerciseSchema()
# to hand a list of user objects
exercises_schema = ExerciseSchema(many=True)