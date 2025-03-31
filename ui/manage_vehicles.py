from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                            QTableWidgetItem, QPushButton, QLabel, QMessageBox,
                            QHeaderView, QDialog, QFormLayout, QLineEdit)
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtGui import QFont, QCursor

from ui.styles import (MANGO_YELLOW, MANGO_ORANGE, MANGO_DARK_ORANGE, MANGO_RED,
                      NEUTRAL_DARK, BUTTON_STYLE, BUTTON_STYLE_DANGER, TABLE_STYLE)
from database import get_parked_vehicles, exit_vehicle
import logging
from datetime import datetime

class VehicleExitDialog(QDialog):
    def __init__(self, parent=None, vehicle_data=None, hours=0, payment=0):
        super().__init__(parent)
        self.vehicle_data = vehicle_data
        self.hours = hours
        self.payment = payment
        self.init_ui()
        
    def init_ui(self):
        # Set dialog properties
        self.setWindowTitle("Vehicle Exit - Payment Details")
        self.setMinimumWidth(400)
        self.setStyleSheet(f"background-color: white;")
        
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Payment Summary")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        
        # Details form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Vehicle details
        vehicle_number = QLabel(self.vehicle_data.get("vehicle_number", ""))
        vehicle_number.setStyleSheet("font-weight: bold;")
        form_layout.addRow("Vehicle Number:", vehicle_number)
        
        owner_name = QLabel(self.vehicle_data.get("name", ""))
        form_layout.addRow("Owner Name:", owner_name)
        
        entry_time = QLabel(self.vehicle_data.get("entry_time", datetime.now()).strftime("%Y-%m-%d %H:%M:%S"))
        form_layout.addRow("Entry Time:", entry_time)
        
        exit_time = QLabel(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        form_layout.addRow("Exit Time:", exit_time)
        
        duration = QLabel(f"{self.hours} hour(s)")
        duration.setStyleSheet("font-weight: bold;")
        form_layout.addRow("Duration:", duration)
        
        rate = QLabel(f"₹{30 if self.vehicle_data.get('vehicle_type') == '2W' else 60} per hour")
        form_layout.addRow("Rate:", rate)
        
        # Payment amount - large and prominent
        payment_layout = QHBoxLayout()
        payment_label = QLabel("Total Amount:")
        payment_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        payment_amount = QLabel(f"₹{self.payment}")
        payment_amount.setStyleSheet(f"""
            font-size: 24px;
            font-weight: bold;
            color: {MANGO_DARK_ORANGE};
            background-color: #F0F0F0;
            padding: 5px 15px;
            border-radius: 5px;
        """)
        
        payment_layout.addWidget(payment_label)
        payment_layout.addWidget(payment_amount, 1, Qt.AlignRight)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        # Close button
        close_button = QPushButton("Close")
        close_button.setStyleSheet(BUTTON_STYLE)
        close_button.setCursor(QCursor(Qt.PointingHandCursor))
        close_button.clicked.connect(self.accept)
        
        buttons_layout.addStretch(1)
        buttons_layout.addWidget(close_button)
        buttons_layout.addStretch(1)
        
        # Add layouts to main layout
        main_layout.addWidget(title)
        main_layout.addSpacing(20)
        main_layout.addLayout(form_layout)
        main_layout.addSpacing(10)
        main_layout.addLayout(payment_layout)
        main_layout.addSpacing(20)
        main_layout.addLayout(buttons_layout)

class ManageVehiclesTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()
        
    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Manage Parked Vehicles")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        
        # Refresh button
        refresh_button = QPushButton("Refresh")
        refresh_button.setStyleSheet(f"""
            background-color: {MANGO_YELLOW};
            color: {NEUTRAL_DARK};
            border: none;
            border-radius: 5px;
            padding: 5px 10px;
        """)
        refresh_button.setCursor(QCursor(Qt.PointingHandCursor))
        refresh_button.clicked.connect(self.refresh_data)
        
        # Header layout
        header_layout = QHBoxLayout()
        header_layout.addWidget(title)
        header_layout.addStretch(1)
        header_layout.addWidget(refresh_button)
        
        # Table for parked vehicles
        self.vehicles_table = QTableWidget()
        self.vehicles_table.setStyleSheet(TABLE_STYLE)
        self.vehicles_table.setColumnCount(7)
        self.vehicles_table.setHorizontalHeaderLabels([
            "Owner Name", "Mobile", "Vehicle Number", "Type", "Slot", "Entry Time", "Actions"
        ])
        
        # Set column widths
        self.vehicles_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.vehicles_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Fixed)
        self.vehicles_table.setColumnWidth(6, 100)  # Actions column
        
        # Add widgets to main layout
        main_layout.addLayout(header_layout)
        main_layout.addWidget(self.vehicles_table)
        
        # Initial data load
        self.refresh_data()
    
    def refresh_data(self):
        """Refresh the vehicles table with current data"""
        try:
            # Get all parked vehicles
            vehicles = get_parked_vehicles()
            
            # Clear the table
            self.vehicles_table.setRowCount(0)
            
            # Fill the table with data
            for i, vehicle in enumerate(vehicles):
                self.vehicles_table.insertRow(i)
                
                # Owner name
                self.vehicles_table.setItem(i, 0, QTableWidgetItem(vehicle.get("name", "")))
                
                # Mobile number
                self.vehicles_table.setItem(i, 1, QTableWidgetItem(vehicle.get("mobile", "")))
                
                # Vehicle number
                vehicle_number_item = QTableWidgetItem(vehicle.get("vehicle_number", ""))
                vehicle_number_item.setFont(QFont("Arial", weight=QFont.Bold))
                self.vehicles_table.setItem(i, 2, vehicle_number_item)
                
                # Vehicle type
                vehicle_type = "2-Wheeler" if vehicle.get("vehicle_type") == "2W" else "4-Wheeler"
                self.vehicles_table.setItem(i, 3, QTableWidgetItem(vehicle_type))
                
                # Slot ID
                self.vehicles_table.setItem(i, 4, QTableWidgetItem(vehicle.get("slot_id", "")))
                
                # Entry time
                entry_time = vehicle.get("entry_time", datetime.now())
                formatted_time = entry_time.strftime("%Y-%m-%d %H:%M:%S")
                self.vehicles_table.setItem(i, 5, QTableWidgetItem(formatted_time))
                
                # Exit button
                exit_button = QPushButton("Exit Vehicle")
                exit_button.setStyleSheet(BUTTON_STYLE_DANGER)
                exit_button.setCursor(QCursor(Qt.PointingHandCursor))
                
                # Store vehicle_id for the button
                vehicle_id = vehicle.get("vehicle_id")
                exit_button.clicked.connect(lambda _, vid=vehicle_id: self.exit_vehicle(vid))
                
                self.vehicles_table.setCellWidget(i, 6, exit_button)
            
            # If no vehicles, show empty message
            if not vehicles:
                self.vehicles_table.setRowCount(1)
                empty_msg = QTableWidgetItem("No vehicles currently parked")
                empty_msg.setTextAlignment(Qt.AlignCenter)
                self.vehicles_table.setSpan(0, 0, 1, 7)
                self.vehicles_table.setItem(0, 0, empty_msg)
                
        except Exception as e:
            logging.error(f"Error refreshing vehicles data: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to load vehicles: {str(e)}")
    
    def exit_vehicle(self, vehicle_id):
        """Process vehicle exit"""
        try:
            # Get all vehicles to find the one with this ID
            vehicles = get_parked_vehicles()
            vehicle_data = next((v for v in vehicles if v.get("vehicle_id") == vehicle_id), None)
            
            if not vehicle_data:
                QMessageBox.warning(self, "Error", "Vehicle not found")
                return
            
            # Confirm exit
            confirm = QMessageBox.question(
                self,
                "Confirm Exit",
                f"Process exit for vehicle {vehicle_data.get('vehicle_number')}?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if confirm == QMessageBox.Yes:
                # Process the exit
                success, message, payment = exit_vehicle(vehicle_id)
                
                if success:
                    # Show payment details
                    hours = vehicle_data.get("duration_hours", 1)
                    dialog = VehicleExitDialog(self, vehicle_data, hours, payment)
                    dialog.exec_()
                    
                    # Refresh data
                    self.refresh_data()
                    
                    # Refresh parent (parking grid) if exists
                    if self.parent and hasattr(self.parent, "refresh_data"):
                        self.parent.refresh_data()
                else:
                    QMessageBox.warning(self, "Error", message)
                    
        except Exception as e:
            logging.error(f"Error processing vehicle exit: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to process exit: {str(e)}")
