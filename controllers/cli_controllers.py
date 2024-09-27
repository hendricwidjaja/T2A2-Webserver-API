from flask import Blueprint

from init import db, bcrypt

from models.user import User
from models.exercise import Exercise
from models.routine import Routine
from models.routine_exercise import RoutineExercise
from models.like import Like

db_commands = Blueprint("db", __name__)

@db_commands.cli.command("create")
def create_tables():
    db.create_all()
    print("Tables created!")

@db_commands.cli.command("seed")
def seed_tables():
    # Create a list of User instances
    users = [
        User(
            username = "Deleted_Account",
            firstname = "Deleted Account",
            lastname = "Deleted Account",
            email = "deleted@email.com",
            password = bcrypt.generate_password_hash("abc123!").decode("utf-8"),
            is_admin = True
        ),
        User(
            username = "Admin",
            firstname = "Admin",
            lastname = "Admin",
            email = "admin@email.com",
            password = bcrypt.generate_password_hash("abc123!").decode("utf-8"),
            is_admin = True
        ),
        User(
            username = "Test.User_A",
            firstname = "John",
            lastname = "Doe",
            email = "usera@email.com",
            password = bcrypt.generate_password_hash("abc123!").decode("utf-8")
        ),
        User(
            username = "Test.User_B",
            firstname = "Julie",
            lastname = "Doe",
            email = "userb@email.com",
            password = bcrypt.generate_password_hash("abc123!").decode("utf-8")
        )
    ]

    db.session.add_all(users)

    exercises = [
        Exercise(
            exercise_name = "Barbell Bench Press",
            description = "A chest building exercise which also trains the triceps and shoulders",
            body_part = "Chest",
            user = users[1]
        ),
        Exercise(
            exercise_name = "Deadlift",
            description = "A back building exercise which also trains the glutes, hamstrings, core and traps",
            body_part = "Back",
            user = users[1]
        ),
        Exercise(
            exercise_name = "Squat",
            description = "A leg building exercise which also trains the core",
            body_part = "Legs",
            user = users[1]
        ),
        Exercise(
            exercise_name = "Shoulder Press",
            description = "A shoulder building exercise which also trains the triceps",
            body_part = "Shoulders",
            user = users[1]
        ),
        Exercise(
            exercise_name = "DB Bicep Curls",
            description = "A bicep building exercise.",
            body_part = "Biceps",
            user = users[1]
        ),
        Exercise(
            exercise_name = "Cable Rope Tricep Extensions",
            description = "A tricep building exercise",
            body_part = "Triceps",
            user = users[1]
        ),
        Exercise(
            exercise_name = "Crunches",
            description = "A core building exercise",
            body_part = "Core",
            user = users[1]
        ),
        Exercise(
            exercise_name = "Jog",
            description = "A cardio building exercise. Zone 2 Cardio.",
            body_part = "Cardio",
            user = users[1]
        ),
        Exercise(
            exercise_name = "UserA Chest Exercise",
            description = "A chest building exercise.",
            body_part = "Chest",
            user = users[2]
        ),
        Exercise(
            exercise_name = "UserA Shoulder Exercise",
            description = "A shoulders building exercise.",
            body_part = "Shoulders",
            user = users[2]
        ),
        Exercise(
            exercise_name = "UserA Legs Exercise",
            description = "A legs building exercise.",
            body_part = "Legs",
            user = users[2]
        ),
        Exercise(
            exercise_name = "User B Back Exercise",
            description = "A back building exercise.",
            body_part = "Back",
            user = users[3]
        ),
        Exercise(
            exercise_name = "User B Shoulders Exercise",
            description = "A shoulders building exercise.",
            body_part = "Shoulders",
            user = users[3]
        ),
        Exercise(
            exercise_name = "User B Chest Exercise",
            description = "A chest building exercise.",
            body_part = "Chest",
            user = users[3]
        )
    ]

    db.session.add_all(exercises)

    routines = [
        Routine(
            routine_title = "User A FullBody Workout",
            description = "This workout is a killer! Targets all body parts. Try to complete in 60min",
            target = "Full Body",
            user = users[2]
        ),
        Routine(
            routine_title = "User B Upper Body Workout",
            description = "This workout is a killer! Targets upper body parts. Try to complete in 60min",
            target = "Upper Body",
            public = False,
            user = users[3]
        ),
        Routine(
            routine_title = "User A Push Workout",
            description = "This workout is a killer! Targets chest, shoulders and triceps. Try to complete in 60min",
            target = "Push Workout",
            public = True,
            user = users[2]
        ),
        Routine(
            routine_title = "User B Cardio Workout",
            description = "Zone 2 cardio workout. Keep your heart rate below 120 bpm",
            target = "Cardio",
            public = True,
            user = users[3]
        )
    ]

    db.session.add_all(routines)

    routine_exercises = [
        RoutineExercise(
            routine = routines[0],
            exercise = exercises[0],
            sets = 3,
            reps = 10,
            weight = 60,
            note = "Focus on form, keep chest up"
        ),
        RoutineExercise(
            routine = routines[0],
            exercise = exercises[1],
            sets = 3,
            reps = 8,
            weight = 100,
            note = "Complete with only 30 seconds rest inbetween sets for stronger burn"
        ),
        RoutineExercise(
            routine = routines[0],
            exercise = exercises[2],
            sets = 3,
            reps = 12,
            weight = 45,
            note = "Insert note here"
        ),
        RoutineExercise(
            routine = routines[1],
            exercise = exercises[3],
            sets = 3,
            reps = 15,
            weight = 40,
            note = "Insert note here"
        ),
        RoutineExercise(
            routine = routines[1],
            exercise = exercises[4],
            sets = 3,
            reps = 12,
            weight = 45,
            note = "Insert note here"
        ),
        RoutineExercise(
            routine = routines[1],
            exercise = exercises[5],
            sets = 5,
            reps = 6,
            weight = 120,
            note = "Insert note here"
        ),
        RoutineExercise(
            routine = routines[2],
            exercise = exercises[6],
            sets = 3,
            reps = 8,
            weight = 15,
            note = "Insert note here"
        ),
        RoutineExercise(
            routine = routines[2],
            exercise = exercises[8],
            sets = 3,
            reps = 10,
            weight = 20,
            note = "Insert note here"
        ),
        RoutineExercise(
            routine = routines[2],
            exercise = exercises[9],
            sets = 3,
            reps = 12,
            weight = 45,
            note = "Insert note here"
        ),
        RoutineExercise(
            routine = routines[3],
            exercise = exercises[7],
            distance_km = 5,
            minutes = 20,
            seconds = 45,
            note = "Insert note here"
        )
    ]

    db.session.add_all(routine_exercises)

    likes = [
        Like(
            user = users[2],
            routine = routines[0]
        ),
        Like(
            user = users[2],
            routine = routines[1]
        ),
        Like(
            user = users[2],
            routine = routines[2]
        ),
        Like(
            user = users[2],
            routine = routines[3]
        ),
        Like(
            user = users[3],
            routine = routines[0]
        )
    ]

    db.session.add_all(likes)

    db.session.commit()

    print("Tables seeded!")

@db_commands.cli.command("drop")
def drop_tables():
    db.drop_all()
    print("Tables dropped.")