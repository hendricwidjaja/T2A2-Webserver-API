from flask import Blueprint

from init import db, bcrypt

from models.user import User
from models.exercise import Exercise

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
            username = "Admin",
            firstname = "Admin",
            lastname = "Admin",
            email = "admin@email.com",
            password = bcrypt.generate_password_hash("123456").decode("utf-8"),
            is_admin = True
        ),
        User(
            username = "User A",
            firstname = "John",
            lastname = "Doe",
            email = "usera@email.com",
            password = bcrypt.generate_password_hash("123456").decode("utf-8")
        ),
        User(
            username = "User B",
            firstname = "Julie",
            lastname = "Doe",
            email = "userb@email.com",
            password = bcrypt.generate_password_hash("123456").decode("utf-8")
        )
    ]

    db.session.add_all(users)

    exercises = [
        Exercise(
            exercise_name = "Barbell Bench Press",
            description = "A chest building exercise which also trains the triceps and shoulders",
            body_part = "Chest",
            public = True,
            user = users[0]
        ),
        Exercise(
            exercise_name = "Deadlift",
            description = "A back building exercise which also trains the glutes, hamstrings, core and traps",
            body_part = "Back",
            public = True,
            user = users[0]
        ),
        Exercise(
            exercise_name = "Squat",
            description = "A leg building exercise which also trains the core",
            body_part = "Legs",
            public = True,
            user = users[0]
        ),
        Exercise(
            exercise_name = "Shoulder Press",
            description = "A shoulder building exercise which also trains the triceps",
            body_part = "Shoulders",
            public = True,
            user = users[0]
        ),
        Exercise(
            exercise_name = "DB Bicep Curls",
            description = "A bicep building exercise.",
            body_part = "Biceps",
            public = True,
            user = users[0]
        ),
        Exercise(
            exercise_name = "Cable Rope Tricep Extensions",
            description = "A tricep building exercise",
            body_part = "Triceps",
            public = True,
            user = users[0]
        ),
        Exercise(
            exercise_name = "Crunches",
            description = "A core building exercise",
            body_part = "Core",
            public = True,
            user = users[0]
        ),
        Exercise(
            exercise_name = "Jog",
            description = "A cardio building exercise. Zone 2 Cardio.",
            body_part = "Cardio",
            public = True,
            user = users[0]
        )
    ]

    db.session.add_all(exercises)

    db.session.commit()

    print("Tables seeded!")

@db_commands.cli.command("drop")
def drop_tables():
    db.drop_all()
    print("Tables dropped.")