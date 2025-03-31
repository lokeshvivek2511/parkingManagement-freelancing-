from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QPushButton, 
                            QVBoxLayout, QHBoxLayout, QGridLayout, 
                            QMessageBox, QFrame)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap, QFont, QCursor

from ui.parking_grid import ParkingGridWindow
from ui.styles import (MANGO_YELLOW, MANGO_ORANGE, MANGO_DARK_ORANGE, 
                      NEUTRAL_DARK, NEUTRAL_LIGHT, BUTTON_STYLE, 
                      INPUT_STYLE, TITLE_STYLE, SUBTITLE_STYLE)
from auth import authenticate

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        # Set window properties
        self.setWindowTitle("Parking Management System - Login")
        self.setGeometry(100, 100, 800, 500)
        self.setStyleSheet(f"background-color: {NEUTRAL_LIGHT};")
        
        # Main layout
        main_layout = QHBoxLayout()
        
        # Left panel (decoration)
        left_panel = QFrame()
        left_panel.setStyleSheet(f"background-color: {MANGO_ORANGE}; border-radius: 10px;")
        left_layout = QVBoxLayout(left_panel)
        
        # Logo or illustration would go here
        # Using a label with styled text instead
        logo_label = QLabel("P")
        logo_label.setStyleSheet(f"""
            font-size: 120px;
            font-weight: bold;
            color: {NEUTRAL_LIGHT};
            background-color: {MANGO_DARK_ORANGE};
            border-radius: 60px;
            padding: 20px;
        """)
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setFixedSize(150, 150)
        
        app_name = QLabel("Parking Management System")
        app_name.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {NEUTRAL_DARK};")
        app_name.setAlignment(Qt.AlignCenter)
        
        app_subtitle = QLabel("Manage Your Parking Space Efficiently")
        app_subtitle.setStyleSheet(f"font-size: 16px; color: {NEUTRAL_DARK};")
        app_subtitle.setAlignment(Qt.AlignCenter)
        
        left_layout.addStretch(1)
        left_layout.addWidget(logo_label, 0, Qt.AlignCenter)
        left_layout.addWidget(app_name, 0, Qt.AlignCenter)
        left_layout.addWidget(app_subtitle, 0, Qt.AlignCenter)
        left_layout.addStretch(1)
        
        # Right panel (login form)
        right_panel = QFrame()
        right_panel.setStyleSheet("background-color: white; border-radius: 10px;")
        right_layout = QVBoxLayout(right_panel)
        
        login_title = QLabel("Admin Login")
        login_title.setStyleSheet(TITLE_STYLE)
        login_title.setAlignment(Qt.AlignCenter)
        
        form_layout = QGridLayout()
        form_layout.setSpacing(15)
        
        username_label = QLabel("Username:")
        username_label.setStyleSheet(SUBTITLE_STYLE)
        self.username_input = QLineEdit()
        self.username_input.setStyleSheet(INPUT_STYLE)
        self.username_input.setFixedHeight(40)
        self.username_input.setPlaceholderText("Enter admin username")
        
        password_label = QLabel("Password:")
        password_label.setStyleSheet(SUBTITLE_STYLE)
        self.password_input = QLineEdit()
        self.password_input.setStyleSheet(INPUT_STYLE)
        self.password_input.setFixedHeight(40)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Enter password")
        
        # Add widgets to form layout
        form_layout.addWidget(username_label, 0, 0)
        form_layout.addWidget(self.username_input, 0, 1)
        form_layout.addWidget(password_label, 1, 0)
        form_layout.addWidget(self.password_input, 1, 1)
        
        # Login button
        self.login_button = QPushButton("Login")
        self.login_button.setStyleSheet(BUTTON_STYLE)
        self.login_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.login_button.setFixedHeight(45)
        self.login_button.clicked.connect(self.handle_login)
        
        # Add widgets to right layout
        right_layout.addStretch(1)
        right_layout.addWidget(login_title)
        right_layout.addSpacing(30)
        right_layout.addLayout(form_layout)
        right_layout.addSpacing(30)
        right_layout.addWidget(self.login_button)
        right_layout.addStretch(1)
        
        # Add panels to main layout
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 1)
        
        self.setLayout(main_layout)
        
        # Set Enter key to trigger login
        self.password_input.returnPressed.connect(self.handle_login)
        self.username_input.returnPressed.connect(lambda: self.password_input.setFocus())
    
    def handle_login(self):
        """Handle the login button click event"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "Login Failed", "Please enter both username and password")
            return
            
        if authenticate(username, password):
            self.open_main_window()
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password")
            self.password_input.clear()
            self.password_input.setFocus()
    
    def open_main_window(self):
        """Open the main window after successful login"""
        self.main_window = ParkingGridWindow()
        self.main_window.show()
        self.close()
