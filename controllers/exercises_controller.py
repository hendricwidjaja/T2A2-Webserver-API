from flask import Blueprint, request

from models.exercise import Exercise, exercise_schema, exercises_schema, ExerciseSchema
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
    # Grabs the ID of the user if user is logged in
    user_id = get_jwt_identity()
    # Selects all exercises in the Exercise model which have public set as True
    stmt = db.Select(Exercise).filter_by(public=True)
    # If a user is logged in, also add exercises which were created by the logged in user
    if user_id:
        stmt = stmt.union_all(db.select(Exercise).filter_by(user_id=user_id))
    # Order the exercise by name
    stmt = stmt.order_by(Exercise.exercise_name)

    exercises = db.session.scalars(stmt)

    return exercises_schema.dump(exercises), 200

@exercises_bp.route("/", methods=["POST"])
@jwt_required()
def create_exercise():
    # get the details of the new exercise from the body of the request
    body_data = exercise_schema.load(request.get_json())

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

# @exercises_bp.route("/", methods=["POST"])
# @jwt_required()
# def copy_exercise():
#     # get the details of the new exercise from the body of the request
#     body_data = exercise_schema.load(request.get_json())

#     stmt = db.select(Exercise).filter_by(id=body.data("id"))
#     exercise = db.session.scalar(stmt)

#     if exercise:
#         exercise = Exercise(