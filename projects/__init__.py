from flask import Flask  # Import Flask class from flask module
from flask_sqlalchemy import SQLAlchemy  # Import SQLAlchemy class for database management
import secrets  # Import secrets module for generating secure tokens

db = SQLAlchemy()  # Initialize SQLAlchemy instance

def create_app():
    app = Flask(__name__)  # Create a Flask application instance
    
    # Configuration
    app.config['SECRET_KEY'] = secrets.token_hex(16)  # Generate a random secret key
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookings.db'  # Database URI for SQLite
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable track modifications

    # Initialize database
    db.init_app(app)  # Bind the app to the database

    # Register blueprints/routes
    from .route import main_bp  # Import main blueprint
    from .auth import auth_bp  # Import authentication blueprint

    app.register_blueprint(main_bp)  # Register main blueprint
    app.register_blueprint(auth_bp)  # Register authentication blueprint

    # Import models inside app context to avoid circular import
    with app.app_context():
        from .model import Admin  # Import Admin model
        db.create_all()  # Create database tables

        # Create default admin if not exists
        if not Admin.query.filter_by(username='admin').first():  # Check if admin exists
            default_admin = Admin(username='admin')  # Create default admin
            default_admin.set_password('admin123')  # Set password for default admin
            db.session.add(default_admin)  # Add default admin to session
            db.session.commit()  # Commit the session

    return app  # Return the Flask app instance

"""
File: __init__.py
Purpose: Entry point for the Click to Ride Flask application.
Features include:
- Initializes Flask app with configuration settings
- Sets up SQLAlchemy database for bookings and admin management
- Registers blueprints for main routes and authentication
- Automatically creates database tables on first run
- Creates a default admin user with username 'admin' and password 'admin123' if not present
- Uses a securely generated SECRET_KEY for session management
Notes:
- The database used is SQLite (bookings.db)
- Ensure proper import of models to avoid circular dependencies
- Application instance is returned for running with Flask
"""

