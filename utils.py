from flask_jwt_extended import get_jwt_identity

from functools import wraps

from init import db
from models.user import User

# Decorator for checking if user is admin
def auth_as_admin(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # get the user's id from get_jwt_identity
        user_id = get_jwt_identity()
        # fetch the user from the db
        stmt = db.select(User).filter_by(id=user_id)
        user = db.session.scalar(stmt)
        # if user is admin
        if user.is_admin:
            # allow the decorator "fn" to execute - this is because the decorator 
            return fn(*args, **kwargs)
        # else
        else:
            return {"error": "Only admin can perform this action "}, 403
        
    return wrapper

# Decorator for checking if logged in user is owner OR admin
def auth_as_admin_or_owner(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # get the user's id from get_jwt_identity
        logged_user_id = get_jwt_identity()
        # fetch the user from the db
        stmt = db.select(User).filter_by(id=logged_user_id)
        user = db.session.scalar(stmt)

        # Fetch the user ID from URL
        user_id = kwargs.get('user_id')

        # if user is admin
        if user.is_admin or user.id == user_id:
            # allow the function to execute
            return fn(*args, **kwargs)
        # else
        else:
            return {"error": "Only admin or owner can perform this action "}, 403
        
    return wrapper