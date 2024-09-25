from flask import Blueprint, request

from models.exercise import Exercise, exercise_schema, exercises_schema, ExerciseSchema
from models.user import User
from init import bcrypt, db

from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity


exercises_bp = Blueprint("exercises", __name__, url_prefix="/exercises")

# GET - list of exercises (both public & private)
# POST - create a new exercise
# POST - copy an existing public exercise and create a private copy
# UPDATE - a specific exercise (can only update if user created the exercise)
# DELETE - a specific exercise (can only delete if user created the exercise)

# /exercises - GET - fetch all exercises which are public and created by the logged in user
@exercises_bp.route("/", methods=["GET"])
@jwt_required(optional=True)
def get_exercises():
    # Retrieve data from the request body
    body_data = request.get_json(silent=True) or {}

    # If username or body_part is provided in the request, store the data in respective variable
    body_part = body_data.get("body_part", None)
    username = body_data.get("username", None)

    # Grabs the ID of the user if user is logged in
    user_id = get_jwt_identity()

    # Selects all exercises in the Exercise model which have public set as True
    stmt = db.select(Exercise).filter_by(public=True)

    # If user provides a body_part, filter exercises by selected body_part
    if body_part:
        stmt = stmt.filter_by(body_part=body_part)

    # If user provides a username, filter exercises by exercises created by specific user (public only)
    if username:
        stmt = stmt.join(User).filter_by(username=username)

    # If the user is logged in + no username is searched
    if user_id and not username:
        # Fetch the users private exercises
        user_stmt = db.select(Exercise).filter_by(user_id=user_id)
        # If the user included a body_part search
        if body_part:
            # filter the user's private exercises by searched body_part
            user_stmt = user_stmt.filter_by(body_part=body_part)
        # Join the user's private filtered/unfiltered exercises (user_stmt) to the list of public exercises (stmt)
        stmt = stmt.union(user_stmt)

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

# @exercises_bp.route("/", methods=["DELETE"])
# @jwt_required()
# def delete_exercise():
#     # get the details of the new exercise from the body of the request