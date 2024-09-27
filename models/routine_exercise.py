from init import db, ma

from marshmallow import pre_dump

class RoutineExercise(db.Model):
    # name of table
    __tablename__ = "routine_exercises"

    # attributes of table
    id = db.Column(db.Integer, primary_key=True)
    sets = db.Column(db.Integer)
    reps = db.Column(db.Integer)
    weight = db.Column(db.Integer)
    distance_km = db.Column(db.Float)
    minutes = db.Column(db.Integer)
    seconds = db.Column(db.Integer)
    note = db.Column(db.String)

    # Foreign Key (users.id = tablename.primarykey attribute)
    routine_id = db.Column(db.Integer, db.ForeignKey("routines.id"), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercises.id"), nullable=False)

    # Define relationships
    exercise = db.relationship("Exercise", back_populates="routine_exercises")
    routine = db.relationship("Routine", back_populates="routine_exercises")

class RoutineExerciseSchema(ma.Schema):

    # Using @pre_dump decorator to apply function which rounds value for distance_km to 2 decimal places

    # Using @pre_dump decorator to apply function which removes fields with None values before providing output to user
    @pre_dump
    def remove_empty_attributes(self, data, **kwargs):
        attributes_with_values = {}
        for key, value in data.__dict__.items():
            if value is not None:
                attributes_with_values[key] = value
  
        return attributes_with_values

    class Meta:
        fields = ("id", "sets", "reps", "weight", "distance_km", "minutes", "seconds", "note")

# to handle a single user object
routine_exercise_schema = RoutineExerciseSchema()
# to hand a list of user objects
routine_exercises_schema = RoutineExerciseSchema(many=True)