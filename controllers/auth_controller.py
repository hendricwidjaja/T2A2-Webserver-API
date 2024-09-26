from datetime import timedelta

from flask import Blueprint, request

from models.user import User, user_schema, UserSchema
from models.exercise import Exercise
from init import bcrypt, db

from sqlalchemy.exc import IntegrityError
from psycopg2 import errorcodes
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from utils import authorise_as_admin

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

DELETED_ACCOUNT_ID = 1

# /auth/register - REGISTER NEW USER
@auth_bp.route("/register", methods=["POST"])
def register_user():
    try:
        # Get the data from the body of the request
        body_data = UserSchema().load(request.get_json())
        # Create an instance of the User Model
        user = User(
            username = body_data.get("username"),
            firstname = body_data.get("firstname"),
            lastname = body_data.get("lastname"),
            email = body_data.get("email")
        )
        # Hash the password using bcrypt
        password = body_data.get("password")
        if password:
            user.password = bcrypt.generate_password_hash(password).decode("utf-8")
        # Add and commit to the DB
        db.session.add(user)
        db.session.commit()
        # Return acknowledgement for the successful creation of a user account
        return user_schema.dump(user), 201
    # If user creation fails, send an appropriate error response based on the type of error/violation
    except IntegrityError as err:
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            return {"error": f"The column {err.orig.diag.column_name} is required"}, 400
        if err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
            # unique violation
            return {"error": "Email address must be unique"}, 400

# /auth/login - USER LOGIN
@auth_bp.route("/login", methods=["POST"])
def login_user():
    # Get the data from the body of the request
    body_data = request.get_json()
    # Find the user in the database with that email address
    stmt = db.select(User).filter_by(email=body_data.get("email"))
    user = db.session.scalar(stmt)
    # If the user exists and the password is correct
    if user and bcrypt.check_password_hash(user.password, body_data.get("password")):
        # create a JWT token
        token = create_access_token(identity=str(user.id), expires_delta=timedelta(days=1))
        # Then return a response to the user with their email address, admin status and JWT token
        return {"username": user.username, "email": user.email, "token": token, "is_admin": user.is_admin}
    # Else
    else:
        # Respond back with an error message
        return {"error": "Invalid email or password"}, 400
    
# /auth/users/ - UPDATE USER DETAILS
@auth_bp.route("/users/", methods=["PUT", "PATCH"])
# Check if the user has a valid JWT token in the header of their request
@jwt_required()
def update_user():
    # get the fields from the body of the request
    body_data = UserSchema().load(request.get_json(), partial=True)
    # If the user inserts a new passowrd, store the new password in a variable named "password" 
    password = body_data.get("password")
    # fetch the user from the database by extracting the user's identity from the JWT token they passed in the header and finding the user ID it matches to in the database 
    # SELECT * FROM user WHERE id = get_jwt_identity
    stmt = db.select(User).filter_by(id=get_jwt_identity())
    user = db.session.scalar(stmt)
    # if the user exists:
    if user:
        # update the fields as required
        user.username = body_data.get("username") or user.username
        user.firstname = body_data.get("firstname") or user.firstname
        user.lastname = body_data.get("lastname") or user.lastname
        if password:
            user.password = bcrypt.generate_password_hash(password).decode("utf-8")
        # commit the changes to the database
        db.session.commit()
        # return a response to the user, acknowledging the changes
        return user_schema.dump(user)
    # else:
    else:
        # return an error response
        return {"error": "User does not exist."}
    
# /auth/users/<int:user_id> - DELETE USER
@auth_bp.route("/users/<int:user_id>", methods=["DELETE"])
# Check if the user has a valid JWT token in the header of their request
@jwt_required()
def delete_user(user_id):
    # find the user with the id from the db
    # SELECT * FROM users WHERE id==user_id;
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.scalar(stmt)
    # Assign user_id #1 (deleted account) to deleted_account variable
    deleted_account = DELETED_ACCOUNT_ID
    # check whether the user is admin or not
    is_admin = authorise_as_admin()
    # if exists:
    if user:
        # if the user that is logged in is not the selected user and not admin, return an error message
        if not is_admin and str(user.id) != get_jwt_identity():
            return {"error": "Cannot perform this operation. Only owners or admin are allowed to execute this operation"}
        
        # Delete all public=False exercises, logs and workout routines
        private_exercises = Exercise.query.filter_by(user_id=user_id, public=False).all()
        for exercise in private_exercises:
            db.session.delete(exercise)

        # Transfer any public exercises and workout routines to the "DELETED_ACCOUNT" user
        Exercise.query.filter_by(user_id=user_id, public=True).update({"user_id": deleted_account})

        # delete the user
        db.session.delete(user)
        db.session.commit()
        # return an acknowledgement message
        return {"message": f"User with id {user_id} is deleted."}
    # else:
    else:
        # return error message
        return {"message": f"User with id {user_id} not found."}, 404