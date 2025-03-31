from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                            QTableWidgetItem, QPushButton, QLabel, QMessageBox,
                            QHeaderView, QComboBox, QLineEdit)
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtGui import QFont, QCursor

from ui.styles import (MANGO_YELLOW, MANGO_ORANGE, NEUTRAL_DARK, 
                      BUTTON_STYLE, TABLE_STYLE)
from database import get_parking_history
import logging
from datetime import datetime

class HistoryTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.page = 0
        self.page_size = 20
        
    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Parking History")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        
        # Filter section
        filter_layout = QHBoxLayout()
        
        # Vehicle type filter
        self.type_filter = QComboBox()
        self.type_filter.setStyleSheet(f"""
            border: 1px solid {MANGO_ORANGE};
            border-radius: 3px;
            padding: 5px;
        """)
        self.type_filter.addItem("All Types", "all")
        self.type_filter.addItem("2-Wheeler", "2W")
        self.type_filter.addItem("4-Wheeler", "4W")
        self.type_filter.currentIndexChanged.connect(self.refresh_data)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setStyleSheet(f"""
            border: 1px solid {MANGO_ORANGE};
            border-radius: 3px;
            padding: 5px;
        """)
        self.search_input.setPlaceholderText("Search by vehicle number...")
        self.search_input.textChanged.connect(self.refresh_data)
        
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
        refresh_button.clicked.connect(lambda: self.refresh_data(force=True))
        
        filter_layout.addWidget(QLabel("Filter:"))
        filter_layout.addWidget(self.type_filter)
        filter_layout.addWidget(QLabel("Search:"))
        filter_layout.addWidget(self.search_input)
        filter_layout.addStretch(1)
        filter_layout.addWidget(refresh_button)
        
        # Table for parking history
        self.history_table = QTableWidget()
        self.history_table.setStyleSheet(TABLE_STYLE)
        self.history_table.setColumnCount(8)
        self.history_table.setHorizontalHeaderLabels([
            "Owner Name", "Mobile", "Vehicle Number", "Type", "Slot", 
            "Entry Time", "Exit Time", "Payment"
        ])
        
        # Set column widths
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Pagination layout
        pagination_layout = QHBoxLayout()
        
        self.prev_button = QPushButton("Previous")
        self.prev_button.setStyleSheet(BUTTON_STYLE)
        self.prev_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.prev_button.clicked.connect(self.prev_page)
        self.prev_button.setEnabled(False)
        
        self.page_label = QLabel("Page 1")
        self.page_label.setAlignment(Qt.AlignCenter)
        self.page_label.setStyleSheet("font-weight: bold;")
        
        self.next_button = QPushButton("Next")
        self.next_button.setStyleSheet(BUTTON_STYLE)
        self.next_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.next_button.clicked.connect(self.next_page)
        
        pagination_layout.addStretch(1)
        pagination_layout.addWidget(self.prev_button)
        pagination_layout.addWidget(self.page_label)
        pagination_layout.addWidget(self.next_button)
        pagination_layout.addStretch(1)
        
        # Add widgets to main layout
        main_layout.addWidget(title)
        main_layout.addLayout(filter_layout)
        main_layout.addWidget(self.history_table)
        main_layout.addLayout(pagination_layout)
        
        # Initial data load
        self.refresh_data()
    
    def refresh_data(self, force=False):
        """Refresh the history table with filtered data"""
        try:
            # Reset to first page if filter changed or forced
            if force:
                self.page = 0
            
            # Get filter values
            vehicle_type = self.type_filter.currentData()
            search_text = self.search_input.text().strip().upper()
            
            # Get parking history
            history_data = get_parking_history(limit=100, skip=0)  # Get all data
            
            # Apply filters
            filtered_data = []
            for entry in history_data:
                # Apply vehicle type filter
                if vehicle_type != "all" and entry.get("vehicle_type") != vehicle_type:
                    continue
                
                # Apply search filter
                if search_text and search_text not in entry.get("vehicle_number", "").upper():
                    continue
                
                filtered_data.append(entry)
            
            # Pagination
            start_idx = self.page * self.page_size
            end_idx = start_idx + self.page_size
            page_data = filtered_data[start_idx:end_idx]
            
            # Update pagination controls
            has_next = end_idx < len(filtered_data)
            has_prev = self.page > 0
            
            self.prev_button.setEnabled(has_prev)
            self.next_button.setEnabled(has_next)
            self.page_label.setText(f"Page {self.page + 1} of {max(1, (len(filtered_data) + self.page_size - 1) // self.page_size)}")
            
            # Clear the table
            self.history_table.setRowCount(0)
            
            # Fill the table with data
            for i, entry in enumerate(page_data):
                self.history_table.insertRow(i)
                
                # Owner name
                self.history_table.setItem(i, 0, QTableWidgetItem(entry.get("name", "")))
                
                # Mobile number
                self.history_table.setItem(i, 1, QTableWidgetItem(entry.get("mobile", "")))
                
                # Vehicle number
                vehicle_number_item = QTableWidgetItem(entry.get("vehicle_number", ""))
                vehicle_number_item.setFont(QFont("Arial", weight=QFont.Bold))
                self.history_table.setItem(i, 2, vehicle_number_item)
                
                # Vehicle type
                vehicle_type = "2-Wheeler" if entry.get("vehicle_type") == "2W" else "4-Wheeler"
                self.history_table.setItem(i, 3, QTableWidgetItem(vehicle_type))
                
                # Slot ID
                self.history_table.setItem(i, 4, QTableWidgetItem(entry.get("slot_id", "")))
                
                # Entry time
                entry_time = entry.get("entry_time", datetime.now())
                formatted_entry_time = entry_time.strftime("%Y-%m-%d %H:%M:%S")
                self.history_table.setItem(i, 5, QTableWidgetItem(formatted_entry_time))
                
                # Exit time
                exit_time = entry.get("exit_time")
                formatted_exit_time = exit_time.strftime("%Y-%m-%d %H:%M:%S") if exit_time else "Still Parked"
                self.history_table.setItem(i, 6, QTableWidgetItem(formatted_exit_time))
                
                # Payment
                payment = entry.get("payment", 0)
                payment_item = QTableWidgetItem(f"₹{payment}")
                payment_item.setFont(QFont("Arial", weight=QFont.Bold))
                if payment > 0:
                    payment_item.setForeground(Qt.darkGreen)
                self.history_table.setItem(i, 7, payment_item)
            
            # If no entries, show empty message
            if not page_data:
                self.history_table.setRowCount(1)
                empty_msg = QTableWidgetItem("No parking history found")
                empty_msg.setTextAlignment(Qt.AlignCenter)
                self.history_table.setSpan(0, 0, 1, 8)
                self.history_table.setItem(0, 0, empty_msg)
                
        except Exception as e:
            logging.error(f"Error refreshing history data: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to load history: {str(e)}")
    
    def next_page(self):
        """Go to next page"""
        self.page += 1
        self.refresh_data()
    
    def prev_page(self):
        """Go to previous page"""
        if self.page > 0:
            self.page -= 1
            self.refresh_data()
