from flask import Blueprint, request

from models.exercise import Exercise, exercise_schema, exercises_schema, ExerciseSchema
from models.user import User
from init import bcrypt, db

from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from utils import authorise_as_admin, string_to_bool


exercises_bp = Blueprint("exercises", __name__, url_prefix="/exercises")

# GET - list of exercises (both public & private)
# POST - create a new exercise
# POST - copy an existing public exercise and create a private copy
# UPDATE - a specific exercise (can only update if user created the exercise)
# DELETE - a specific exercise (can only delete if user created the exercise)

# /exercises - GET - fetch all exercises which are public only
@exercises_bp.route("/public", methods=["GET"])
def get_public_exercises():
    # Retrieve data from the request body
    body_data = request.get_json(silent=True) or {}

    # If username or body_part is provided in the request, store the data in respective variable
    body_part = body_data.get("body_part", None)
    username = body_data.get("username", None)

    # Selects all exercises in the Exercise model which have public set as True
    stmt = db.select(Exercise).filter_by(public=True)

    # If user provides a body_part, filter exercises by selected body_part
    if body_part:
        stmt = stmt.filter_by(body_part=body_part)

    # If user provides a username, filter exercises by exercises created by specific user (public only)
    if username:
        stmt = stmt.join(User).filter_by(username=username)

    # Order the exercise by name
    stmt = stmt.order_by(Exercise.exercise_name)

    exercises = db.session.scalars(stmt)

    return exercises_schema.dump(exercises), 200


# /exercises - GET - fetch all exercises which are private/created by the logged in user
@exercises_bp.route("/private", methods=["GET"])
@jwt_required()
def get_private_exercises():
    # Retrieve data from the request body
    body_data = request.get_json(silent=True) or {}

    # If username or body_part is provided in the request, store the data in respective variable
    body_part = body_data.get("body_part", None)
    username = body_data.get("username", None)

    # Grabs the ID of the user if user is logged in
    user_id = get_jwt_identity()

    # Fetch all exercises which have been created by the logged in user
    stmt = db.select(Exercise).filter_by(user_id=user_id)

    # If user provides a body_part, filter exercises by selected body_part
    if body_part:
        stmt = stmt.filter_by(body_part=body_part)

    # Order the exercise by name
    stmt = stmt.order_by(Exercise.exercise_name)

    exercises = db.session.scalars(stmt)

    return exercises_schema.dump(exercises), 200


@exercises_bp.route("/", methods=["POST"])
@jwt_required()
def create_exercise():
    # get the details of the new exercise from the body of the request
    body_data = exercise_schema.load(request.get_json())
    
    if "body_part" not in body_data:
        return {"error": "body_part is required when creating an exercise."}, 400

    public_value = body_data.get("public")
    public = str(public_value).lower() in ("true", "yes")

    exercise = Exercise(
        user_id = get_jwt_identity(),
        exercise_name = body_data.get("exercise_name"),
        description = body_data.get("description"),
        body_part = body_data.get("body_part"),
        public = public
    )
    # add and commit to the DB
    db.session.add(exercise)
    db.session.commit()
    # response message
    return exercise_schema.dump(exercise)


@exercises_bp.route("/<int:exercise_id>", methods=["DELETE"])
@jwt_required()
def delete_exercise(exercise_id):
    # Fetch the exercise the user is requesting to delete from the database
    stmt = db.select(Exercise).filter_by(id=exercise_id)
    exercise = db.session.scalar(stmt)

    # Check if user is admin
    is_admin = authorise_as_admin()

    # Fetch the user_id of the logged in user
    user_id = get_jwt_identity()

    # If exercise exists:
    if exercise:
        # Check if user is creator of the exercise or is admin (if not, return an error message)
        if not (str(exercise.user_id) == user_id or is_admin):
            return {"error": "You do not have permission to delete this exercise"}, 403
        # Check if exercise is public (public exercises cannot be deleted)
        if exercise.public:
            return {"error": "Publicly posted exercises cannot be deleted."}, 403
        db.session.delete(exercise)
        db.session.commit()
        return {"message": f"Exercise ID:{exercise.id} ({exercise.exercise_name}) has been deleted successfully!"}
    else:
        # Return an error message - exercise does not exist
        return {"error": f"Exercise ID:{exercise_id} does not exist"}, 404


@exercises_bp.route("/<int:exercise_id>", methods=["PATCH"])
@jwt_required()
def update_exercise(exercise_id):
    # Fetch information from the body of the request
    body_data = exercise_schema.load(request.get_json())

    # Fetch the exercise from the database
    stmt = db.select(Exercise).filter_by(id=exercise_id)
    exercise = db.session.scalar(stmt)

    # Check if user is admin
    is_admin = authorise_as_admin()

    # Fetch the user_id of the logged in user
    user_id = get_jwt_identity()

    # If exercise exists:
    if exercise:
        # If logged in user is not creator of exercise or admin
        if not (str(exercise.user_id) == user_id or is_admin):
            return {"error": "You do not have permission to update this exercise"}, 403
        
        if exercise.public:
            return {"error": "Publicly posted exercises cannot be updated or changed to private."}, 403
        if "public" in body_data and string_to_bool(body_data.get("public")):
            exercise.public = string_to_bool(body_data.get("public"))
        
        # Update exercises as per data in body of request
        exercise.exercise_name = body_data.get("exercise_name") or exercise.exercise_name
        exercise.description = body_data.get("description") or exercise.description
        exercise.body_part = body_data.get("body_part") or exercise.body_part

        db.session.commit()

        return exercise_schema.dump(exercise)
    else:
        # return an error message
        return {"error": f"Exercise with id:{exercise_id} could not be found."}, 404