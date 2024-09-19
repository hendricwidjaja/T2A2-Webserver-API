from flask import Blueprint, request

from models.user import User, user_schema, UserSchema
from init import bcrypt, db

from sqlalchemy.exc import IntegrityError
from psycopg2 import errorcodes
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/register", methods=["POST"])
def register_user()
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

@auth_bp.route("/login")