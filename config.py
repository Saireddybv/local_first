"""
Configuration and constants for Puppy Clipboard Sync
"""

# Flask Configuration
FLASK_HOST = '0.0.0.0'
FLASK_PORT = 5055
FLASK_SECRET_KEY = 'clipboard-sync-secret'

# Screenshot Configuration
ENABLE_SCREENSHOT = True
SCREENSHOT_TIMEOUT = 10  # seconds

# Server Configuration
CORS_ALLOWED_ORIGINS = "*"
DEBUG = False
