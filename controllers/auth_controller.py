# Import timedelta for access token expiry (USER LOGIN route)
from datetime import timedelta

# Import Blueprint & request for better organisation and route management
from flask import Blueprint, request

# Import models and schemas required for object creation and to serialise/deserialise data
from models.user import User, user_schema, UserSchema
from models.exercise import Exercise
from models.routine import Routine
# Import bcrypt and SQLAlchemy for password hashing and database functionality
from init import bcrypt, db

# Import validation and authentication libraries for error handling, authentication and JWT management
from sqlalchemy.exc import IntegrityError
from psycopg2 import errorcodes
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

# Import from utils.py:
# auth_as_admin_or_owner: decorator which checks if logged in user has authorisation to access the decorated route
# ADMIN_EMAIL: used for abstracting admin email
from utils import auth_as_admin_or_owner, ADMIN_EMAIL

# Create blueprint named "auth". Also decorate with url_prefix for management of routes.
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# Identifies that the deleted account is account with ID = 1
# When a user deletes their account, they can choose to either leave their public routines on the server for others to continue using/viewing, or they can be deleted entirely.
# If the user decides to keep them on the server, their public routines will be transferred and 'owned' by the deleted account (prior to removing the user from the database)
DELETED_ACCOUNT_ID = 1


# /auth/register - REGISTER NEW USER
@auth_bp.route("/register", methods=["POST"])
@jwt_required(optional=True) # User can optionally be logged in to access route (allows admin to create another admin)
def register_user():
    # Get the data from the body of the request
    body_data = UserSchema().load(request.get_json())

    # Store body data for username and email
    username = body_data.get("username")
    email = body_data.get("email")

    # Check if given username and/or email exist in database
    user_stmt = db.select(User).filter_by(username=username)
    email_stmt = db.select(User).filter_by(email=email)
    # Execute statements
    username_taken = db.session.scalar(user_stmt)
    email_taken = db.session.scalar(email_stmt)

    # If either username or email has been taken, return an error message
    if username_taken:
        return {"error": f"The username '{body_data.get('username')}' has been taken. Please choose a unique username."}, 400
    if email_taken:
        return {"error": f"The email you've entered '{body_data.get('email')}' is already taken. Please try to log in instead, or email admin: {ADMIN_EMAIL}"}, 400

    # Fetch user_id if user is logged in
    logged_in_user = get_jwt_identity()

    # Check if there was an admin registration request ("is_admin": true)
    admin_request = body_data.get("is_admin")

    # If there was an admin request = true, perform error handling for:
    if admin_request:
        # If user is not logged in
        if not logged_in_user:
            # Return an error message
            return {"error": "An admin request has been detected, please log in as admin and try again."}, 401
        else:
            # If logged in user != admin
            check_log_stmt = db.select(User).filter_by(id=logged_in_user)
            check_logged_user = db.session.scalar(check_log_stmt)
            if not check_logged_user.is_admin:
                # Return an error stating only admins can create another admin
                return {"error": "Only Admins can register an admin account. User registration has been cancelled."}, 403

    # If the admin request = true and the logged in user is an admin, set admin_result as True. Else, revert back to default (false)        
    if admin_request and check_logged_user.is_admin:
        admin_result = True 
    else:
        admin_result = False
    
    # Create an instance of the new user using the details from the body of the request
    user = User(
        username = body_data.get("username"),
        firstname = body_data.get("firstname"),
        lastname = body_data.get("lastname"),
        email = body_data.get("email"),
        is_admin = admin_result # True or False, determined by previous code
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
        # create a JWT token (expires in 1 day)
        token = create_access_token(identity=str(user.id), expires_delta=timedelta(days=1))
        # Then return a response to the user with their email address, admin status and JWT token
        return {"username": user.username, "email": user.email, "token": token, "is_admin": user.is_admin}
    # Else
    else:
        # Respond back with an error message
        return {"error": "Invalid email or password"}, 400
    
# /auth/users/ - UPDATE USER DETAILS
@auth_bp.route("/users/", methods=["PUT", "PATCH"])
# User must be authenticated / logged in
@jwt_required()
def update_user():
    try:
        # get the fields from the body of the request
        body_data = UserSchema().load(request.get_json(), partial=True)
        # If the user inserts a new passowrd, store the new password in a variable named "password" 
        password = body_data.get("password")

        # fetch the user from the database by extracting the user's identity from the JWT token they passed in the header and finding the user ID it matches to in the database 
        # SELECT * FROM user WHERE id = get_jwt_identity
        stmt = db.select(User).filter_by(id=get_jwt_identity())
        user = db.session.scalar(stmt)

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
    
    except IntegrityError as err:
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            return {"error": f"The column '{err.orig.diag.column_name}' is required"}, 400
        if err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
            # Unique violation
            return {"error": f"The value for 'username' must be unique. The username you entered already exists in our database."}, 400

    
# /auth/users/<int:user_id> - DELETE - Delete user. UPON REQUEST, database will keep any public routines but delete private ones (default = delete all). Will also keep any exercises created by user by transferring ownership. This will keep data integrity and also allow users to still have access to these public routines
@auth_bp.route("/users/<int:user_id>", methods=["DELETE"])
@jwt_required() # Check if the user has a valid JWT token in the header of their request
@auth_as_admin_or_owner # Validates if user_id in URL exists and if logged in user is admin or owner of resource
def delete_user(user_id):
    # Grab data from body of JSON request (provide empty dictionary if body is empty)
    body_data = request.get_json(silent=True) or {}

    # Grab "delete_public_routines" from data (default to True if not provided)
    delete_public_routines = body_data.get("delete_public_routines", True)

    # Validate if user input is either boolean (true or false)
    if not isinstance(delete_public_routines, bool):
        # if not boolean, submit an error
        return {"error": "Invalid input for 'delete_public_routines'. Please input true or false."}, 400
    
    # Create variable for better acknowledgement message regarding user's public routines
    decision = "deleted"
    if delete_public_routines is False:
        decision = "kept"
    
    # Find & select user in database
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.scalar(stmt)

    # If user wants to leave their public routines on the database
    if not delete_public_routines:
        # Select all routines which are created by the user and public
        stmt = db.select(Routine).filter_by(user_id=user_id, public=True)
        user_public_routines = db.session.scalars(stmt)
        # For each of these routines, transfer user_id to DELETED_ACCOUNT_ID
        for routine in user_public_routines:
            routine.user_id = DELETED_ACCOUNT_ID

    # Select all/remainder user routines
    stmt = db.select(Routine).filter_by(user_id=user_id)
    remaining_routines = db.session.scalars(stmt)

    for routine in remaining_routines:
        db.session.delete(routine)

    # Transfer ownership of any user created exercises to the "DELETED_ACCOUNT" user_id
    stmt = db.select(Exercise).filter_by(user_id=user_id)
    user_exercises = db.session.scalars(stmt)

    for exercise in user_exercises:
        exercise.user_id = DELETED_ACCOUNT_ID

    # Delete user and commit changes to database
    db.session.delete(user)
    db.session.commit()

    # return an acknowledgement message
    return {"message": f"User with id {user_id} has been deleted. We have {decision} your public routines. If there has been a mistake, please email us on '{ADMIN_EMAIL}'. We hope you come back soon!"}, 200
