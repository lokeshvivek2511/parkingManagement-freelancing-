import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from datetime import datetime
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Import database functions
from database import (initialize_db, get_available_slots, get_all_slots, 
                     add_vehicle, get_parked_vehicles, exit_vehicle, 
                     get_parking_history)
from auth import authenticate

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "parking_management_secret_key")

# Initialize database
initialize_db()

# Login decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if authenticate(username, password):
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            error = 'Invalid username or password. Please try again.'
    
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get all slots with their status
    slots = get_all_slots()
    
    # Count available slots
    two_wheeler_slots = [slot for slot in slots if slot["type"] == "2W"]
    four_wheeler_slots = [slot for slot in slots if slot["type"] == "4W"]
    
    two_wheeler_available = sum(1 for slot in two_wheeler_slots if not slot["occupied"])
    four_wheeler_available = sum(1 for slot in four_wheeler_slots if not slot["occupied"])
    
    return render_template('dashboard.html', 
                           two_wheeler_slots=two_wheeler_slots,
                           four_wheeler_slots=four_wheeler_slots,
                           two_wheeler_available=two_wheeler_available,
                           four_wheeler_available=four_wheeler_available)

@app.route('/add_vehicle', methods=['GET', 'POST'])
@login_required
def add_vehicle_page():
    if request.method == 'POST':
        name = request.form['name']
        mobile = request.form['mobile']
        vehicle_number = request.form['vehicle_number'].upper()
        vehicle_type = request.form['vehicle_type']
        slot_id = request.form['slot_id']
        
        success, message = add_vehicle(name, mobile, vehicle_number, vehicle_type, slot_id)
        
        if success:
            flash('Vehicle added successfully', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash(message, 'danger')
    
    # Get available slots for both vehicle types
    two_wheeler_slots = get_available_slots('2W')
    four_wheeler_slots = get_available_slots('4W')
    
    return render_template('add_vehicle.html', 
                           two_wheeler_slots=two_wheeler_slots,
                           four_wheeler_slots=four_wheeler_slots)

@app.route('/manage_vehicles')
@login_required
def manage_vehicles():
    vehicles = get_parked_vehicles()
    return render_template('manage_vehicles.html', vehicles=vehicles)

@app.route('/exit_vehicle/<vehicle_id>')
@login_required
def process_exit(vehicle_id):
    # First, just calculate the payment without actually processing exit
    success, message, payment = exit_vehicle(vehicle_id)
    
    if not success:
        flash(message, 'danger')
        return redirect(url_for('manage_vehicles'))
    
    # If calculation was successful, get vehicle details for payment page
    if success:
        # Get vehicle details
        vehicles = get_parked_vehicles()
        vehicle = next((v for v in vehicles if v["vehicle_id"] == vehicle_id), None)
        
        if vehicle:
            # Calculate hours (round up to the nearest hour)
            entry_time = vehicle["entry_time"]
            exit_time = datetime.now()
            duration_seconds = (exit_time - entry_time).total_seconds()
            hours = max(1, int((duration_seconds + 3599) / 3600))  # Round up
            
            # Render payment options page
            return render_template('payment.html', 
                                  vehicle=vehicle, 
                                  payment=payment, 
                                  hours=hours)
        else:
            flash('Vehicle not found', 'danger')
            return redirect(url_for('manage_vehicles'))

@app.route('/complete_exit/<vehicle_id>')
@login_required
def complete_exit(vehicle_id):
    payment_method = request.args.get('method', 'cash')
    
    # Process the vehicle exit with payment method
    success, message, payment = exit_vehicle(vehicle_id, payment_method, 'completed')
    
    if success:
        method_text = "cash" if payment_method == "cash" else "QR code"
        flash(f'Vehicle exited successfully. Payment of ₹{payment} received via {method_text}.', 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('manage_vehicles'))

@app.route('/parking_history')
@login_required
def parking_history():
    page = request.args.get('page', 1, type=int)
    limit = 10
    skip = (page - 1) * limit
    
    history = get_parking_history(limit=limit, skip=skip)
    
    # Get total count for pagination
    total_history = len(get_parking_history(limit=1000, skip=0))
    total_pages = (total_history + limit - 1) // limit
    
    return render_template('history.html', 
                           history=history, 
                           page=page, 
                           total_pages=total_pages)

# API endpoints for AJAX requests
@app.route('/api/available_slots/<vehicle_type>')
def api_available_slots(vehicle_type):
    slots = get_available_slots(vehicle_type)
    return jsonify(slots)

@app.route('/api/all_slots')
def api_all_slots():
    slots = get_all_slots()
    return jsonify(slots)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)