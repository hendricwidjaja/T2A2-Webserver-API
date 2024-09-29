from flask import Blueprint, request

from models.user import User
from models.routine import Routine, routine_schema, routines_schema
from models.routine_exercise import RoutineExercise, routine_exercise_schema
from models.like import Like
from init import db
from utils import auth_as_admin_or_owner, user_is_admin

from flask_jwt_extended import jwt_required, get_jwt_identity


routines_bp = Blueprint("routines", __name__, url_prefix="/routines")

# /routines - GET - fetch all public routines + personal private routines if logged in. Admin can see all. Allows users to see what the newest routines which have been added by other users
@routines_bp.route("/", methods=["GET"])
@jwt_required(optional=True)
def get_routines():
    # Fetch user_id if exists
    user_id = get_jwt_identity()

    # If user is logged in:
    if user_id:
        # Fetch user in database
        stmt = db.select(User).filter_by(id=user_id)
        logged_user = db.session.scalar(stmt)
        # If user is an admin:
        if logged_user.is_admin:
            # Query database for all routines in order of most recent
            stmt = db.select(Routine).order_by(Routine.created.desc())
        # If user is not admin
        else:
            # Fetch all public routines
            public_stmt = db.select(Routine).filter_by(public=True)
            # Fetch all private routines created by logged in user
            priv_stmt = db.select(Routine).filter_by(user_id=user_id, public=False)
            # Combine results of queries and order by date routine was created
            stmt = public_stmt.union(priv_stmt).order_by(Routine.created.desc())

    # If user is not logged in
    else:
        stmt = db.select(Routine).filter_by(public=True).order_by(Routine.created.desc())

    # Execute query:
    routines = db.session.scalars(stmt)
    # Return respective list to each type of user
    return routines_schema.dump(routines), 200


# /routines/<str:target> - GET - Search for a public routine which targets a specific muscle group. User can also order the selected muscle group by popularity (how many likes), recent, and oldest
@routines_bp.route("/<target>", methods=["GET"])
def get_target_routine(target, order):
    # Fetch user_id if exists
    user_id = get_jwt_identity()

    # Initialise order by (default as order by Routine title)
    order_by = Routine.routine_title.asc()

    # Grab data from body of JSON request
    body_data = request.get_json()

    # Grab "order" from data
    order = body_data.get("order")

    # Validation for body_data
    if order == "popular":
        order_by = Routine.likes_count.desc()
    elif order == "recent":
        order_by = Routine.created.desc()
    elif order == "oldest":
        order_by = Routine.created.asc()
    elif order is not None:
        return {"error": "Could not recognise the filter applied. Please input 'popular', 'recent' or 'oldest'."}

    # If user is logged in:
    if user_id:
        # Fetch user in database
        stmt = db.select(User).filter_by(id=user_id)
        logged_user = db.session.scalar(stmt)
        # If user is an admin:
        if logged_user.is_admin:
            # Select all routines in order of most recent
            stmt = db.select(Routine).filter_by(target=target).order_by(order_by)
        # If user is not admin
        else:
            # Fetch all public routines with target
            public_stmt = db.select(Routine).filter_by(public=True, target=target)
            # Fetch all private routines created by logged in user with target
            priv_stmt = db.select(Routine).filter_by(user_id=user_id, public=False, target=target)
            # Combine results of queries and order by date routine was created
            stmt = public_stmt.union(priv_stmt).order_by(order_by)

    # If user is not logged in:
    else:
        # Select all routines which are public and include target as specified in URL.
        stmt = db.select(Routine).filter_by(public=True, target=target).order_by(order_by)

    # Execute query:
    routines = db.session.scalars(stmt)

    # Return respective list to each type of user
    return routines_schema.dump(routines), 200


# /routines/liked - GET - View all routines that logged in user has liked
@routines_bp.route("/liked", methods=["GET"])
@jwt_required()
def liked_routines():
    # Fetch user's id using jwt
    user_id = get_jwt_identity()

    # Grab all logged in user's likes in 'Like' table
    stmt = db.select(Like).filter_by(user_id=user_id)
    likes = db.session.scalars(stmt)

    # If user has likes:
    if likes:
        # Fetch routine IDs from each liked routine and store in 'routine_ids'
        routine_ids = []
        for like in likes:
            routine_ids.append(like.routine_id)

        # Select all routines from Routine table that match 'routine_ids' and order from newest to oldest
        stmt = db.select(Routine).filter(Routine.id.isin(routine_ids)).order_by(Routine.created.desc())

        # Execute the query
        liked_routines = db.session.scalars(stmt)

        # Return list of liked routines to user
        return routines_schema.dump(liked_routines), 200
    
    # Else, if user hasn't liked any posts yet
    return {"message": "You haven't liked any routines yet."}, 200


# /routines - POST - create a new routine (must be logged in)
@routines_bp.route("/", methods=["POST"])
@jwt_required()
def create_routine():
    # Fetch data from JSON body
    body_data = routine_schema.load(request.get_json())

    # Fetch user's id from JWT
    user_id = jwt_required()

    # Create an instance of a routine using the data from the JSON body. User_id is determined by jwt
    routine = Routine(
        routine_title = body_data.get("routine_title"),
        description = body_data.get("description"),
        target = body_data.get("target"),
        public = body_data.get("public"),
        user_id = user_id
    )

    # Add and commit instance to database
    db.session.add(routine)
    db.session.commit()

    # Return routine information to user
    return routine_schema.dump(routine), 201


# /routines/<int:routine_id> - GET - fetch specific routine (can be viewed by all if public. If private, must be owner or admin to view)
@routines_bp.route("/<int:routine_id>", methods=["GET"])
@jwt_required(optional=True)
def get_specific_routine(routine_id):
    # Query the database for the routine that matches routine_id
    stmt = db.select(Routine).filter_by(id=routine_id)

    # Execute the query
    routine = db.session.scalar(stmt)

    # If the routine exists, check the below:
    if routine:
        # If the routine is set to public
        if routine.public:
            # Return routine to user
            return routine_schema.dump(routine), 200
        else:
            # If routine is private, check if the user is the creator or an admin
            user_id = get_jwt_identity() 

            # If logged in user matches the user id on the routine or is an admin
            if user_id == routine.user_id or user_is_admin():
                # Return to user
                return routine_schema.dump(routine), 200
            # Else:
            else:
                # Return an error message 
                return {"error": f"Access Restricted: A public routine with ID '{routine_id}' does not exist"}, 403
    else:
        # Return an error message if the routine doesn't exist
        return {"error": f"Routine with id '{routine_id}' does not exist."}, 404   


# /routines/<int:routine_id> - PUT/PATCH - update specific routine (must be owner or admin)
@routines_bp.route("/<int:routine_id>", methods=["PUT, PATCH"])
@jwt_required()
@auth_as_admin_or_owner
def update_routine(routine_id):
    # Fetch data from the body of the request
    body_data = routine_schema.load(request.get_json(), partial=True)

    # Fetch the routine from the database
    stmt = db.select(Routine).filter_by(id=routine_id)
    routine = db.session.scalar(stmt)

    # If routine does not exist
    if not routine:
        return {"error": f"Routine with ID {routine_id} not found."}, 404

    # If routine does exist, update attributes (if provided)
    routine.routine_title = body_data.get('routine_title') or routine.routine_title 
    routine.description = body_data.get('description') or routine.description
    routine.target = body_data.get('target') or routine.target
    routine.public = body_data.get('public') or routine.public

    # Commit the changes
    db.session.commit()

    return routine_schema.dump(routine), 200

# /routines/<int:routine_id> - DELETE - delete a specific routine (must be owner or admin)
@routines_bp.route("/<int:routine_id>", methods=["DELETE"])
@jwt_required()
@auth_as_admin_or_owner # Performs validation & checks if user is admin or owner or resource
def delete_routine(routine_id):
    # Fetch the routine from the Routine table. Filter by routine_id from URL
    stmt = db.select(Routine).filter_by(id=routine_id)
    routine = db.session.scalar(stmt)

    # Delete the routine
    db.session.delete(routine)
    db.session.commit()

    # Return successful delete message to user
    return {"message": f"Routine with ID {routine_id} has been deleted."}, 200


# /routines/<int:routine_id>/exercise - POST - add a routine_exercise to a routine
@routines_bp.route("/<int:routine_id>/exercise", methods=["POST"])
@jwt_required()
@auth_as_admin_or_owner
def add_routine_exercise(routine_id):
    # Fetch the routine from the Routine table. Filter by routine_id from URL
    stmt = db.select(Routine).filter_by(id=routine_id)
    routine = db.session.scalar(stmt)

    # If routine does not exist
    if not routine:
        return {"error": f"Routine with ID {routine_id} not found."}, 404

    # Get routine exercise data from request body
    body_data = routine_exercise_schema.load(request.get_json())

    # Create a new RoutineExercise object
    routine_exercise = RoutineExercise(
        routine_id = routine_id,
        exercise_id = body_data['exercise_id'],
        sets = body_data.get('sets'),
        reps = body_data.get('reps'), 
        weight = body_data.get('weight'), 
        distance_km = body_data.get('distance_km'), 
        distance_m = body_data.get('distance_m'), 
        hours = body_data.get('hours'), 
        minutes = body_data.get('minutes'), 
        seconds = body_data.get('seconds'), 
        note = body_data.get('note')
    )

    # Add and commit the new exercise
    db.session.add(routine_exercise)
    db.session.commit()

    return routine_exercise_schema.dump(routine_exercise), 201


# /routines/<int:routine_id>/<int:routine_exercise_id> - GET - View a specific routine exercise (public = view by everyone, private = owner or admin)
@routines_bp.route("/<int:routine_id>/<int:routine_exercise_id>", methods=["GET"])
@jwt_required(optional=True)
def get_routine_exercise(routine_id, routine_exercise_id):
    # Fetch the routine in the URL
    stmt = db.select(Routine).filter_by(id=routine_id)
    routine = db.session.scalar(stmt)

    # If routine does not exist
    if not routine:
        return {"error": f"Routine with ID {routine_id} not found."}, 404

    # Fetch user logged in user's ID 
    user_id = get_jwt_identity()

    # If the routine is private
    if not routine.public:
        # If user isn't logged in, doesn't own the routine and is not admin
        if not user_id or (user_id != routine.user_id and not user_is_admin()):
            return {"error": "You do not have permission to view this routine exercise."}, 403

    # Fetch the routine exercise where id = routine_exercise_id
    stmt = db.select(RoutineExercise).filter_by(id=routine_exercise_id)
    routine_exercise = db.session.scalar(stmt)

    if not routine_exercise:
        return {"error": f"Routine exercise with ID {routine_exercise_id} not found."}, 404

    return routine_exercise_schema.dump(routine_exercise), 200


# /routines/<int:routine_id>/<int:routine_exercise_id> - PUT/PATCH - Update a specific routine exercise (must be owner or admin)
@routines_bp.route("/<int:routine_id>/<int:routine_exercise_id>", methods=["PUT", "PATCH"])
@jwt_required()
@auth_as_admin_or_owner
def update_routine_exercise(routine_id, routine_exercise_id):
    # Get the data from the body of the request
    body_data = routine_exercise_schema.load(request.get_json())

    # Fetch the routine exercise
    stmt = db.select(RoutineExercise).filter_by(id=routine_exercise_id)
    routine_exercise = db.session.scalar(stmt)

    # If routine exercise exists, update attributes if provided
    if routine_exercise:
        routine_exercise.sets = body_data.get("sets") or routine_exercise.sets
        routine_exercise.reps = body_data.get("reps") or routine_exercise.reps
        routine_exercise.weight = body_data.get("weight") or routine_exercise.weight
        routine_exercise.distance_km = body_data.get("distance_km") or routine_exercise.distance_km
        routine_exercise.distance_m = body_data.get("distance_m") or routine_exercise.distance_m
        routine_exercise.hours = body_data.get("hours") or routine_exercise.hours
        routine_exercise.minutes = body_data.get("minutes") or routine_exercise.minutes
        routine_exercise.seconds = body_data.get("seconds") or routine_exercise.seconds
        routine_exercise.note = body_data.get("note") or routine_exercise.note

        # Commit updates to database
        db.session.commit()

        # Return acknowledgement
        return routine_exercise_schema.dump(routine_exercise)

    # If routine_exercise doesn't exist
    else:
        # Return an error message
        return {"error": f"Routine exercise with ID '{routine_exercise_id}' was not found."}, 404


# /routines/<int:routine_id>/<int:routine_exercise_id> - DELETE - Delete a specific routine exercise (must be owner or admin)
@routines_bp.route("/<int:routine_id>/<int:routine_exercise_id>", methods=["DELETE"])
@jwt_required()
@auth_as_admin_or_owner
def delete_routine_exercise(routine_id, routine_exercise_id):
    # Fetch specified routine exercise in URL
    stmt = db.select(RoutineExercise).filter_by(id=routine_exercise_id)
    routine_exercise = db.session.scalar(stmt)

    # If routine exercise exists:
    if routine_exercise:
        # Delete the routine exercise
        db.session.delete(routine_exercise)
        db.session.commit()

        # Return acknowledgement message
        return {"message": f"Routine exercise with ID '{routine_exercise_id}' has been deleted."}, 200
    
    else:
        return {"error": f"Routine exercise with ID '{routine_exercise_id}' not found."}, 404


# /routines/<int:routine_id>/like - POST - like a routine (must be logged in)
@routines_bp.route("/<int:routine_id>/like", methods=["POST"])
@jwt_required()
def like_routine(routine_id):
    # Get user identity
    user_id = get_jwt_identity()

    # Check if the routine exists (if not, return an error)
    stmt = db.select(Routine).filter_by(id=routine_id)
    routine = db.session.scalar(stmt)
    if not routine:
        return {"error": f"Routine with ID {routine_id} not found."}, 404

    # Check if the user has already liked this routine
    like_stmt = db.select(Like).filter_by(user_id=user_id)
    like_exists = db.session.scalar(like_stmt)
    if like_exists:
        return {"error": "You have already liked this routine."}, 400

    # Create a new like
    like = Like(
        user_id=user_id,
        routine_id=routine_id
    )

    # Add and commit to database
    db.session.add(like)
    db.session.commit()

    # Return a successfully liked message
    return {"message": f"Routine with ID '{routine_id}' liked successfully."}, 201


# /routines/<int:routine_id>/like - DELETE - Delete a like from a specific routine (must be logged in)
@routines_bp.route("/<int:routine_id>/like", methods=["DELETE"])
@jwt_required()
def unlike_routine(routine_id):
    # Get user identity
    user_id = get_jwt_identity()

    # Check if user has liked the routine
    like_stmt = db.select(Like).filter_by(user_id=user_id)
    like_exists = db.session.scalar(like_stmt)
    # If routine has not been liked
    if not like_exists:
        # Error message
        return {"error": "You have not liked this routine."}, 400

    # Delete the like
    db.session.delete(like_exists)
    db.session.commit()

    # Return a successfully unliked message
    return {"message": f"You have unliked routine with ID '{routine_id}' successfully."}, 200