from init import db, ma

from marshmallow import fields
from marshmallow.validate import OneOf

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

    user = db.relationship("User", back_populates="exercises")
    routine_exercises = db.relationship("RoutineExercise", back_populates="exercise")

class ExerciseSchema(ma.Schema):
    body_part = fields.String(required=False, validate=OneOf(VALID_BODYPARTS))

    class Meta:
        fields = ("id", "exercise_name", "description", "body_part")

# to handle a single user object
exercise_schema = ExerciseSchema()
# to hand a list of user objects
exercises_schema = ExerciseSchema(many=True)