import os
import logging
import datetime
import json
from copy import deepcopy
import pymongo
from bson.objectid import ObjectId

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                   format='%(asctime)s - %(levelname)s - %(message)s')

# MongoDB connection string
MONGODB_USERNAME = "rojasridhandapani"
MONGODB_PASSWORD = "jIvrpN95gMcC2dmC"  # Using direct password as provided by user
MONGODB_CONNECTION_STRING = f"mongodb+srv://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@cluster0.k8ocq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
MONGODB_DB_NAME = "parkingManagement"

# Initialize MongoDB client
try:
    mongo_client = pymongo.MongoClient(MONGODB_CONNECTION_STRING)
    db = mongo_client[MONGODB_DB_NAME]
    logging.info(f"Successfully connected to MongoDB: {MONGODB_DB_NAME}")
except Exception as e:
    logging.error(f"Error connecting to MongoDB: {str(e)}")
    db = None

# In-memory database as fallback if MongoDB connection fails
db_storage = {
    "vehicles": [],
    "parkingHistory": [],
    "parkingSlots": []
}

# Global database flag
db_initialized = False
use_mongodb = db is not None

def initialize_db():
    """Initialize the database and create necessary collections."""
    global db_initialized, db_storage, use_mongodb
    
    try:
        if use_mongodb:
            logging.info("Initializing MongoDB database...")
            
            # Check if collections exist, if not, create them
            if "parkingSlots" not in db.list_collection_names():
                # Create 30 two-wheeler slots
                two_wheeler_slots = [
                    {"slot_id": f"2W-{i:02d}", "type": "2W", "occupied": False, "vehicle_id": None} 
                    for i in range(1, 31)
                ]
                
                # Create 30 four-wheeler slots
                four_wheeler_slots = [
                    {"slot_id": f"4W-{i:02d}", "type": "4W", "occupied": False, "vehicle_id": None} 
                    for i in range(1, 31)
                ]
                
                # Add slots to MongoDB
                db.parkingSlots.insert_many(two_wheeler_slots + four_wheeler_slots)
                logging.info("Initialized parking slots in MongoDB")
            
            db_initialized = True
            logging.info("Successfully initialized MongoDB database")
            return True
            
        else:
            logging.info("Initializing in-memory database (MongoDB unavailable)...")
            
            # Check if slots already exist
            if len(db_storage["parkingSlots"]) == 0:
                # Create 30 two-wheeler slots
                two_wheeler_slots = [
                    {"slot_id": f"2W-{i:02d}", "type": "2W", "occupied": False, "vehicle_id": None} 
                    for i in range(1, 31)
                ]
                
                # Create 30 four-wheeler slots
                four_wheeler_slots = [
                    {"slot_id": f"4W-{i:02d}", "type": "4W", "occupied": False, "vehicle_id": None} 
                    for i in range(1, 31)
                ]
                
                # Add slots to storage
                db_storage["parkingSlots"] = two_wheeler_slots + four_wheeler_slots
                logging.info("Initialized parking slots in memory")
            
            db_initialized = True
            logging.info("Successfully initialized in-memory database")
            return True
        
    except Exception as e:
        logging.error(f"Database initialization error: {str(e)}")
        use_mongodb = False  # Fallback to in-memory if MongoDB fails
        return initialize_db()  # Try again with in-memory

def get_available_slots(vehicle_type):
    """Get available parking slots for a specific vehicle type."""
    if not db_initialized:
        logging.error("Database not initialized")
        return []
    
    try:
        if use_mongodb:
            # Filter available slots by vehicle type from MongoDB
            cursor = db.parkingSlots.find({"type": vehicle_type, "occupied": False})
            slots = [slot["slot_id"] for slot in cursor]
        else:
            # Filter available slots by vehicle type from in-memory
            slots = [
                slot["slot_id"] for slot in db_storage["parkingSlots"]
                if slot["type"] == vehicle_type and not slot["occupied"]
            ]
        
        logging.debug(f"Available {vehicle_type} slots: {slots}")
        return slots
    except Exception as e:
        logging.error(f"Error fetching available slots: {str(e)}")
        return []

def get_all_slots():
    """Get all parking slots with their status."""
    if not db_initialized:
        logging.error("Database not initialized")
        return []
    
    try:
        if use_mongodb:
            # Get all slots from MongoDB
            cursor = db.parkingSlots.find()
            slots = list(cursor)  # Convert cursor to list
            # MongoDB ObjectId is not JSON serializable, remove it
            for slot in slots:
                if '_id' in slot:
                    del slot['_id']
        else:
            # Get from in-memory storage
            slots = deepcopy(db_storage["parkingSlots"])
        
        return slots
    except Exception as e:
        logging.error(f"Error fetching all slots: {str(e)}")
        return []

def add_vehicle(name, mobile, vehicle_number, vehicle_type, slot_id):
    """Add a new vehicle to the parking."""
    if not db_initialized:
        logging.error("Database not initialized")
        return False, "Database not initialized"
    
    try:
        logging.debug(f"Adding vehicle: {name}, {mobile}, {vehicle_number}, {vehicle_type}, slot: {slot_id}")
        
        # Create vehicle entry
        entry_time = datetime.datetime.now()
        vehicle_id = f"{vehicle_number}-{entry_time.strftime('%Y%m%d%H%M%S')}"
        
        if use_mongodb:
            # Check if vehicle already exists in parking
            existing_vehicle = db.vehicles.find_one({
                "vehicle_number": vehicle_number,
                "exit_time": None
            })
            
            if existing_vehicle:
                logging.warning(f"Vehicle {vehicle_number} already parked in slot {existing_vehicle['slot_id']}")
                return False, "Vehicle already parked"
            
            # Check if slot exists and is available
            slot = db.parkingSlots.find_one({"slot_id": slot_id})
            
            if not slot:
                logging.warning(f"Slot {slot_id} not found in database")
                available_slots = get_available_slots(vehicle_type)
                logging.debug(f"Available {vehicle_type} slots: {available_slots}")
                return False, f"Selected slot {slot_id} not found"
            
            if slot.get("occupied", False):
                logging.warning(f"Slot {slot_id} is already occupied")
                return False, f"Selected slot {slot_id} is already occupied"
            
            # Verify vehicle type matches slot type
            if slot["type"] != vehicle_type:
                logging.warning(f"Vehicle type {vehicle_type} does not match slot type {slot['type']}")
                return False, f"Selected slot is for {slot['type']} vehicles"
            
            # Create vehicle data
            vehicle_data = {
                "vehicle_id": vehicle_id,
                "name": name,
                "mobile": mobile,
                "vehicle_number": vehicle_number,
                "vehicle_type": vehicle_type,
                "slot_id": slot_id,
                "entry_time": entry_time,
                "exit_time": None,
                "payment": 0
            }
            
            # Add vehicle to MongoDB
            db.vehicles.insert_one(vehicle_data)
            
            # Update slot status in MongoDB
            db.parkingSlots.update_one(
                {"slot_id": slot_id},
                {"$set": {"occupied": True, "vehicle_id": vehicle_id}}
            )
        else:
            # In-memory operations
            # Check if vehicle already exists in parking
            existing_vehicle = next(
                (v for v in db_storage["vehicles"] 
                if v["vehicle_number"] == vehicle_number and v["exit_time"] is None),
                None
            )
            
            if existing_vehicle:
                logging.warning(f"Vehicle {vehicle_number} already parked in slot {existing_vehicle['slot_id']}")
                return False, "Vehicle already parked"
            
            # Check if slot is available
            slot = next(
                (s for s in db_storage["parkingSlots"] if s["slot_id"] == slot_id),
                None
            )
            
            if not slot:
                logging.warning(f"Slot {slot_id} not found in database")
                available_slots = get_available_slots(vehicle_type)
                logging.debug(f"Available {vehicle_type} slots: {available_slots}")
                return False, f"Selected slot {slot_id} not found"
            
            if slot["occupied"]:
                logging.warning(f"Slot {slot_id} is already occupied")
                return False, f"Selected slot {slot_id} is already occupied"
            
            # Verify vehicle type matches slot type
            if slot["type"] != vehicle_type:
                logging.warning(f"Vehicle type {vehicle_type} does not match slot type {slot['type']}")
                return False, f"Selected slot is for {slot['type']} vehicles"
            
            # Create vehicle data
            vehicle_data = {
                "vehicle_id": vehicle_id,
                "name": name,
                "mobile": mobile,
                "vehicle_number": vehicle_number,
                "vehicle_type": vehicle_type,
                "slot_id": slot_id,
                "entry_time": entry_time,
                "exit_time": None,
                "payment": 0
            }
            
            # Add vehicle to in-memory storage
            db_storage["vehicles"].append(vehicle_data)
            
            # Update slot status in in-memory storage
            for s in db_storage["parkingSlots"]:
                if s["slot_id"] == slot_id:
                    s["occupied"] = True
                    s["vehicle_id"] = vehicle_id
                    break
        
        logging.info(f"Vehicle {vehicle_number} successfully parked in slot {slot_id}")
        return True, "Vehicle added successfully"
    
    except Exception as e:
        logging.error(f"Error adding vehicle: {str(e)}")
        return False, f"Error: {str(e)}"

def get_parked_vehicles():
    """Get all currently parked vehicles."""
    if not db_initialized:
        logging.error("Database not initialized")
        return []
    
    try:
        if use_mongodb:
            # Get all vehicles that haven't exited yet from MongoDB
            cursor = db.vehicles.find({"exit_time": None})
            vehicles = list(cursor)
            # Remove MongoDB ObjectId
            for vehicle in vehicles:
                if '_id' in vehicle:
                    del vehicle['_id']
        else:
            # Filter vehicles that haven't exited yet from in-memory storage
            vehicles = [v for v in db_storage["vehicles"] if v["exit_time"] is None]
            vehicles = deepcopy(vehicles)
        
        return vehicles
    except Exception as e:
        logging.error(f"Error fetching parked vehicles: {str(e)}")
        return []

def exit_vehicle(vehicle_id, payment_method=None, payment_status=None):
    """
    Process vehicle exit and calculate payment.
    
    Args:
        vehicle_id (str): The ID of the vehicle to exit
        payment_method (str, optional): Method of payment ('cash', 'qr_code')
        payment_status (str, optional): Status of payment ('pending', 'completed')
    
    Returns:
        tuple: (success, message, payment_amount)
    """
    if not db_initialized:
        logging.error("Database not initialized")
        return False, "Database not initialized", 0
    
    # If payment method is not provided, this is just a calculation step
    if payment_method is None:
        try:
            # Get vehicle details
            if use_mongodb:
                vehicle = db.vehicles.find_one({"vehicle_id": vehicle_id, "exit_time": None})
                if vehicle:
                    # Create a copy without MongoDB ObjectId
                    vehicle_copy = deepcopy(vehicle)
                    if '_id' in vehicle_copy:
                        del vehicle_copy['_id']
                    vehicle = vehicle_copy
            else:
                vehicle = next(
                    (v for v in db_storage["vehicles"] 
                    if v["vehicle_id"] == vehicle_id and v["exit_time"] is None),
                    None
                )
            
            if not vehicle:
                return False, "Vehicle not found", 0
            
            # Calculate duration and payment
            exit_time = datetime.datetime.now()
            entry_time = vehicle["entry_time"]
            
            # Calculate hours (round up to the nearest hour)
            duration_seconds = (exit_time - entry_time).total_seconds()
            hours = max(1, int((duration_seconds + 3599) / 3600))  # Round up
            
            # Calculate payment based on vehicle type
            rate_per_hour = 30 if vehicle["vehicle_type"] == "2W" else 60
            payment = hours * rate_per_hour
            
            return True, f"Calculate payment: ₹{payment} for {hours} hour(s)", payment
        
        except Exception as e:
            logging.error(f"Error calculating payment: {str(e)}")
            return False, f"Error: {str(e)}", 0
    
    # If payment method is provided, process the actual exit
    try:
        # Get vehicle details
        if use_mongodb:
            vehicle = db.vehicles.find_one({"vehicle_id": vehicle_id, "exit_time": None})
            if vehicle:
                # Create a copy without MongoDB ObjectId
                vehicle_copy = deepcopy(vehicle)
                if '_id' in vehicle_copy:
                    del vehicle_copy['_id']
                vehicle = vehicle_copy
        else:
            vehicle = next(
                (v for v in db_storage["vehicles"] 
                if v["vehicle_id"] == vehicle_id and v["exit_time"] is None),
                None
            )
        
        if not vehicle:
            return False, "Vehicle not found", 0
        
        # Calculate duration and payment
        exit_time = datetime.datetime.now()
        entry_time = vehicle["entry_time"]
        
        # Calculate hours (round up to the nearest hour)
        duration_seconds = (exit_time - entry_time).total_seconds()
        hours = max(1, int((duration_seconds + 3599) / 3600))  # Round up
        
        # Calculate payment based on vehicle type
        rate_per_hour = 30 if vehicle["vehicle_type"] == "2W" else 60
        payment = hours * rate_per_hour
        
        # Set default payment status if not provided
        if payment_status is None:
            payment_status = "completed"
        
        # Create history entry data
        history_entry = deepcopy(vehicle)
        history_entry["exit_time"] = exit_time
        history_entry["payment"] = payment
        history_entry["duration_hours"] = hours
        history_entry["payment_method"] = payment_method
        history_entry["payment_status"] = payment_status
        
        if use_mongodb:
            # Update vehicle in MongoDB
            db.vehicles.update_one(
                {"vehicle_id": vehicle_id},
                {"$set": {
                    "exit_time": exit_time,
                    "payment": payment,
                    "duration_hours": hours,
                    "payment_method": payment_method,
                    "payment_status": payment_status
                }}
            )
            
            # Add to history collection in MongoDB
            db.parkingHistory.insert_one(history_entry)
            
            # Free up the slot in MongoDB
            db.parkingSlots.update_one(
                {"slot_id": vehicle["slot_id"]},
                {"$set": {"occupied": False, "vehicle_id": None}}
            )
        else:
            # Update vehicle record in memory
            for v in db_storage["vehicles"]:
                if v["vehicle_id"] == vehicle_id:
                    v["exit_time"] = exit_time
                    v["payment"] = payment
                    v["duration_hours"] = hours
                    v["payment_method"] = payment_method
                    v["payment_status"] = payment_status
                    break
            
            # Add to history in memory
            db_storage["parkingHistory"].append(history_entry)
            
            # Free up the slot in memory
            for s in db_storage["parkingSlots"]:
                if s["slot_id"] == vehicle["slot_id"]:
                    s["occupied"] = False
                    s["vehicle_id"] = None
                    break
        
        method_text = "cash" if payment_method == "cash" else "QR code"
        return True, f"Vehicle exited after {hours} hour(s). Payment of ₹{payment} received via {method_text}.", payment
    
    except Exception as e:
        logging.error(f"Error processing vehicle exit: {str(e)}")
        return False, f"Error: {str(e)}", 0

def get_parking_history(limit=100, skip=0):
    """Get parking history for analysis."""
    if not db_initialized:
        logging.error("Database not initialized")
        return []
    
    try:
        if use_mongodb:
            # Query MongoDB for parking history, sorted by exit time
            cursor = db.parkingHistory.find({}).sort("exit_time", -1).skip(skip).limit(limit)
            history = list(cursor)
            
            # Remove MongoDB ObjectId
            for record in history:
                if '_id' in record:
                    del record['_id']
        else:
            # Sort history by exit time (most recent first) from in-memory storage
            sorted_history = sorted(
                db_storage["parkingHistory"],
                key=lambda x: x["exit_time"] if x["exit_time"] else datetime.datetime.min,
                reverse=True
            )
            
            # Apply pagination
            history = sorted_history[skip:skip+limit]
            history = deepcopy(history)
        
        return history
    except Exception as e:
        logging.error(f"Error fetching parking history: {str(e)}")
        return []

def close_connection():
    """Close the database connection."""
    # No actual connection to close with in-memory storage
    logging.info("In-memory database connection closed")
    pass
