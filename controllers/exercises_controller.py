from flask import Blueprint, request

from models.exercise import Exercise, exercise_schema, exercises_schema
from models.user import User
from models.routine_exercise import RoutineExercise
from init import db
from utils import auth_as_admin_or_owner, ADMIN_EMAIL, user_is_admin

from sqlalchemy.exc import IntegrityError
from psycopg2 import errorcodes
from flask_jwt_extended import jwt_required, get_jwt_identity


exercises_bp = Blueprint("exercises", __name__, url_prefix="/exercises")


# /exercises - GET - fetch all exercises (optional: filter by body_part and/or username)
@exercises_bp.route("/", methods=["GET"])
def get_exercises():
    # Fetch any fields from body of request
    body_data = request.get_json(silent=True) or {}

    # If username or body_part is provided in the request, store the data in respective variable
    body_part = body_data.get("body_part", None)
    username = body_data.get("username", None)

    # Fetch all exercises
    stmt = db.select(Exercise)

    # If user provides "body_part" or "username", filter by user value
    if body_part:
        stmt = stmt.filter(Exercise.body_part == body_part)
    if username:
        stmt = stmt.join(User).filter(User.username == username)

    # Return exercises in alphabetical order (by exercise_name)
    stmt = stmt.order_by(Exercise.exercise_name.asc())

    # Execute the query
    exercises = db.session.scalars(stmt).all()

    # Error handling if exercise can't be found for each case
    if not exercises:
        if body_part and username:
            return {"error": f"We couldn't find any '{body_part}' exercises by '{username}'. Make sure body_part = (Chest, Shoulders, Back, Legs, Triceps, Biceps, Core, Cardio)"}, 404
        elif body_part:
            return {"error": f"We couldn't find any '{body_part}' exercises. Try searching by (Chest, Shoulders, Back, Legs, Triceps, Biceps, Core, Cardio)"}, 404
        elif username:
            return {"error": f"We couldn't find any exercises by '{username}'."}, 404
        else:
            return {"error": "No exercises found."}, 404

    # Return the exercises as a response
    return exercises_schema.dump(exercises)


# /exercises/<int:exercise_id> - GET - fetch a specific exercise
@exercises_bp.route("/<int:exercise_id>", methods=["GET"])
def get_exercise(exercise_id):
    stmt = db.select(Exercise).filter_by(id=exercise_id)

    card = db.session.scalar(stmt)

    if card:
        return exercise_schema.dump(card), 200
    else:
        return {"error": f"Exercise with id '{exercise_id}' not found"}, 404


# /exercises/ - POST - create an exercise
@exercises_bp.route("/", methods=["POST"])
@jwt_required()
def create_exercise():
    try:
        # Get the details of the new exercise from the body of the request
        body_data = exercise_schema.load(request.get_json())

        # Check if the provided exercise name already exists in the list of exercises
        exercise_name = body_data.get("exercise_name")
        existing_exercise = db.session.query(Exercise).filter_by(exercise_name=exercise_name).first()
        # If the exercise already exists, send an error message
        if existing_exercise: 
            return {"error": "An exercise with that name already exists. Please choose a different name."}, 400

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


# /exercises/<int:exercise_id> - DELETE - Delete an exercise
@exercises_bp.route("/<int:exercise_id>", methods=["DELETE"])
@jwt_required()
@auth_as_admin_or_owner
def delete_exercise(exercise_id):
    # Fetch the exercise the user is requesting to delete from the database
    stmt = db.select(Exercise).filter_by(id=exercise_id)
    exercise = db.session.scalar(stmt)

    # Check if exercise appears in a user's routine
    exercise_is_used = db.session.query(RoutineExercise).filter_by(exercise_id=exercise_id).first()
    # If exists in a user's routine:
    if exercise_is_used:
        # return error
        return {"error": f"Exercise with 'ID - {exercise_id}' is being used in existing routine/s. Delete has been aborted. If action is still required, email admin: {ADMIN_EMAIL}"}

    # If it doesn't exist in a user's routine, delete the exercise from the database
    db.session.delete(exercise)
    db.session.commit()
    # Return an acknowledgement message
    return {"message": f"Exercise with 'ID - {exercise_id}' has been successfully deleted."}


# /exercises/<int:exercise_id> - PUT/PATCH - Update an exercise
@exercises_bp.route("/<int:exercise_id>", methods=["PUT", "PATCH"])
@jwt_required()
@auth_as_admin_or_owner
def update_exercise(exercise_id):
    try:
        # Fetch data from body of request
        body_data = exercise_schema.load(request.get_json(), partial=True)

        # Fetch the exercise the user is requesting to update from the database
        stmt = db.select(Exercise).filter_by(id=exercise_id)
        exercise = db.session.scalar(stmt)

        # Check if exercise appears in a user's routine
        exercise_is_used = db.session.query(RoutineExercise).filter_by(exercise_id=exercise_id).first()

        # If exists in a user's routine and user is not admin
        if exercise_is_used and not user_is_admin():
            # return error
            return {"error": f"Exercise with 'ID - {exercise_id}' is being used in existing routine/s. Update has been aborted. If action is still required, email admin: {ADMIN_EMAIL}"}

        # If it doesn't exist in a user's routine, update the below attributes for the exercise
        exercise.exercise_name = body_data.get("exercise_name") or exercise.exercise_name
        exercise.description = body_data.get("description") or exercise.description
        exercise.body_part = body_data.get("body_part") or exercise.body_part

        # Commit to the database
        db.session.commit()

        # Return the updated exercise to the user
        return exercise_schema.dump(exercise)
    
    except IntegrityError as err:
        db.session.rollback()
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            return {"error": f"The column {err.orig.diag.column_name} is required"}, 400
        if err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
            # unique violation
            return {"error": f"The value for '{err.orig.diag.column_name}' must be unique. An exercise with that name already exists. Please choose a different name."}, 400    