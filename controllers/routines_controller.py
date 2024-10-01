from flask import Blueprint, request

from sqlalchemy import func

from models.user import User
from models.routine import Routine, routine_schema, routines_schema, VALID_TARGET
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

    # Fetch all public routines
    stmt = db.select(Routine).filter_by(public=True)

    # If user is logged in:
    if user_id:
        # Fetch user in database
        stmt = db.select(User).filter_by(id=user_id)
        logged_user = db.session.scalar(stmt)

        # If user is an admin:
        if logged_user.is_admin:
            # Query database for all routines in order of most recent
            stmt = db.select(Routine)

        # If user is not admin
        else:
            # Fetch from database Routines which are public OR routine has a associated user ID = logged in user
            stmt = db.select(Routine).filter(
                (Routine.public == True) | (Routine.user_id == user_id)
            )

    # Filter final stmt based on when Routine was created
    stmt = stmt.order_by(Routine.created.desc())

    # Execute query and return as list
    routines = db.session.scalars(stmt).all()

    # Check if any routines were found
    if not routines:
        return {"error": "Could not find any routines. We recommend you create one!"}, 404
    
    # Return respective list to each type of user
    return routines_schema.dump(routines), 200


# /routines/<str:target> - GET - Search for a public routine which targets a specific muscle group. User can also order the selected muscle group by popularity (how many likes), recent, and oldest using paramater query (e.g. ?sort=<filter> where filter can = popular, recent, oldest)
@routines_bp.route("/<target>", methods=["GET"])
@jwt_required(optional=True)
def get_target_routine(target):
    # Check if target is valid
    if target not in VALID_TARGET:
        return {"error": f"Invalid target group provided. Please search for a valid target. {', '.join(VALID_TARGET)}"}, 400

    # Fetch user_id if exists
    user_id = get_jwt_identity()

    # INITIAL QUERY with ALL routines filtered by target provided by user
    stmt = db.session.query(Routine).filter(Routine.target == target)

    # THIS SECTION TAKES THE FILTERED STATEMENT AND ORGANISES THE QUERY BASED OFF QUERY PARAMETER 'SORT' PROVIDED BY USER

    # Fetch 'sort' from query paramater if provided. Default to None if no paramater query provided by user
    sort = request.args.get("sort") or None

    # If user entered anything other than popular, recent or oldest AND query contains a value
    if sort not in ["popular", "recent", "oldest", None]:
        return {"error": "The provided filter query could not be recognised. Please provide a paramater query that exists ('popular', 'recent', 'oldest')."}, 400
    
    # If user provided popular:
    if sort == "popular":
        # Recreate query to allow for the count of likes for each routine
        stmt = stmt.outerjoin( # Perform an OUTERJOIN between initial query (filtered Routine Table) AND Like table where the routine id's match on both tables.
            Like, Routine.id == Like.routine_id).group_by( # GROUP Routine IDs together
                Routine.id).order_by( 
            func.count(Like.id).desc())  # Order by number of likes each Routine has.
    
    # If user provided oldest:
    elif sort == "oldest":
        # Order initial query by when routine was created (oldest to most recent)
        stmt = stmt.order_by(Routine.created.asc())
    
    # If user provided recent:
    elif sort == "recent":
        # Order initial query by when routine was created (most recent to oldest)
        stmt = stmt.order_by(Routine.created.desc())
    # Else
    else:
        # Order initial query by routine title as default
        stmt = stmt.order_by(Routine.routine_title.asc())

    # THIS SECTION FILTERS THE INTIAL QUERY WHICH IS DETERMINED BY USER STATUS (NOT LOGGED IN / LOGGED IN / ADMIN)

    # If user is logged in:
    if user_id:
        # Fetch user in database
        user_stmt = db.select(User).filter_by(id=user_id)
        logged_user = db.session.scalar(user_stmt)
        # If user is an admin:
        if logged_user.is_admin:
            # Leave statement as is (admin can see all)
            stmt = stmt
        # If user is not admin (but logged in)
        else:
            # Filter the initial query by public routines bitwise OR routines the user has created that are private
            stmt = stmt.filter(Routine.public == True) | (Routine.user_id == user_id, Routine.public == False)
    # Else (if user is not logged in)
    else:
        stmt = stmt.filter(Routine.public == True)

    # Execute query:
    routines = db.session.scalars(stmt).all()

    # Check if any routines were found
    if not routines:
        return {"error": "Could not find any routines."}, 404

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
    likes = db.session.scalars(stmt).all()

    # If user has likes:
    if likes:
        # Fetch routine IDs from each liked routine and store in 'routine_ids'
        routine_ids = []
        for like in likes:
            routine_ids.append(like.routine_id)

        # Select all routines from Routine table that match 'routine_ids' and order from newest to oldest
        # stmt = db.select(Routine).filter(Routine.id.in_(routine_ids)).order_by(Routine.created.desc())

        # JOIN the Routine and Like table by linking Routine(id) & Like(routine_id)
        # Filter by selecting the routines where the routine id = the routines the user has liked (from the list created previously)
        stmt = db.select(Routine).join(
            Like, Routine.id == Like.routine_id).filter(
                Routine.id.in_(routine_ids), Like.user_id == user_id).order_by(Like.created.desc())
        
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
    logged_user_id = get_jwt_identity()

    # Create an instance of a routine using the data from the JSON body. User_id is determined by jwt
    routine = Routine(
        routine_title = body_data.get("routine_title"),
        description = body_data.get("description"),
        target = body_data.get("target"),
        public = body_data.get("public"),
        user_id = logged_user_id
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

    if not routine:
        return {"error": f"Routine with id '{routine_id}' does not exist."}, 404
    
    if routine.public:
        return routine_schema.dump(routine), 200
    
    # Check if user is logged in / exists
    user_id = get_jwt_identity() 

    # If user exists / logged in
    if user_id:
        # If logged in user matches the user id on the routine OR is an admin
        if user_id == str(routine.user_id) or user_is_admin():
            # Return to user
            return routine_schema.dump(routine), 200
        else:
            return {"error": "Only admin or the owner of this resource can perform this action."}, 403
    else:
        return {"error": "Sorry, authorised access is required. Please log in for verification"}, 401


# /routines/<int:routine_id> - PUT/PATCH - update specific routine (must be owner or admin) NEEED TO FIX THIS. ERROR WITH CHANGING PUBLIC VALUE DOENS"T CHANGE WHEN REQUESTED
@routines_bp.route("/<int:routine_id>", methods=["PUT", "PATCH"])
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

    # If routine is originally public
    if routine.public is True:
        # Fetch updated value (either true or false) - validation completed in schema
        update_public = body_data.get('public')
        # If updated value is public = False
        if not update_public:
            # Remove all associated likes in likes table
            stmt = db.select(Like).filter_by(routine_id=routine_id)
            remove_likes = db.session.scalars(stmt)
            
            for like in remove_likes:
                db.session.delete(remove_likes)

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
@routines_bp.route("/<int:routine_id>/exercise/<int:routine_exercise_id>", methods=["GET"])
@jwt_required(optional=True)
def get_routine_exercise(routine_id, routine_exercise_id):
    # Fetch the routine in the URL
    stmt = db.select(Routine).filter_by(id=routine_id)
    routine = db.session.scalar(stmt)

    # Fetch the routine_exercise in the URL
    routine_ex_stmt = db.select(RoutineExercise).filter_by(id=routine_exercise_id)
    routine_exercise = db.session.scalar(routine_ex_stmt)

    # If routine does not exist
    if not routine:
        return {"error": f"Routine with ID {routine_id} does not exist."}, 404

    # If routine exercise does not exist
    if not routine_exercise:
        return {"error": f"Routine exercise with ID {routine_exercise_id} does not exist."}, 404

    # Fetch logged in user's ID 
    user_id = get_jwt_identity()
    user_stmt = db.select(User).filter_by(id=user_id)
    logged_user = db.session.scalar(user_stmt)
    
    # If routine is private
    if not routine.public:
        # If user is not logged in or 
        if not logged_user:
            return {"error": f"Sorry, authorised access is required. Please log in for verification"}, 401
        elif logged_user.id != routine.user_id:
            # Return error denying permission
            return {"error": f"Sorry, you do not have permission to view this routine exercise."}, 403

    # If routine_exercise does not belong to specified routine, provide error    
    if routine_exercise.routine_id != routine.id:
        return {"error": f"Routine with ID '{routine_id}' does not have a routine exercise with ID '{routine_exercise_id}'."}, 404

    # Fetch the routine exercise where routine_exercise's routine_id = routine's ID
    stmt = db.select(RoutineExercise).filter_by(id=routine_exercise_id)
    routine_exercise = db.session.scalar(stmt)

    return routine_exercise_schema.dump(routine_exercise), 200


# /routines/<int:routine_id>/<int:routine_exercise_id> - PUT/PATCH - Update a specific routine exercise (must be owner or admin)
@routines_bp.route("/<int:routine_id>/exercise/<int:routine_exercise_id>", methods=["PUT", "PATCH"])
@jwt_required()
@auth_as_admin_or_owner
def update_routine_exercise(routine_id, routine_exercise_id):
    # Get the data from the body of the request
    body_data = routine_exercise_schema.load(request.get_json())

    # Fetch the routine exercise
    stmt = db.select(RoutineExercise).filter_by(id=routine_exercise_id)
    routine_exercise = db.session.scalar(stmt)

    # If routine exercise does not exist
    if not routine_exercise:
        return {"error": f"Routine exercise with ID {routine_exercise_id} does not exist."}, 404
    
    # If routine_exercise does not belong to specified routine, provide error    
    if routine_exercise.routine_id != routine_id:
        return {"error": f"Routine with ID '{routine_id}' does not have a routine exercise with ID '{routine_exercise_id}'."}, 404


    routine_exercise.routine_id = routine_id
    routine_exercise.exercise_id = body_data.get("exercise_id") or routine_exercise.exercise_id
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
    return routine_exercise_schema.dump(routine_exercise), 200


# /routines/<int:routine_id>/<int:routine_exercise_id> - DELETE - Delete a specific routine exercise (must be owner or admin)
@routines_bp.route("/<int:routine_id>/exercise/<int:routine_exercise_id>", methods=["DELETE"])
@jwt_required()
@auth_as_admin_or_owner
def delete_routine_exercise(routine_id, routine_exercise_id):
    # Fetch specified routine exercise in URL
    stmt = db.select(RoutineExercise).filter_by(id=routine_exercise_id)
    routine_exercise = db.session.scalar(stmt)

    # If routine exercise does not exist
    if not routine_exercise:
        return {"error": f"Routine exercise with ID {routine_exercise_id} does not exist."}, 404
    
    # If routine_exercise does not belong to specified routine, provide error    
    if routine_exercise.routine_id != routine_id:
        return {"error": f"Routine with ID '{routine_id}' does not have a routine exercise with ID '{routine_exercise_id}'."}, 404

    # For better error message:
    # Fetch specified routine exercise name and routine title
    routine_title = routine_exercise.routine.routine_title
    exercise_name = routine_exercise.exercise.exercise_name

    # Delete the routine exercise
    db.session.delete(routine_exercise)
    db.session.commit()

    # Return acknowledgement message
    return {"message": f"The exercise '{exercise_name}' has been deleted from the routine named '{routine_title}'."}, 200


# /routines/<int:routine_id>/like - POST - like a routine (must be logged in)
@routines_bp.route("/<int:routine_id>/like", methods=["POST"])
@jwt_required()
def like_routine(routine_id):
    # Get user identity
    user_id = get_jwt_identity()

    # Check if the routine exists (if not, return an error)
    stmt = db.select(Routine).filter_by(id=routine_id)
    routine = db.session.scalar(stmt)

    # If routine doesn't exist
    if not routine:
        # Return an error
        return {"error": f"Routine with ID {routine_id} not found."}, 404

    if not routine.public:
        return {"error": f"Only public routines can be liked."}, 403

    # Check if the user has already liked this routine
    like_stmt = db.select(Like).filter_by(user_id=user_id, routine_id=routine_id)
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
    return {"message": f"You have successly liked Routine with ID '{routine_id}' named {routine.routine_title}."}, 201


# /routines/<int:routine_id>/like - DELETE - Delete a like from a specific routine (must be logged in)
@routines_bp.route("/<int:routine_id>/like", methods=["DELETE"])
@jwt_required()
def unlike_routine(routine_id):
    # Get user identity
    user_id = get_jwt_identity()

    # Check if the routine exists (if not, return an error)
    stmt = db.select(Routine).filter_by(id=routine_id)
    routine = db.session.scalar(stmt)

    # If routine doesn't exist
    if not routine:
        # Return an error
        return {"error": f"Routine with ID {routine_id} not found."}, 404

    # Check if user has liked the this specific routine
    like_stmt = db.select(Like).filter_by(user_id=user_id, routine_id=routine_id)
    like_exists = db.session.scalar(like_stmt)

    # If routine has not been liked
    if not like_exists:
        # Error message
        return {"error": "You have not liked this routine."}, 400

    # Delete the like
    db.session.delete(like_exists)
    db.session.commit()

    # Return a successfully unliked message
    return {"message": f"You have unliked routine with ID '{routine_id}' named {routine.routine_title} successfully."}, 200