from flask import Blueprint, request

from models.exercise import Exercise, exercise_schema, exercises_schema, ExerciseSchema
from models.user import User
from models.routine_exercise import RoutineExercise
from init import bcrypt, db
from utils import auth_as_admin_or_owner

from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity


exercises_bp = Blueprint("exercises", __name__, url_prefix="/exercises")

# GET - list of exercises
# POST - create a new exercise
# POST - copy an existing public exercise and create a private copy
# UPDATE - a specific exercise (can only update if user created the exercise)
# DELETE - a specific exercise (can only delete if user created the exercise)

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
        return {"error": f"Exercise with 'ID - {exercise_id}' is being used in existing routine/s. Delete has been aborted."}

    # If it doesn't exist in a user's routine, delete the exercise from the database
    db.session.delete(exercise)
    db.session.commit()
    # Return an acknowledgement message
    return {"message": f"Exercise with 'ID - {exercise_id}' has been successfully deleted."}