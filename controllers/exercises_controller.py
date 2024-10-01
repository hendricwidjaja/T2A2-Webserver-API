from flask import Blueprint, request

from models.exercise import Exercise, exercise_schema, exercises_schema, VALID_BODYPARTS
from models.user import User
from models.routine_exercise import RoutineExercise
from init import db
from utils import auth_as_admin_or_owner, ADMIN_EMAIL, user_is_admin

from sqlalchemy.exc import IntegrityError
from psycopg2 import errorcodes
from flask_jwt_extended import jwt_required, get_jwt_identity


exercises_bp = Blueprint("exercises", __name__, url_prefix="/exercises")


# /exercises - GET - Fetch all exercises 
@exercises_bp.route("/", methods=["GET"])
def get_all_exercises():
    # Fetch all exercises in database (order in alphabetical order)
    stmt = db.select(Exercise).order_by(Exercise.exercise_name.asc())

    # Execute statement & return as list
    exercises = db.session.scalars(stmt).all()

    # Check if any exercises exist
    if exercises:
        # Return list of exercises
        return exercises_schema.dump(exercises), 200
    # Else:
    else:
        # Return error message advising no exercises available
        return {"error": f"There are currently no exercises that could be found. We recommend you create one!"}, 404

# /exercises/body-part/<body_part> - GET - Fetch all exercises for a specific body_part
@exercises_bp.route("/body-part/<body_part>", methods=["GET"]) 
def get_body_part_exercises(body_part):
    # Fetch all exercises from database with filter for specified body_part mentioned in URL. Capitalise the first letter when filtering to match VALID_BODYPARTS, then order in alphabetical order
    stmt = db.select(Exercise).filter_by(body_part=body_part.capitalize()).order_by(Exercise.exercise_name.asc())

    # Execute the query and return as a list
    exercises = db.session.scalars(stmt).all()

    # Check if any exercises exist
    if exercises:
        # If exists, return exercises to user
        return exercises_schema.dump(exercises), 200
    # Else:
    else:
        # Return error message
        return {"error": f"There are currently no '{body_part}' exercises that could be found. Our current body part categories include {VALID_BODYPARTS}."}, 404


#/exercises/id/<int:exercise_id> - GET - Fetch a specific exercise by ID
@exercises_bp.route("/id/<int:exercise_id>", methods=["GET"])
def get_specific_exercise(exercise_id):
    # Query the database for exercises that match exercise_id in URL
    stmt = db.select(Exercise).filter_by(id=exercise_id)

    # Execute the query
    exercise = db.session.scalar(stmt)

    # Check if any exercises exist
    if exercise:
        # If exists, return exercise to user
        return exercise_schema.dump(exercise), 200
    # Else: 
    else:
        # Return an error message stating the exercise does not exist
        return {"error": f"Exercise with id '{exercise_id}' - does not exist."}, 404


#/exercises/user/<user_id> - GET - Fetch all exercises created by a user.
@exercises_bp.route("/user/<int:user_id>/", methods=["GET"])
def get_user_exercises(user_id):
    # Check if user exists:
    stmt = db.select(User).filter_by(id=user_id)
    user_exists = db.session.scalar(stmt)

    # If user exists:
    if user_exists:
        # Fetch exercises while filtering only by user_id
        stmt = db.select(Exercise).filter_by(user_id=user_id)
        # Execute the query and return as a list
        exercises = db.session.scalars(stmt).all()
        # If exercises exist:
        if exercises:
            # Return exercises list to user
            return exercises_schema.dump(exercises), 200
        # Else:
        else:
            return {"error": f"We could not find any exercises created by '{user_exists.username}' with ID {user_id}."}, 404
    # If user does not exist    
    else:
        # Return an error message
        return {"error": f"User with ID '{user_id}' not found."}, 404


#/exercises/user/<user_id> - GET - Fetch a filtered list of exercises created by a user. Filter by query parameter (e.g. ?body_part=Chest)
@exercises_bp.route("/user/<int:user_id>/filter", methods=["GET"])
def filter_user_exercises(user_id):
    # Fetch body part from query paramater if provided
    body_part = request.args.get("body_part")

    # INITIAL STATEMENT - Fetch exercises while filtering only by user_id
    stmt = db.select(Exercise).filter_by(user_id=user_id)

    # If body_part was provided
    if body_part:
        # Validate user input against VALID_BODYPARTS (capitalise query for ease)
        if body_part.capitalize() in VALID_BODYPARTS:
            # Include validated body_part filter + (capitalised) to INITIAL STATEMENT
            stmt = stmt.filter_by(user_id=user_id, body_part=body_part.capitalize())
        # Else:
        else:
            # Return an error message with prompt of valid body parts
            return {"error": f"'{body_part}' is an invalid body_part. Please search by {', '.join(VALID_BODYPARTS)}"}, 400

    # If body part filter is not provided. Execute the query and return as a list
    exercises = db.session.scalars(stmt).all()

    # If exercises exist:
    if exercises:
        # Return exercises list to user
        return exercises_schema.dump(exercises), 200
    else:
        # Fetch username from database for informational error message
        user_stmt = db.select(User).filter_by(id=user_id)
        user_exists = db.session.scalar(user_stmt)
        # If user exists, fetch the user's username
        if user_exists:
            username = user_exists.username
        # Else:
        else:
            # Return an error message
            return {"error": f"User with ID '{user_id}' not found."}, 404
        # Return error message advising no exercise could be found
        return {"error": f"We could not find any {body_part} exercises created by '{username}'."}, 404


# /exercises/ - POST - create an exercise
@exercises_bp.route("/", methods=["POST"])
@jwt_required() # Check if user is logged in using jwt_required
def create_exercise():
    try:
        # Get the details of the new exercise from the body of the request
        body_data = exercise_schema.load(request.get_json())

        # Check if the provided exercise name already exists in the list of exercises
        exercise_name = body_data.get("exercise_name")
        exist_exer_stmt = db.select(Exercise).filter_by(exercise_name=exercise_name)
        existing_exercise = db.session.scalar(exist_exer_stmt)
        # If the exercise already exists, send an error message
        if existing_exercise: 
            return {"error": f"An exercise with the name '{existing_exercise.exercise_name}' already exists. Please choose a different name."}, 400

        # Populate new entry into exercise table accordingly
        exercise = Exercise(
            user_id = get_jwt_identity(),
            exercise_name = body_data.get("exercise_name"),
            description = body_data.get("description"),
            body_part = body_data.get("body_part"),
        )
        # Add and commit to the DB
        db.session.add(exercise)
        db.session.commit()

        # Successfully created response message
        return exercise_schema.dump(exercise), 201
    
    # Error handling & rollback
    except IntegrityError as err:
        db.session.rollback()
        return {"error": f"An unexpected error occured when trying to add an exercise: {err}"}, 400


# /exercises/<int:exercise_id> - DELETE - Delete an exercise (user must have created the exercise)
@exercises_bp.route("/<int:exercise_id>", methods=["DELETE"])
@jwt_required() # Check if user is logged in using jwt_required
@auth_as_admin_or_owner # Validate if the exercise id in the URL exists and if the logged in user has authority to delete (either as owner or admin)
def delete_exercise(exercise_id):
    # Check if exercise appears in a user's routine. 
    exer_is_used_stmt = db.select(RoutineExercise).filter_by(exercise_id=exercise_id)
    exercise_is_used = db.session.scalars(exer_is_used_stmt).first()

    # If exists in a user's routine and user is not admin (owner)
    if exercise_is_used and not user_is_admin():
        # return error
        return {"error": f"Exercise with 'ID - {exercise_id}' is being used in existing routine/s. Delete has been aborted. If action is still required, email admin: {ADMIN_EMAIL}"}, 409

    # If exercise is not being used, fetch the exercise the user is requesting to delete from the database
    stmt = db.select(Exercise).filter_by(id=exercise_id)
    exercise = db.session.scalar(stmt)

    # If it doesn't exist in a user's routine, delete the exercise from the database
    db.session.delete(exercise)
    db.session.commit()
    # Return an acknowledgement message
    return {"message": f"Exercise with 'ID - {exercise_id}' has been successfully deleted."}, 200


# /exercises/<int:exercise_id> - PUT/PATCH - Update an exercise
@exercises_bp.route("/<int:exercise_id>", methods=["PUT", "PATCH"])
@jwt_required() # Check if user is logged in using jwt_required
@auth_as_admin_or_owner # Validate if the exercise id in the URL exists and if the logged in user has authority to update (either as owner or admin)
def update_exercise(exercise_id):
    try:
        # Fetch data from body of request
        body_data = exercise_schema.load(request.get_json(), partial=True)

        # Check if exercise appears in a user's routine
        exer_is_used_stmt = db.select(RoutineExercise).filter_by(exercise_id=exercise_id)
        exercise_is_used = db.session.scalars(exer_is_used_stmt).first()

        # If exists in a user's routine and user is not admin (owner)
        if exercise_is_used and not user_is_admin():
            # return error
            return {"error": f"Exercise with 'ID - {exercise_id}' is being used in an existing routine/s. Update has been aborted. If action is still required, email admin: {ADMIN_EMAIL}"}, 409

        # If exercise does not appear in any user routines, fetch the exercise the user is requesting to update from the database
        stmt = db.select(Exercise).filter_by(id=exercise_id)
        exercise = db.session.scalar(stmt)

        # Update the below attributes for the exercise
        exercise.exercise_name = body_data.get("exercise_name") or exercise.exercise_name
        exercise.description = body_data.get("description") or exercise.description
        exercise.body_part = body_data.get("body_part") or exercise.body_part

        # Commit to the database
        db.session.commit()

        # Return the updated exercise to the user
        return exercise_schema.dump(exercise), 200
    
    # Catch any integrity errors (most likely unique violations)
    except IntegrityError as err:
        # Rollback session to retain database integrity
        db.session.rollback()
        # If error matches not null violation, return error message to user advising requirements
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            return {"error": f"Both 'exercise_name' and 'body_part' is required"}, 400
        # If error matches unique violation, return error message to user advising of unique requirement for exercise name
        if err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
            # unique violation
            return {"error": f"The value for 'exercise_name' must be unique. An exercise with that name already exists. Please choose a different name."}, 400    