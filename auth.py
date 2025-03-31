import logging

# Hardcoded admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "team@10"

def authenticate(username, password):
    logging.debug(f"Authenticating user: {username}")
    
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        logging.info("Authentication successful")
        return True
    else:
        logging.warning(f"Authentication failed for user: {username}")
        return False

    """
    Authenticate the admin user with hardcoded credentials.
    
    Args:
        username (str): The input username
        password (str): The input password
        
    Returns:
        bool: True if authentication successful, False otherwise
    """