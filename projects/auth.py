from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from . import db
from .model import Admin

# Create a Blueprint for authentication
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Handle login logic
    if request.method == 'POST':
        username = request.form.get('username')  # Get username from form
        password = request.form.get('password')  # Get password from form
        admin = Admin.query.filter_by(username=username).first()  # Query admin by username

        # Check if admin exists and password is correct
        if admin and admin.check_password(password):
            session['admin_id'] = admin.id  # Store admin ID in session
            flash('Login successful.', 'success')  # Flash success message
            return redirect(url_for('main.admin_bookings'))  # Redirect to admin bookings
        else:
            flash('Invalid username or password.', 'danger')  # Flash error message

    return render_template('login.html')  # Render login template

@auth_bp.route('/logout')
def logout():
    session.pop('admin_id', None)  # Remove admin ID from session
    flash('You have been logged out.', 'info')  # Flash logout message
    return redirect(url_for('auth.login'))  # Redirect to login page

"""
File: auth.py
Purpose: Authentication blueprint for Click to Ride system.
Features include:
- Provides routes for admin login and logout
- Validates admin credentials using the Admin model
- Stores admin session upon successful login
- Displays flash messages for login success, failure, and logout
- Redirects to appropriate pages based on authentication status
Notes:
- Uses Flask session to maintain admin login state
- Template used for login page: login.html
- Integrates with main blueprint for admin bookings page
"""
