"""
Data models for the Parking Management System.
Defines the structure of data objects used in the application.
"""

class Vehicle:
    """
    Vehicle model for representing parked vehicles.
    
    Attributes:
        vehicle_id (str): A unique identifier for the vehicle
        name (str): Owner's name
        mobile (str): Owner's mobile number
        vehicle_number (str): License plate number
        vehicle_type (str): Type of vehicle ('2W' or '4W')
        slot_id (str): Parking slot ID
        entry_time (datetime): Time when vehicle entered
        exit_time (datetime): Time when vehicle exited (None if still parked)
        payment (float): Payment amount (0 if still parked)
        payment_method (str): Method of payment ('cash', 'qr_code', or None if not paid)
        payment_status (str): Status of payment ('pending', 'completed', or None if not processed)
    """
    def __init__(self, vehicle_id, name, mobile, vehicle_number, vehicle_type, 
                 slot_id, entry_time, exit_time=None, payment=0, 
                 payment_method=None, payment_status=None):
        self.vehicle_id = vehicle_id
        self.name = name
        self.mobile = mobile
        self.vehicle_number = vehicle_number
        self.vehicle_type = vehicle_type
        self.slot_id = slot_id
        self.entry_time = entry_time
        self.exit_time = exit_time
        self.payment = payment
        self.payment_method = payment_method
        self.payment_status = payment_status


class ParkingSlot:
    """
    Parking slot model.
    
    Attributes:
        slot_id (str): A unique identifier for the slot (e.g., '2W-01', '4W-01')
        type (str): Type of vehicle the slot is for ('2W' or '4W')
        occupied (bool): Whether the slot is occupied
        vehicle_id (str): ID of the vehicle parked in this slot (if occupied)
    """
    def __init__(self, slot_id, type, occupied=False, vehicle_id=None):
        self.slot_id = slot_id
        self.type = type
        self.occupied = occupied
        self.vehicle_id = vehicle_id


class ParkingHistory:
    """
    Parking history entry model.
    
    Attributes:
        All attributes from Vehicle plus:
        duration_hours (int): Duration of parking in hours
        payment_method (str): Method of payment ('cash', 'qr_code')
        payment_status (str): Status of payment ('completed')
    """
    def __init__(self, vehicle_data, duration_hours):
        self.vehicle_id = vehicle_data.get('vehicle_id')
        self.name = vehicle_data.get('name')
        self.mobile = vehicle_data.get('mobile')
        self.vehicle_number = vehicle_data.get('vehicle_number')
        self.vehicle_type = vehicle_data.get('vehicle_type')
        self.slot_id = vehicle_data.get('slot_id')
        self.entry_time = vehicle_data.get('entry_time')
        self.exit_time = vehicle_data.get('exit_time')
        self.payment = vehicle_data.get('payment')
        self.payment_method = vehicle_data.get('payment_method', 'cash')
        self.payment_status = vehicle_data.get('payment_status', 'completed')
        self.duration_hours = duration_hours
