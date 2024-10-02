# Import sqlalchemy and marshmallow
from init import db, ma

# Import mashmallow modules for validation of fields, data clean up and defining schemas
from marshmallow.exceptions import ValidationError
from marshmallow import fields, post_dump, pre_load
from marshmallow.validate import Length, Range

# Constant variable for max inputs
MAX_RANGE = 999999
# Constant variable for valid inputs
VALID_INPUTS = ("sets", "reps", "weight", "distance_km", "distance_m", "hours", "minutes", "seconds", "note")

# Table for Routine Exercises
class RoutineExercise(db.Model):
    # Name of table
    __tablename__ = "routine_exercises"

    # Attributes of table
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

    # Foreign Keys
    routine_id = db.Column(db.Integer, db.ForeignKey("routines.id"), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercises.id"), nullable=False)

    # Define relationships with exercise and routine table
    exercise = db.relationship("Exercise", back_populates="routine_exercises")
    routine = db.relationship("Routine", back_populates="routine_exercises")

# Reason for validation is to ensure that user inputs are not too long. Also to ensure particular attributes do not exceed certain values (e.g. minutes and seconds should not exceed 59).
# Also include nesting for retrieving the associated exercise name for the exercise_id. This is retrieved by accessing the exercise relationship.
class RoutineExerciseSchema(ma.Schema):
    sets = fields.Integer(validate=Range(max=MAX_RANGE))
    reps = fields.Integer(validate=Range(max=MAX_RANGE))
    weight = fields.Integer(validate=Range(max=MAX_RANGE))
    distance_km = fields.Integer(validate=Range(max=MAX_RANGE))
    distance_m = fields.Integer(validate=Range(max=999)) 
    hours = fields.Integer(validate=Range(max=MAX_RANGE))
    minutes = fields.Integer(validate=Range(max=59))
    seconds = fields.Integer(validate=Range(max=59))
    note = fields.String(validate=Length(max=255))
    # To allow exercise name to appear when routine exercises are called/input into JSON response
    exercise_name = fields.Nested("ExerciseSchema", only=["exercise_name"], attribute="exercise")


    # Pre-load decorator to perform validation on user input. Raise a validation error if no attributes provided to avoid empty routine_exercises. 
    @pre_load
    def validate_attributes(self, data, **kwargs):
        # Create a list to hold valid attributes
        valid_attributes = []
        
        # Loop through each attribute provided in the data by the user
        for attribute, value in data.items():
            # Check if the attribute is valid and contains a value
            if attribute in VALID_INPUTS and value is not None and value != "":
                valid_attributes.append(attribute)
        
        # If valid attributes is empty, raise an error
        if not valid_attributes:
            raise ValidationError(f"Please provide at least one of the following: {', '.join(VALID_INPUTS)}")
        
        # If valid attributes exist, return the data
        return data

    # Using @post_dump decorator to apply function which removes fields with None values before providing output to user. This ensures that only relevant data is displayed when a routine exercise is dumped. 
    @post_dump
    def remove_none_values(self, data, **kwargs):
        # Initialise empty dictionary to return to user
        response_for_user = {} 
        # For each key-value pair in data
        for key, value in data.items(): 
            # If value contains data
            if value is not None: 
                # Transfer key value pair into response for user
                response_for_user[key] = value
        # Return cleaned data
        return response_for_user 

    # Confirms which fields can be visible
    class Meta:
        fields = ("id", *VALID_INPUTS, "exercise_name", "exercise_id")

# to hand a single routine exercise object
routine_exercise_schema = RoutineExerciseSchema()
# to hand a list of routine exercise objects
routine_exercises_schema = RoutineExerciseSchema(many=True)