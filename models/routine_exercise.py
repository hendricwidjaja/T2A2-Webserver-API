from init import db, ma

from marshmallow.exceptions import ValidationError
from marshmallow import fields, pre_dump, pre_load
from marshmallow.validate import Length, Range
from marshmallow import pre_dump

# Constant variable for max inputs
MAX_RANGE = 999999
# Constant variable for valid inputs
VALID_INPUTS = ("sets", "reps", "weight", "distance_km", "distance_m", "hours", "minutes", "seconds", "note")

class RoutineExercise(db.Model):
    # name of table
    __tablename__ = "routine_exercises"

    # attributes of table
    id = db.Column(db.Integer, primary_key=True)
    sets = db.Column(db.Integer)
    reps = db.Column(db.Integer)
    weight = db.Column(db.Integer)
    distance_km = db.Column(db.Integer)
    distance_m = db.Column(db.Integer)
    hours = db.Column(db.Integer)
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
    sets = fields.Integer(validate=Range(max=MAX_RANGE))
    reps = fields.Integer(validate=Range(max=MAX_RANGE))
    weight = fields.Integer(validate=Range(max=MAX_RANGE))
    distance_km = fields.Integer(validate=Range(max=MAX_RANGE))
    distance_m = fields.Integer(validate=Range(max=MAX_RANGE)) 
    hours = fields.Integer(validate=Range(max=MAX_RANGE))
    minutes = fields.Integer(validate=Range(max=MAX_RANGE))
    seconds = fields.Integer(validate=Range(max=MAX_RANGE))
    note = fields.String(validate=Length(max=255))

    # Pre-load decorator to perform validation on user input. Raise a validation error if no attributes provided to avoid empty routine_exercises
    @pre_load
    def validate_attributes(self, data, **kwargs):
        # Create a list to hold valid attributes
        valid_attributes = []
        
        # Loop through each attribute provided in the data by the user
        for attribute in data:
            # If the attribute is one of the VALID_INPUTS and user has provided a value
            if attribute in VALID_INPUTS and data[attribute]:
                # Append attribute to list of valid_attributes
                valid_attributes.append(attribute)
        
        # If valid attributes is empty, raise an error
        if not valid_attributes:
            raise ValidationError(f"Please provide at least one of the following: {', '.join(VALID_INPUTS)}")
        
        # If valid attributes exist, return the data
        return data

    # Using @pre_dump decorator to apply function which removes fields with None values before providing output to user
    @pre_dump
    def filter_empty_attributes(self, data, **kwargs):
        attributes_with_values = {}
        for key, value in data.__dict__.items():
            if value is not None:
                attributes_with_values[key] = value
  
        return attributes_with_values

    class Meta:
        fields = ("id", *VALID_INPUTS)

# to handle a single user object
routine_exercise_schema = RoutineExerciseSchema()
# to hand a list of user objects
routine_exercises_schema = RoutineExerciseSchema(many=True)