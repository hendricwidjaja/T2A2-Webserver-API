from init import db, ma
from sqlalchemy import func

from marshmallow import fields

class RoutineExercise(db.Model):
    # name of table
    __tablename__ = "routine_exercises"

    # attributes of table
    id = db.Column(db.Integer, primary_key=True)
    sets = db.Column(db.Integer)
    reps = db.Column(db.Integer)
    weight = db.Column(db.Integer)
    duration = db.Column(db.Interval)
    note = db.Column(db.String)

    # Foreign Key (users.id = tablename.primarykey attribute)
    routine_id = db.Column(db.Integer, db.ForeignKey("routines.id"), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercises.id"), nullable=False)

    # Define relationships
    exercise = db.relationship("Exercise", back_populates="routine_exercises")
    routine = db.relationship("Routines", back_populates="routine_exercises")

class RoutineExerciseSchema(ma.Schema):

    class Meta:
        fields = ("id", "sets", "reps", "weight", "duration", "note")

# to handle a single user object
routine_exercise_schema = RoutineExerciseSchema()
# to hand a list of user objects
routine_exercises_schema = RoutineExerciseSchema(many=True)