import secrets  # Importing the secrets module for generating secure tokens
import pytz # local time zone
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash  # Importing necessary Flask components
from datetime import datetime, timedelta  # Importing datetime and timedelta for date manipulation
from . import db  # Importing the database instance
from .model import Booking  # Importing the Booking model
from math import ceil
from sqlalchemy import func



main_bp = Blueprint('main', __name__)  # Creating a Blueprint for the main application

# Route data
ROUTES = [  # List of available routes for booking
    {
        'id': 1,
        'from': 'CALBAYOG',
        'to': 'PEÑA',
        'duration': '45 mins',
        'price': '₱ 55',
        'color': 'blue'
    },
    {
        'id': 2,
        'from': 'CALBAYOG',
        'to': 'TARABUKAN',
        'duration': '1 hr',
        'price': '₱ 60',
        'color': 'pink'
    },
    {
        'id': 3,
        'from': 'TARABUKAN',
        'to': 'CALBAYOG',
        'duration': '1 hr',
        'price': '₱ 60',
        'color': 'orange'
    },
    {
        'id': 4,
        'from': 'PEÑA',
        'to': 'CALBAYOG',
        'duration': '45 mins',
        'price': '₱ 55',
        'color': 'green'
    }
]

def generate_booking_code():
    # Generate a unique booking code using a random hex string
    return 'VR' + secrets.token_hex(3).upper()

@main_bp.route('/')
def index():
    # Render the homepage with the list of available routes
    # Local time zone
    ph_tz = pytz.timezone('Asia/Manila')
    return render_template('index.html', routes=ROUTES, current_year=datetime.now(ph_tz).year)

@main_bp.route('/reserve', methods=['POST'])
def reserve():
    # Handle reservation form submission
    # Extract form data
    route_id = int(request.form.get('route_id'))
    name = request.form.get('name')
    contact_number = request.form.get('contact')
    email = request.form.get('email')
    date = request.form.get('date')
    time = request.form.get('time')
    passengers = int(request.form.get('passengers'))
    
    # Find the selected route by ID
    selected_route = next((r for r in ROUTES if r['id'] == route_id), None)
    
    if not selected_route:
        # Redirect to homepage if route is not found
        return redirect(url_for('main.index'))
    
    # Generate a unique booking code
    booking_code = generate_booking_code()
    
    # Create a new booking record in the database
    new_booking = Booking(
        booking_code=booking_code,
        customer_name=name,
        contact_number=contact_number,
        email=email,
        route_from=selected_route['from'],
        route_to=selected_route['to'],
        travel_date=datetime.strptime(date, '%Y-%m-%d').date(),
        departure_time=time,
        passengers=passengers,
        price=selected_route['price'],
        route_duration=selected_route['duration'],
        route_color=selected_route['color']
    )
    
    db.session.add(new_booking)
    db.session.commit()
    
    # Store booking information in the session
    booking = {
        'code': booking_code,
        'route': selected_route,
        'name': name,
        'date': date,
        'time': time,
        'passengers': passengers
    }
    
    session['booking'] = booking
    
    # Redirect to the ticket page
    return redirect(url_for('main.ticket'))

@main_bp.route('/ticket')
def ticket():
    # Display the ticket page with booking details
    booking = session.get('booking')
    if not booking:
        # Redirect to homepage if no booking is found in the session
        return redirect(url_for('main.index'))
    
    try:
        # Format the travel date for display
        date_obj = datetime.strptime(booking['date'], '%Y-%m-%d')
        formatted_date = date_obj.strftime('%b %d, %Y')
    except:
        formatted_date = booking['date']
    
    return render_template('ticket.html', booking=booking, formatted_date=formatted_date)

@main_bp.route('/new-booking')
def new_booking():
    # Clear the current booking from the session and redirect to homepage
    session.pop('booking', None)
    return redirect(url_for('main.index'))

@main_bp.route('/admin/confirm/<int:booking_id>', methods=['POST'])
def confirm_booking(booking_id):
    # Confirm the booking by updating its status in the database
    booking = Booking.query.get_or_404(booking_id)
    booking.status = 'confirmed'
    db.session.commit()
    return redirect(url_for('main.admin_bookings'))

@main_bp.route('/admin/delete_booking/<int:booking_id>', methods=['POST'])
def delete_booking(booking_id):
    if 'admin_id' not in session:
        flash('Please log in to access admin page.', 'warning')
        return redirect(url_for('auth.login'))

    booking = Booking.query.get_or_404(booking_id)
    db.session.delete(booking)
    db.session.commit()
    flash(f'Booking {booking.booking_code} has been deleted successfully.', 'success')
    return redirect(url_for('main.admin_bookings'))

@main_bp.route('/admin/auto_unconfirm')
def auto_unconfirm():
    ph_tz = pytz.timezone('Asia/Manila')
    now = datetime.now(ph_tz)  # Local time in PH
    
    late_bookings = Booking.query.filter(Booking.status == 'pending').all()
    updated = 0

    for booking in late_bookings:
        try:
            departure_dt = datetime.combine(
                booking.travel_date,
                datetime.strptime(booking.departure_time, '%H:%M').time()
            )
            departure_dt = ph_tz.localize(departure_dt)
        except ValueError:
            continue

        if now > departure_dt + timedelta(minutes=10):
            booking.status = 'unconfirmed'
            updated += 1

    if updated > 0:
        db.session.commit()

    return jsonify({'message': f'{updated} booking(s) marked as unconfirmed.'})

@main_bp.route('/admin/bookings')
def admin_bookings():
    if 'admin_id' not in session:
        flash('Please log in to access admin page.', 'warning')
        return redirect(url_for('auth.login'))
    
    # Local time zone
    ph_tz = pytz.timezone('Asia/Manila')
    
    # Pagination setup
    page = request.args.get('page', 1, type=int)
    per_page = 12 # table row

    # Pagination query
    total_bookings = Booking.query.count()
    total_pages = ceil(total_bookings / per_page)
    bookings = (Booking.query
                .order_by(Booking.created_at.desc())
                .offset((page - 1) * per_page)
                .limit(per_page)
                .all())

    # Count totals across ALL records (not just this page)
    confirmed_count = db.session.query(func.count(Booking.id)).filter_by(status='confirmed').scalar() or 0
    unconfirmed_count = db.session.query(func.count(Booking.id)).filter_by(status='unconfirmed').scalar() or 0

    return render_template(
        'admin_bookings.html',
        bookings=bookings,
        page=page,
        total_pages=total_pages,
        total_bookings=total_bookings,
        confirmed_count=confirmed_count,
        unconfirmed_count=unconfirmed_count,
        current_year=datetime.now(ph_tz).year
    )

"""
File: route.py
Purpose: Define the main application routes for Click to Ride system.
Includes:
- Homepage display with available routes
- Reservation form submission and ticket generation
- Admin routes for confirming, deleting, and auto-updating bookings
- Session handling for storing current booking info
- Pagination for admin booking list
""" 