from flask_jwt_extended import get_jwt_identity

from functools import wraps

from init import db
from models.user import User
from models.exercise import Exercise
from models.routine import Routine

ADMIN_EMAIL = "admin@email.com"

def user_is_admin():
    # get the user's id from get_jwt_identity
    user_id = get_jwt_identity()
    # fetch the user from the db
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.scalar(stmt)
    # check whether the user is an admin or not
    return user.is_admin

# Decorator for checking if logged in user is the owner of the resource (user_id, exercise_id or routine_id) OR an admin 
# Also includes validation by checking if the resource id in the URL can be found in the respective resource table

def auth_as_admin_or_owner(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # get the user's id from get_jwt_identity
        logged_user_id = get_jwt_identity()
        # fetch the user from the db
        stmt = db.select(User).filter_by(id=logged_user_id)
        user = db.session.scalar(stmt)

        # Fetch the user/exercise/routine ID from URL
        user_id = kwargs.get('user_id')
        exercise_id = kwargs.get('exercise_id')
        routine_id = kwargs.get('routine_id')

        # If user_id is provided in URL:
        if user_id:
            # Check if user_id exists in User table
            user_exists = db.session.query(User).filter_by(id=user_id).first()
            # If user doesn't exist:
            if not user_exists:
                # Return error message
                return {"error": f"User with ID '{user_id}' could not be found."}, 404
            # if user is admin or correct user
            if user.is_admin or user.id == int(user_id):
                # allow the function to execute
                return fn(*args, **kwargs)
            
        # If exercise_id is provided in URL:
        elif exercise_id:
            # Check if exercise_id exists in Exercise table
            exercise_exists = db.session.query(Exercise).filter_by(id=exercise_id).first()
            # If it doesn't exist:
            if not exercise_exists:
                # Return error message
                return {"error": f"Exercise with ID '{exercise_id}' could not be found."}, 404
            # Else:
            else:
                # if user is admin or owner of exercise
                if user.is_admin or exercise_exists.user_id == int(logged_user_id):
                    # allow the function to execute
                    return fn(*args, **kwargs)
        # If routine_id is provided in URL:
        elif routine_id:
            # Check if routine_id exists in Routine table
            routine_exists = db.session.query(Routine).filter_by(id=routine_id).first()
            # If it doesn't exist:
            if not routine_exists:
                # Return error message
                return {"error": f"Routine with ID '{routine_id}' could not be found."}, 404
            # Else:
            else:
                # if user is admin or owner of routine
                if user.is_admin or routine_exists.user_id == int(logged_user_id):
                    # allow the function to execute
                    return fn(*args, **kwargs)

        return {"error": "Only admin or the owner of this resource can perform this action."}, 403
        
    return wrapper