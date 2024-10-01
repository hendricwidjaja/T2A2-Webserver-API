# Import sqlalchemy and marshmallow
from init import db, ma

# Import func method for database methods (timestamp)
from sqlalchemy import func

# Import mashmallow modules for validation of fields and defining schemas
from marshmallow import fields, validates
from marshmallow.validate import OneOf, Length

# Constant variable for valid "target" muscle groups to be trained to allow for easier tracking and updating of valid "targets"
VALID_TARGET = ("Full-Body", "Upper-Body", "Lower-Body", "Push-Workout", "Pull-Workout", "Chest", "Shoulders", "Back", "Legs", "Arms", "Core", "Cardio")

# Table for Routine Model
class Routine(db.Model):
    # Name of table
    __tablename__ = "routines"

    # Attributes of table
    id = db.Column(db.Integer, primary_key=True)
    routine_title = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    target = db.Column(db.String, nullable=False)
    public = db.Column(db.Boolean, default=False, nullable=False)
    created = db.Column(db.DateTime, server_default=func.current_timestamp(), nullable=False)

    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # Define relationships with user, routine exercises and likes table. Delete all associated routine exercises and likes when routine is deleted.
    # Note: Routine exercises associated with public routines will be kept by transferring ownership to "DELETED ACCOUNT" account if user chooses to not delete public routines when deleting account (see logic for delete user in auth_controller.py)
    user = db.relationship("User", back_populates="routines")
    routine_exercises = db.relationship("RoutineExercise", back_populates="routine", cascade="all, delete")
    likes = db.relationship("Like", back_populates="routine", cascade="all, delete")

    # Function to count how many users have liked the specific instance of a routine. Accesses relationship with Like model via 'likes'.
    def count_likes(self):
        return len(self.likes)

class RoutineSchema(ma.Schema):
    # Reason for validation are as per error messages provided. 
    # Generally ensure user inputs are not too long and any required inputs are provided by user.
    # Also used for formatting (e.g. timestamp) and allowing nesting of data from other tables (e.g. created_by & routine methods).
    # Also incorporate fields.Method to call function (get_likes_count) which calculates the amount of likes for a particular routine instance which can then be seen by user when routine is dumped. 
    routine_title = fields.String(validate=Length(max=50), error="Routine title cannot exceed 50 characters.")
    description = fields.String(validate=Length(max=255), error="You have exceeded the 255 character count limit.")
    target = fields.String(validate=OneOf(VALID_TARGET))
    public = fields.Boolean(missing=False)
    created = fields.Method("format_timestamp")
    created_by = fields.Nested("UserSchema", only=["username"], attribute="user")
    routine_exercises = fields.List(fields.Nested('RoutineExerciseSchema'), attribute="routine_exercises")
    # Defines the "likes_count" field as an integer which is equal to the result of the "count_likes" method in the Routine model.
    likes_count = fields.Method("get_likes_count")

    # Method to format the created timestamp
    def format_timestamp(self, routine):
        return routine.created.strftime("%Y-%m-%d %H:%M:%S")

    # Method to call count_likes() on routine instance
    def get_likes_count(self, routine):
        return routine.count_likes()

    # Create validation for public attribute
    @validates("public")
    def validates_public(self, value):
        # If value is not boolean (true or false)
        if not isinstance(value, bool):
            raise ValueError("Could not recognise the value for 'public'. Please insert either true or false.")

    # Confirms which fields can be visible
    class Meta:
        fields = ("id", "routine_title", "description", "target", "public", "created", "created_by", "routine_exercises", "likes_count")

# to hand a single routine object
routine_schema = RoutineSchema()
# to hand a list of routine objects
routines_schema = RoutineSchema(many=True)