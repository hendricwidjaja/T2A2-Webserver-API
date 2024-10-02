import os # Import os for environment functionality
from flask import Flask # Import flask to create flask application
from marshmallow.exceptions import ValidationError # Import ValidationError to utlise in app.errorhandler
from sqlalchemy.exc import IntegrityError # Import IntegrityError to utilise in app.errorhandler

# Import sqlalchemy, mashmallow, bcrypt and JWTManager to be initialised
from init import db, ma, bcrypt, jwt

# Import all blueprints for registration
from controllers.cli_controllers import db_commands
from controllers.auth_controller import auth_bp
from controllers.exercises_controller import exercises_bp
from controllers.routines_controller import routines_bp

# Create Flask app
def create_app():
    app = Flask(__name__)

    # Configure connection to database. Retrieve DATABASE_URL & JWT_SECRET_KEY from .env 
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")

    # Initialise database, marshmallow, bcrypt and JWT with flask app
    db.init_app(app)
    ma.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # GLOBAL ERROR HANDLERS IN ORDER OF SPECIFICITY

    # Global ValidationError handle. If validation error occurs, returns error message with 400 HTTP status (bad request).
    @app.errorhandler(ValidationError)
    def validation_error(err):
        return {"error": err.messages}, 400

    # Global IntegrityError handler. If integrity error occurs, rolls back session and returns error message with 400 HTTP status (bad request).
    @app.errorhandler(IntegrityError)
    def integrity_error(err):
        db.session.rollback()
        return {"error": "An unexpected database integrity error has occurred. To prevent any loss, we've rolled back any changes you've made."}, 400
    
    # Global JWT authentication/unauthorised access error handler. Custom error message requesting user to log in.
    @jwt.unauthorized_loader
    def unauthorised_response(callback):
        return {"error": "Unauthorized access detected. Please log in for verification!"}, 401
    
    # Global 404 (not found) error handler. Provides a customer error message.
    @app.errorhandler(404)
    def incorrect_route(err):
        return {"error": "This route doesn't exist. Try again :( "}, 404
    
    # Global 405 (Method not allowed) error handler. To assist scenarios where user provides incorrect inputs that are unrecognisable (e.g. incorrect routes)
    @app.errorhandler(405)
    def incorrect_route(err):
        return {"error": "Unknown error, please ensure all routes and inputs have been inserted correctly"}, 405
    
    @app.errorhandler(Exception)
    def exceptions(err):
        db.session.rollback()
        return {"error": "An unexpected error occured", "details": str(err)}, 500

    # Register all blueprints
    app.register_blueprint(db_commands)
    app.register_blueprint(auth_bp)
    app.register_blueprint(exercises_bp)
    app.register_blueprint(routines_bp)

    return app