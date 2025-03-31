from PyQt5.QtWidgets import (QMainWindow, QWidget, QLabel, QPushButton, 
                            QVBoxLayout, QHBoxLayout, QGridLayout, 
                            QTabWidget, QFrame, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QIcon, QFont, QCursor

from ui.add_vehicle import AddVehicleDialog
from ui.manage_vehicles import ManageVehiclesTab
from ui.history import HistoryTab
from ui.styles import (MANGO_YELLOW, MANGO_ORANGE, MANGO_DARK_ORANGE, 
                      MANGO_GREEN, MANGO_RED, NEUTRAL_DARK, NEUTRAL_LIGHT, 
                      TITLE_STYLE, SUBTITLE_STYLE, BUTTON_STYLE, TAB_STYLE,
                      SLOT_AVAILABLE_STYLE, SLOT_OCCUPIED_STYLE)
from database import get_all_slots, initialize_db
import logging

class ParkingGridWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
        # Set up auto-refresh timer (every 10 seconds)
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(10000)  # 10 seconds
        
    def init_ui(self):
        # Set window properties
        self.setWindowTitle("Parking Management System")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet(f"background-color: {NEUTRAL_LIGHT};")
        
        # Create central widget and main layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # Header section
        header = QWidget()
        header.setStyleSheet(f"background-color: {MANGO_DARK_ORANGE}; border-radius: 5px;")
        header_layout = QHBoxLayout(header)
        
        # App logo/title
        title_label = QLabel("Parking Management System")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        
        # Stats section
        stats_widget = QWidget()
        stats_widget.setStyleSheet(f"background-color: {MANGO_ORANGE}; border-radius: 5px;")
        stats_layout = QHBoxLayout(stats_widget)
        
        self.two_wheeler_count = QLabel("2W Available: 0/30")
        self.two_wheeler_count.setStyleSheet("color: white; font-weight: bold;")
        
        self.four_wheeler_count = QLabel("4W Available: 0/30")
        self.four_wheeler_count.setStyleSheet("color: white; font-weight: bold;")
        
        stats_layout.addWidget(self.two_wheeler_count)
        stats_layout.addWidget(self.four_wheeler_count)
        
        # Add to header
        header_layout.addWidget(title_label)
        header_layout.addStretch(1)
        header_layout.addWidget(stats_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(TAB_STYLE)
        
        # Create tabs
        self.parking_tab = QWidget()
        self.manage_tab = ManageVehiclesTab(self)
        self.history_tab = HistoryTab()
        
        # Add tabs to widget
        self.tab_widget.addTab(self.parking_tab, "Parking Layout")
        self.tab_widget.addTab(self.manage_tab, "Manage Vehicles")
        self.tab_widget.addTab(self.history_tab, "Parking History")
        
        # Setup parking grid tab
        self.setup_parking_grid()
        
        # Add widgets to main layout
        main_layout.addWidget(header)
        main_layout.addWidget(self.tab_widget, 1)  # 1 is the stretch factor
        
        # Set central widget
        self.setCentralWidget(central_widget)
        
        # Initial data load
        self.refresh_data()
    
    def setup_parking_grid(self):
        """Set up the parking grid tab with 2W and 4W sections"""
        parking_layout = QVBoxLayout(self.parking_tab)
        
        # Add new vehicle button
        add_button = QPushButton("Add New Vehicle")
        add_button.setStyleSheet(BUTTON_STYLE)
        add_button.setCursor(QCursor(Qt.PointingHandCursor))
        add_button.clicked.connect(self.show_add_vehicle_dialog)
        add_button.setFixedHeight(40)
        
        # Legend section
        legend_widget = QWidget()
        legend_layout = QHBoxLayout(legend_widget)
        
        available_sample = QLabel("Available")
        available_sample.setStyleSheet(SLOT_AVAILABLE_STYLE + "padding: 5px 10px;")
        
        occupied_sample = QLabel("Occupied")
        occupied_sample.setStyleSheet(SLOT_OCCUPIED_STYLE + "padding: 5px 10px;")
        
        legend_layout.addWidget(QLabel("Legend:"))
        legend_layout.addWidget(available_sample)
        legend_layout.addWidget(occupied_sample)
        legend_layout.addStretch(1)
        
        # Two-wheeler section
        two_wheeler_frame = QFrame()
        two_wheeler_frame.setStyleSheet(f"background-color: white; border-radius: 10px; padding: 10px;")
        two_wheeler_layout = QVBoxLayout(two_wheeler_frame)
        
        two_wheeler_title = QLabel("Two-Wheeler Parking (30 slots)")
        two_wheeler_title.setStyleSheet(SUBTITLE_STYLE)
        
        self.two_wheeler_grid = QGridLayout()
        self.two_wheeler_grid.setSpacing(10)
        
        # Create initial empty slot buttons for two-wheelers
        for i in range(30):
            row, col = divmod(i, 6)  # 6 slots per row
            slot_id = f"2W-{i+1:02d}"
            slot_button = QPushButton(slot_id)
            slot_button.setStyleSheet(SLOT_AVAILABLE_STYLE)
            slot_button.setFixedSize(120, 60)
            slot_button.setCursor(QCursor(Qt.PointingHandCursor))
            slot_button.clicked.connect(lambda _, s=slot_id: self.slot_clicked(s))
            self.two_wheeler_grid.addWidget(slot_button, row, col)
        
        two_wheeler_layout.addWidget(two_wheeler_title)
        two_wheeler_layout.addLayout(self.two_wheeler_grid)
        
        # Four-wheeler section
        four_wheeler_frame = QFrame()
        four_wheeler_frame.setStyleSheet(f"background-color: white; border-radius: 10px; padding: 10px;")
        four_wheeler_layout = QVBoxLayout(four_wheeler_frame)
        
        four_wheeler_title = QLabel("Four-Wheeler Parking (30 slots)")
        four_wheeler_title.setStyleSheet(SUBTITLE_STYLE)
        
        self.four_wheeler_grid = QGridLayout()
        self.four_wheeler_grid.setSpacing(10)
        
        # Create initial empty slot buttons for four-wheelers
        for i in range(30):
            row, col = divmod(i, 6)  # 6 slots per row
            slot_id = f"4W-{i+1:02d}"
            slot_button = QPushButton(slot_id)
            slot_button.setStyleSheet(SLOT_AVAILABLE_STYLE)
            slot_button.setFixedSize(120, 60)
            slot_button.setCursor(QCursor(Qt.PointingHandCursor))
            slot_button.clicked.connect(lambda _, s=slot_id: self.slot_clicked(s))
            self.four_wheeler_grid.addWidget(slot_button, row, col)
        
        four_wheeler_layout.addWidget(four_wheeler_title)
        four_wheeler_layout.addLayout(self.four_wheeler_grid)
        
        # Add all sections to parking layout
        parking_layout.addWidget(add_button, alignment=Qt.AlignRight)
        parking_layout.addWidget(legend_widget)
        parking_layout.addWidget(two_wheeler_frame)
        parking_layout.addSpacing(20)
        parking_layout.addWidget(four_wheeler_frame)
    
    def refresh_data(self):
        """Refresh the parking grid and vehicle count display"""
        try:
            # Get all slots with their status
            slots = get_all_slots()
            
            # Count available slots
            two_wheeler_available = sum(1 for slot in slots if slot["type"] == "2W" and not slot["occupied"])
            four_wheeler_available = sum(1 for slot in slots if slot["type"] == "4W" and not slot["occupied"])
            
            # Update the labels
            self.two_wheeler_count.setText(f"2W Available: {two_wheeler_available}/30")
            self.four_wheeler_count.setText(f"4W Available: {four_wheeler_available}/30")
            
            # Update slot buttons
            self.update_slot_buttons(slots)
            
            # Refresh other tabs
            if hasattr(self.manage_tab, 'refresh_data'):
                self.manage_tab.refresh_data()
            
            if hasattr(self.history_tab, 'refresh_data'):
                self.history_tab.refresh_data()
                
        except Exception as e:
            logging.error(f"Error refreshing data: {str(e)}")
    
    def update_slot_buttons(self, slots):
        """Update the slot button styles based on occupancy"""
        # Create a dictionary for easier access
        slot_dict = {slot["slot_id"]: slot for slot in slots}
        
        # Update two-wheeler slots
        for i in range(30):
            row, col = divmod(i, 6)
            slot_id = f"2W-{i+1:02d}"
            button_item = self.two_wheeler_grid.itemAtPosition(row, col)
            
            if button_item and slot_id in slot_dict:
                button = button_item.widget()
                slot = slot_dict[slot_id]
                
                if slot["occupied"]:
                    button.setStyleSheet(SLOT_OCCUPIED_STYLE)
                    vehicle_id = slot.get("vehicle_id", "")
                    if vehicle_id:
                        # Just show the slot ID - can be modified to show more details
                        button.setText(f"{slot_id}\n(Occupied)")
                else:
                    button.setStyleSheet(SLOT_AVAILABLE_STYLE)
                    button.setText(slot_id)
        
        # Update four-wheeler slots
        for i in range(30):
            row, col = divmod(i, 6)
            slot_id = f"4W-{i+1:02d}"
            button_item = self.four_wheeler_grid.itemAtPosition(row, col)
            
            if button_item and slot_id in slot_dict:
                button = button_item.widget()
                slot = slot_dict[slot_id]
                
                if slot["occupied"]:
                    button.setStyleSheet(SLOT_OCCUPIED_STYLE)
                    vehicle_id = slot.get("vehicle_id", "")
                    if vehicle_id:
                        # Just show the slot ID - can be modified to show more details
                        button.setText(f"{slot_id}\n(Occupied)")
                else:
                    button.setStyleSheet(SLOT_AVAILABLE_STYLE)
                    button.setText(slot_id)
    
    def slot_clicked(self, slot_id):
        """Handle slot button click - show add vehicle dialog for empty slots"""
        try:
            # Get all slots
            slots = get_all_slots()
            slot_dict = {slot["slot_id"]: slot for slot in slots}
            
            # Check if the slot exists and its status
            if slot_id in slot_dict:
                slot = slot_dict[slot_id]
                
                if not slot["occupied"]:
                    # If slot is available, show add vehicle dialog
                    self.show_add_vehicle_dialog(slot_id)
                else:
                    # If slot is occupied, possibly show vehicle details
                    # For now, just switch to manage tab
                    self.tab_widget.setCurrentIndex(1)  # Switch to Manage Vehicles tab
        except Exception as e:
            logging.error(f"Error handling slot click: {str(e)}")
    
    def show_add_vehicle_dialog(self, slot_id=None):
        """Show dialog to add a new vehicle"""
        dialog = AddVehicleDialog(self, slot_id)
        if dialog.exec_():
            # Refresh after adding vehicle
            self.refresh_data()
