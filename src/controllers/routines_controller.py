# Import Blueprint & request for better organisation and route management
from flask import Blueprint, request

# Import the func module for database SQL functions (count likes)
from sqlalchemy import func

# Import models and schemas required for object creation and to serialise/deserialise data
from models.user import User
from models.exercise import Exercise
from models.routine import Routine, routine_schema, routines_schema, VALID_TARGET
from models.routine_exercise import RoutineExercise, routine_exercise_schema
from models.like import Like

# Import SQLAlchemy database for database operations
from init import db

# Import from utils.py:
# auth_as_admin_or_owner: decorator which checks if logged in user has authorisation to access the decorated route
# user_is_admin: function which checks if logged in user is admin
from utils import auth_as_admin_or_owner, user_is_admin

# Import authentication libraries
# jwt_required: decorator which checks if user logged in
# get_jwt_identity: function which grabs the logged in users user ID
from flask_jwt_extended import jwt_required, get_jwt_identity

# Create a blueprint named "routines". Also decorate with url_prefix for management of routes.
routines_bp = Blueprint("routines", __name__, url_prefix="/routines")


# /routines - GET - fetch all public routines + personal private routines if logged in. Admin can see all. Allows users to see what the newest routines which have been added or updated by other users
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

    # Filter final stmt based on when Routine was last_updated
    stmt = stmt.order_by(Routine.last_updated.desc())

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
    # Adjust user input to match format of VALID_TARGET for ease of entry
    target = target.lower().capitalize()
    
    # Check if target is valid
    if target not in VALID_TARGET:
        return {"error": f"Invalid target group provided. Please search for a valid target. {', '.join(VALID_TARGET)}"}, 400

    # Fetch user_id if exists
    user_id = get_jwt_identity()

    # INITIAL QUERY with ALL routines filtered by target provided by user
    stmt = db.select(Routine).filter_by(target=target)

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
        # Order initial query by when routine was last_updated (oldest to most recent)
        stmt = stmt.order_by(Routine.last_updated.asc())
    
    # If user provided recent:
    elif sort == "recent":
        # Order initial query by when routine was last_updated (most recent to oldest)
        stmt = stmt.order_by(Routine.last_updated.desc())
    # Else
    else:
        # Order initial query by routine title as default
        stmt = stmt.order_by(Routine.routine_title.asc())

    # THIS SECTION FILTERS THE INITIAL QUERY WHICH IS DETERMINED BY USER STATUS (NOT LOGGED IN / LOGGED IN / ADMIN)

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

# /routines/<int:routine_id>/copy - POST - Copy another user's routine as personal private routine
@routines_bp.route("/<int:routine_id>/copy", methods=["POST"])
@jwt_required()  # User must be logged in
def copy_routine(routine_id):
    # Fetch the routine ID the user wants to copy in URL
    stmt = db.select(Routine).filter_by(id=routine_id)
    routine_to_copy = db.session.scalar(stmt)
    
    # Check if routine exists and routine is not private. If any, return an appropriate error message
    if not routine_to_copy:
        return {"error": f"Routine with id '{routine_id}' does not exist."}, 404
    if not routine_to_copy.public:
        return {"error": "Access denied: Only public routines can be copied."}, 403
    
    # Get logged in user's ID
    user_id = get_jwt_identity()

    # Copy the routine details
    copied_routine = Routine(
        routine_title=f"{routine_to_copy.routine_title} (Copied from {routine_to_copy.user.username}", # Suffix to identify routine was copied
        description=routine_to_copy.description,
        target=routine_to_copy.target,
        public=False,  # Set the copied routine to private by default
        user_id=user_id  # Set user ID to logged in user's ID
    )

    # Add copied routine to the database
    db.session.add(copied_routine)
    # Call db.session.flush to allow access to added changes before committing to database
    db.session.flush()

    # For each routine_exercise that was part of the original routine
    for exercise in routine_to_copy.routine_exercises:
        # Copy the exercise details for each exercise
        copied_exercise = RoutineExercise(
            routine_id=copied_routine.id, # set associated routine ID as the new copied routine ID
            exercise_id=exercise.exercise_id,
            sets=exercise.sets,
            reps=exercise.reps,
            weight=exercise.weight,
            distance_km=exercise.distance_km,
            minutes=exercise.minutes,
            seconds=exercise.seconds,
            note=exercise.note
        )
        # Add each copied exercise object into the session
        db.session.add(copied_exercise)

    # Commit all changes (new copied routine + associated exercises)
    db.session.commit()

    # Return successful message along with 
    return {"message": "The routine has been copied successfully!", "details": routine_schema.dump(copied_routine)}, 201

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
    # Attempt to select the routine from the database based off routine ID provided in URL
    stmt = db.select(Routine).filter_by(id=routine_id)

    # Execute the query
    routine = db.session.scalar(stmt)

    # If routine was not found from the previous query
    if not routine:
        # Return an error message stating the routine does not exist
        return {"error": f"Routine with id '{routine_id}' does not exist."}, 404
    # If routine exists and is public
    if routine.public:
        # Return routine to user
        return routine_schema.dump(routine), 200
    
    # If routine is not public, check if user is logged in / exists
    user_id = get_jwt_identity() 

    # If user exists / logged in
    if user_id:
        # If logged in user matches the user id on the routine OR is an admin
        if user_id == str(routine.user_id) or user_is_admin():
            # Return to user
            return routine_schema.dump(routine), 200
        # Else (if user is not the owner or admin)
        else:
            # Return forbidden error message
            return {"error": "Only admin or the owner of this resource can perform this action."}, 403
    # Else (if user is not logged in)
    else:
        # Return unauthorised error message
        return {"error": "Sorry, authorised access is required. Please log in for verification"}, 401


# /routines/<int:routine_id> - PUT/PATCH - update specific routine (must be owner or admin)
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
    if routine.public:
        # Fetch updated value (either true or false) - validation completed in schema
        update_public = body_data.get('public')
        # If updated value is public = False and the field is not None (i.e. the user has explicitly provided an input which = False)
        if update_public is not None and not update_public:
            # Select all associated likes in Like table
            stmt = db.select(Like).filter_by(routine_id=routine_id)
            remove_likes = db.session.scalars(stmt)
            # For each selected like, delete from database
            for like in remove_likes:
                db.session.delete(like)

    # If routine is not originally public and exists, update attributes (if provided)
    routine.routine_title = body_data.get('routine_title', routine.routine_title)
    routine.description = body_data.get('description', routine.description)
    routine.target = body_data.get('target', routine.target)
    routine.public = body_data.get('public', routine.public)

    # Commit changes to database
    db.session.commit()

    # Return updated routine to user
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


# /routines/<int:routine_id>/exercise - POST - add a routine_exercise to a routine (must be owner of routine or admin)
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

    # Check if the exercise exists
    exercise_id = body_data.get('exercise_id')
    exer_stmt = db.select(Exercise).filter_by(id=exercise_id)
    exercise_exists = db.session.scalar(exer_stmt)

    # If exercise does not exist
    if not exercise_exists:
        # Return not found error
        return {"error": f"Exercise with ID {exercise_id} does not exist."}, 404

    # Create a new object of an exercise routine based off body data - attach to specified routine ID in URL
    routine_exercise = RoutineExercise(
        routine_id = routine_id,
        exercise_id = exercise_id,
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

    # If routine does not exist
    if not routine:
        return {"error": f"Routine with ID {routine_id} does not exist."}, 404

    # Fetch the routine_exercise in the URL
    routine_ex_stmt = db.select(RoutineExercise).filter_by(id=routine_exercise_id)
    routine_exercise = db.session.scalar(routine_ex_stmt)

    # If routine exercise does not exist
    if not routine_exercise:
        return {"error": f"Routine exercise with ID {routine_exercise_id} does not exist."}, 404

    # If routine_exercise does not belong to specified routine, provide error    
    if routine_exercise.routine_id != routine.id:
        return {"error": f"Routine with ID '{routine_id}' does not have a routine exercise with ID '{routine_exercise_id}'."}, 404

    # Fetch logged in user's ID 
    user_id = get_jwt_identity()
    user_stmt = db.select(User).filter_by(id=user_id)
    logged_user = db.session.scalar(user_stmt)
    
    # If routine is private
    if not routine.public:
        # If user is not logged in or 
        if not logged_user:
            return {"error": f"Sorry, authorised access is required. Please log in for verification"}, 401
        # If logged in user's ID does not match user ID associated with routine.
        elif logged_user.id != routine.user_id:
            # Return error denying permission
            return {"error": f"Sorry, you do not have permission to view this routine exercise."}, 403

    # Fetch the routine exercise where routine_exercise's routine_id = routine's ID
    stmt = db.select(RoutineExercise).filter_by(id=routine_exercise_id)
    routine_exercise = db.session.scalar(stmt)

    return routine_exercise_schema.dump(routine_exercise), 200


# /routines/<int:routine_id>/<int:routine_exercise_id> - PUT/PATCH - Update a specific routine exercise (must be owner or admin)
@routines_bp.route("/<int:routine_id>/exercise/<int:routine_exercise_id>", methods=["PUT", "PATCH"])
@jwt_required()
@auth_as_admin_or_owner # Verify if logged in user is owner of the routine ID or is admin
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
    
    # Check if the exercise exists
    exercise_id = body_data.get('exercise_id')
    exer_stmt = db.select(Exercise).filter_by(id=exercise_id)
    exercise_exists = db.session.scalar(exer_stmt)

    # If exercise does not exist
    if not exercise_exists:
        # Return not found error
        return {"error": f"Exercise with ID {exercise_id} does not exist."}, 404

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
@auth_as_admin_or_owner # Verify if logged in user is owner of the routine ID or is admin
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
    # Fetch the exercise name and routine title from the specified routine in the URL
    routine_title = routine_exercise.routine.routine_title
    exercise_name = routine_exercise.exercise.exercise_name

    # Delete the routine exercise
    db.session.delete(routine_exercise)
    db.session.commit()

    # Return acknowledgement message
    return {"message": f"The exercise '{exercise_name}' has been deleted from the routine named '{routine_title}'."}, 200


# /routines/<int:routine_id>/like - POST - like a routine (must be logged in)
@routines_bp.route("/<int:routine_id>/like", methods=["POST"])
@jwt_required() # User must be logged in to assign their user ID to the newly created like.
def like_routine(routine_id):
    # Check if the routine exists (if not, return an error)
    stmt = db.select(Routine).filter_by(id=routine_id)
    routine = db.session.scalar(stmt)

    # If routine doesn't exist
    if not routine:
        # Return an error
        return {"error": f"Routine with ID {routine_id} not found."}, 404

    if not routine.public:
        return {"error": f"Only public routines can be liked."}, 403

    # Get user identity to perform below checks
    user_id = get_jwt_identity()

    # Check if the user has already liked this routine (filter like table by user ID and routine ID specified in URL)
    like_stmt = db.select(Like).filter_by(user_id=user_id, routine_id=routine_id)
    like_exists = db.session.scalar(like_stmt)
    # If user has liked the routine
    if like_exists:
        # Return error message (each routine can only be liked once)
        return {"error": "You have already liked this routine."}, 400

    # If like doesn't exist, create a new like
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
@jwt_required() # Check if used is logged in
def unlike_routine(routine_id):
    # Check if the routine exists (if not, return an error)
    stmt = db.select(Routine).filter_by(id=routine_id)
    routine = db.session.scalar(stmt)

    # If routine doesn't exist
    if not routine:
        # Return an error
        return {"error": f"Routine with ID {routine_id} not found."}, 404

    # Get user identity to perform below checks
    user_id = get_jwt_identity()

    # Check if user has liked the this specific routine (filter like table by user ID and routine ID specified in URL)
    like_stmt = db.select(Like).filter_by(user_id=user_id, routine_id=routine_id)
    like_exists = db.session.scalar(like_stmt)

    # If routine has not been liked
    if not like_exists:
        # Error message
        return {"error": "You have not liked this routine."}, 400

    # If like does exist, delete the like
    db.session.delete(like_exists)
    db.session.commit()

    # Return a successfully unliked message
    return {"message": f"You have unliked routine with ID '{routine_id}' named {routine.routine_title} successfully."}, 200