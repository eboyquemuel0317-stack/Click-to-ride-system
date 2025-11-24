import pytz
from . import db  # Import the database instance
from datetime import datetime  # Import datetime for handling date and time
from werkzeug.security import generate_password_hash, check_password_hash  # Import security functions for password hashing

class Admin(db.Model):
    __tablename__ = 'admins'  # Table name for the Admin model
    id = db.Column(db.Integer, primary_key=True)  # Primary key for the admin
    username = db.Column(db.String(50), unique=True, nullable=False)  # Unique username for the admin
    password_hash = db.Column(db.String(200), nullable=False)  # Hashed password for security

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)  # Hash the password before storing

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)  # Verify the hashed password

def philippine_time_now():
    return datetime.now(pytz.timezone('Asia/Manila'))

class Booking(db.Model):
    __tablename__ = 'bookings'  # Table name for the Booking model
    
    # Define the columns for the 'bookings' table and set their properties with nullable constraints
    id = db.Column(db.Integer, primary_key=True)  # Primary key for the booking
    booking_code = db.Column(db.String(20), unique=True, nullable=False)  # Unique code for the booking
    customer_name = db.Column(db.String(100), nullable=False)  # Name of the customer
    contact_number = db.Column(db.String(20))  # Optional contact number
    email = db.Column(db.String(100))  # Optional email address  
    route_from = db.Column(db.String(50), nullable=False)  # Starting route
    route_to = db.Column(db.String(50), nullable=False)  # Destination route
    travel_date = db.Column(db.Date, nullable=False)  # Date of travel
    departure_time = db.Column(db.String(10), nullable=False)  # Time of departure
    passengers = db.Column(db.Integer, nullable=False)  # Number of passengers
    price = db.Column(db.String(20), nullable=False)  # Price of the booking
    route_duration = db.Column(db.String(20))  # Duration of the route
    route_color = db.Column(db.String(20))  # Color associated with the route
    status = db.Column(db.String(20), default='pending')  # Status of the booking
    created_at = db.Column(db.DateTime, default=philippine_time_now)  # Timestamp when the booking was created
    
    # Define how the object is represented as a string
    def __repr__(self):
        return f'<Booking {self.booking_code} - {self.customer_name}>'
    
    # Convert the Booking object into a dictionary format
    def to_dict(self):
        return {
            'id': self.id,
            'booking_code': self.booking_code,
            'customer_name': self.customer_name,
            'contact_number': self.contact_number,
            'email': self.email,
            'route_from': self.route_from,
            'route_to': self.route_to,
            'travel_date': self.travel_date.strftime('%Y-%m-%d'),  # Format the travel date as a string
            'departure_time': self.departure_time,
            'passengers': self.passengers,
            'price': self.price,
            'route_duration': self.route_duration,
            'route_color': self.route_color,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')  # Format the created_at timestamp as a string
        }

"""
File: model.py
Purpose: Define database models for Click to Ride system using SQLAlchemy.
Features include:
- Admin model for managing admin users with secure password hashing
- Booking model for storing reservation details including route, passenger info, date, time, and status
- philippine_time_now() function to generate current time in Philippine timezone
- Booking.to_dict() method to convert booking objects to dictionary for API or template rendering
Notes:
- Passwords are hashed using Werkzeug security functions
- The Booking model includes default status 'pending' and auto-generated creation timestamp
- Route color and duration can be used for UI representation
"""
