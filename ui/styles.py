"""
Styles module for the Parking Management System.
Contains colors, styles, and other visual constants.
Uses the Mango Dreams color theme.
"""

# Color scheme based on Mango Dreams theme
MANGO_YELLOW = "#FFD966"  # Primary yellow
MANGO_ORANGE = "#F9B572"  # Light orange
MANGO_DARK_ORANGE = "#F79D65"  # Darker orange
MANGO_RED = "#E85D5D"  # For warnings, occupied slots
MANGO_GREEN = "#8BBF9F"  # For success, available slots

# Neutral colors
NEUTRAL_DARK = "#333333"  # For text
NEUTRAL_MEDIUM = "#666666"  # For secondary text
NEUTRAL_LIGHT = "#F5F5F5"  # For backgrounds

# Common styles
TITLE_STYLE = f"""
    font-size: 28px;
    font-weight: bold;
    color: {NEUTRAL_DARK};
    margin-bottom: 10px;
"""

SUBTITLE_STYLE = f"""
    font-size: 16px;
    font-weight: bold;
    color: {NEUTRAL_DARK};
"""

BUTTON_STYLE = f"""
    background-color: {MANGO_DARK_ORANGE};
    color: white;
    border: none;
    border-radius: 5px;
    padding: 10px 15px;
    font-size: 16px;
    font-weight: bold;
"""

BUTTON_STYLE_SECONDARY = f"""
    background-color: {MANGO_YELLOW};
    color: {NEUTRAL_DARK};
    border: none;
    border-radius: 5px;
    padding: 8px 12px;
    font-size: 14px;
    font-weight: bold;
"""

BUTTON_STYLE_DANGER = f"""
    background-color: {MANGO_RED};
    color: white;
    border: none;
    border-radius: 5px;
    padding: 8px 12px;
    font-size: 14px;
    font-weight: bold;
"""

INPUT_STYLE = f"""
    border: 2px solid {MANGO_ORANGE};
    border-radius: 5px;
    padding: 8px 12px;
    font-size: 14px;
    color: {NEUTRAL_DARK};
    background-color: white;
"""

TABLE_STYLE = f"""
    QTableWidget {{
        background-color: white;
        border: 1px solid {MANGO_ORANGE};
        border-radius: 5px;
        gridline-color: {MANGO_YELLOW};
    }}
    QTableWidget::item {{
        padding: 8px;
    }}
    QHeaderView::section {{
        background-color: {MANGO_DARK_ORANGE};
        color: white;
        padding: 8px;
        font-weight: bold;
        border: none;
    }}
"""

# Slot styles for parking grid
SLOT_AVAILABLE_STYLE = f"""
    background-color: {MANGO_GREEN};
    color: {NEUTRAL_DARK};
    border: 1px solid {NEUTRAL_DARK};
    border-radius: 5px;
    font-weight: bold;
    padding: 5px;
"""

SLOT_OCCUPIED_STYLE = f"""
    background-color: {MANGO_RED};
    color: white;
    border: 1px solid {NEUTRAL_DARK};
    border-radius: 5px;
    font-weight: bold;
    padding: 5px;
"""

TAB_STYLE = f"""
    QTabWidget::pane {{
        border: 1px solid {MANGO_ORANGE};
        border-radius: 5px;
        background-color: white;
    }}
    QTabBar::tab {{
        background-color: {NEUTRAL_LIGHT};
        color: {NEUTRAL_DARK};
        border: 1px solid {MANGO_ORANGE};
        border-bottom: none;
        border-top-left-radius: 5px;
        border-top-right-radius: 5px;
        padding: 8px 15px;
        margin-right: 2px;
    }}
    QTabBar::tab:selected {{
        background-color: {MANGO_ORANGE};
        color: white;
        font-weight: bold;
    }}
"""
