from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                            QLabel, QLineEdit, QComboBox, QPushButton,
                            QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QCursor

from ui.styles import (MANGO_ORANGE, MANGO_DARK_ORANGE, NEUTRAL_DARK, 
                      TITLE_STYLE, BUTTON_STYLE, INPUT_STYLE)
from database import get_available_slots, add_vehicle
import logging

class AddVehicleDialog(QDialog):
    def __init__(self, parent=None, selected_slot=None):
        super().__init__(parent)
        self.selected_slot = selected_slot
        self.init_ui()
        
    def init_ui(self):
        # Set dialog properties
        self.setWindowTitle("Add New Vehicle")
        self.setMinimumWidth(500)
        self.setStyleSheet(f"background-color: white;")
        
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Add New Vehicle")
        title.setStyleSheet(TITLE_STYLE)
        title.setAlignment(Qt.AlignCenter)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        
        # Owner name
        self.name_input = QLineEdit()
        self.name_input.setStyleSheet(INPUT_STYLE)
        self.name_input.setPlaceholderText("Enter owner name")
        form_layout.addRow("Owner Name:", self.name_input)
        
        # Mobile number
        self.mobile_input = QLineEdit()
        self.mobile_input.setStyleSheet(INPUT_STYLE)
        self.mobile_input.setPlaceholderText("Enter mobile number")
        self.mobile_input.setInputMask("9999999999;_")  # 10-digit mobile number
        form_layout.addRow("Mobile Number:", self.mobile_input)
        
        # Vehicle number
        self.vehicle_number_input = QLineEdit()
        self.vehicle_number_input.setStyleSheet(INPUT_STYLE)
        self.vehicle_number_input.setPlaceholderText("Enter vehicle number (e.g., TN01AB1234)")
        form_layout.addRow("Vehicle Number:", self.vehicle_number_input)
        
        # Vehicle type
        self.vehicle_type_combo = QComboBox()
        self.vehicle_type_combo.setStyleSheet(INPUT_STYLE)
        self.vehicle_type_combo.addItem("2-Wheeler", "2W")
        self.vehicle_type_combo.addItem("4-Wheeler", "4W")
        self.vehicle_type_combo.currentIndexChanged.connect(self.on_vehicle_type_changed)
        form_layout.addRow("Vehicle Type:", self.vehicle_type_combo)
        
        # Parking slot
        self.slot_combo = QComboBox()
        self.slot_combo.setStyleSheet(INPUT_STYLE)
        form_layout.addRow("Parking Slot:", self.slot_combo)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.setStyleSheet(f"""
            background-color: #E0E0E0;
            color: {NEUTRAL_DARK};
            border: none;
            border-radius: 5px;
            padding: 10px 15px;
            font-size: 14px;
        """)
        cancel_button.setCursor(QCursor(Qt.PointingHandCursor))
        cancel_button.clicked.connect(self.reject)
        
        # Add button
        add_button = QPushButton("Add Vehicle")
        add_button.setStyleSheet(BUTTON_STYLE)
        add_button.setCursor(QCursor(Qt.PointingHandCursor))
        add_button.clicked.connect(self.add_vehicle)
        
        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(add_button)
        
        # Add layouts to main layout
        main_layout.addWidget(title)
        main_layout.addSpacing(20)
        main_layout.addLayout(form_layout)
        main_layout.addSpacing(20)
        main_layout.addLayout(buttons_layout)
        
        # Initial loading of available slots
        self.load_available_slots()
        
        # Set pre-selected slot if provided
        if self.selected_slot:
            slot_type = self.selected_slot[:2]  # "2W" or "4W"
            
            # Set the vehicle type combo to match the slot type
            if slot_type == "2W":
                self.vehicle_type_combo.setCurrentIndex(0)
            elif slot_type == "4W":
                self.vehicle_type_combo.setCurrentIndex(1)
            
            # Find the slot in the combo box and select it
            for i in range(self.slot_combo.count()):
                if self.slot_combo.itemText(i) == self.selected_slot:
                    self.slot_combo.setCurrentIndex(i)
                    break
    
    def load_available_slots(self):
        """Load available parking slots based on selected vehicle type"""
        try:
            self.slot_combo.clear()
            vehicle_type = self.vehicle_type_combo.currentData()
            
            # Get available slots
            available_slots = get_available_slots(vehicle_type)
            
            if not available_slots:
                self.slot_combo.addItem("No slots available")
                return
                
            # Add available slots to combo box
            for slot_id in available_slots:
                self.slot_combo.addItem(slot_id)
                
        except Exception as e:
            logging.error(f"Error loading available slots: {str(e)}")
            self.slot_combo.addItem("Error loading slots")
    
    def on_vehicle_type_changed(self):
        """Reload available slots when vehicle type changes"""
        self.load_available_slots()
    
    def add_vehicle(self):
        """Add a new vehicle to the system"""
        # Get form data
        name = self.name_input.text().strip()
        mobile = self.mobile_input.text().strip()
        vehicle_number = self.vehicle_number_input.text().strip().upper()
        vehicle_type = self.vehicle_type_combo.currentData()
        slot_id = self.slot_combo.currentText()
        
        # Validate input
        if not name:
            QMessageBox.warning(self, "Input Error", "Please enter owner name")
            self.name_input.setFocus()
            return
            
        if not mobile or len(mobile) != 10:
            QMessageBox.warning(self, "Input Error", "Please enter a valid 10-digit mobile number")
            self.mobile_input.setFocus()
            return
            
        if not vehicle_number:
            QMessageBox.warning(self, "Input Error", "Please enter vehicle number")
            self.vehicle_number_input.setFocus()
            return
            
        if slot_id == "No slots available" or slot_id == "Error loading slots":
            QMessageBox.warning(self, "Slot Error", "No parking slots available")
            return
        
        try:
            # Add vehicle to database
            success, message = add_vehicle(name, mobile, vehicle_number, vehicle_type, slot_id)
            
            if success:
                QMessageBox.information(self, "Success", "Vehicle added successfully")
                self.accept()  # Close dialog
            else:
                QMessageBox.warning(self, "Error", message)
                
        except Exception as e:
            logging.error(f"Error adding vehicle: {str(e)}")
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
