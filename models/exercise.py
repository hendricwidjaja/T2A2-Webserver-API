# Import sqlalchemy and marshmallow
from init import db, ma

# Import mashmallow modules for validation of fields and defining schemas
from marshmallow import fields
from marshmallow.validate import OneOf, Length

# Constant variable for valid "body_parts" to be trained to allow for easier tracking and updating of valid "body_parts"
VALID_BODYPARTS = ("Chest", "Shoulders", "Back", "Legs", "Triceps", "Biceps", "Core", "Cardio")

# Table for Exercises
class Exercise(db.Model):
    # Name of table
    __tablename__ = "exercises"

    # Attributes of table
    id = db.Column(db.Integer, primary_key=True)
    exercise_name = db.Column(db.String, nullable=False, unique=True)
    description = db.Column(db.String)
    body_part = db.Column(db.String, nullable=False)

    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
   
    # Define relationships with user & routine_exercise table
    user = db.relationship("User", back_populates="exercises")
    routine_exercises = db.relationship("RoutineExercise", back_populates="exercise")

class ExerciseSchema(ma.Schema):
    # Reason for validation is to ensure any required fields are included in user requests. Also ensures inputs are not too larger. Nested values are also included (e.g. created_by) to allow more information to users when exercises are included in responses.
    exercise_name = fields.String(required=True, validate=Length(max=50, min=1))
    description = fields.String(validate=Length(max=255))
    body_part = fields.String(required=True, validate=OneOf(VALID_BODYPARTS))
    created_by = fields.Nested('UserSchema', only=["username"], attribute="user")

    # Confirms which fields can be visible
    class Meta:
        fields = ("id", "exercise_name", "description", "body_part", "created_by")

# to hand a single exercise object
exercise_schema = ExerciseSchema()
# to hand a list of exercise objects
exercises_schema = ExerciseSchema(many=True)