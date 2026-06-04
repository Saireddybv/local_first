"""
ARCHITECTURE & MODULAR DESIGN GUIDE
====================================

This document explains the new modular project structure and how components work together.
"""

# 🏗️ PROJECT ARCHITECTURE

The project is now split into focused, reusable modules:

```
app.py (Main Application)
    ├─ imports config.py (settings)
    ├─ imports keyboard_handler.py (keystroke capture)
    ├─ imports screenshot_handler.py (screenshot capture)
    ├─ imports ui.py (HTML template)
    └─ defines Flask routes and WebSocket events

ui.py (User Interface)
    └─ exports HTML_TEMPLATE (3-panel interface)

config.py (Configuration)
    ├─ FLASK_HOST, FLASK_PORT, FLASK_SECRET_KEY
    ├─ ENABLE_SCREENSHOT
    ├─ SCREENSHOT_TIMEOUT
    └─ CORS_ALLOWED_ORIGINS

keyboard_handler.py (Keyboard Events)
    ├─ class KeyboardHandler
    │   ├─ start_listening()
    │   ├─ stop_listening()
    │   └─ set_keystroke_callback()
    └─ global instance: keyboard_handler

screenshot_handler.py (Screenshot Capture)
    ├─ class ScreenshotHandler
    │   ├─ capture_screenshot()
    │   ├─ set_screenshot_callback()
    │   └─ get_last_screenshot_image()
    └─ global instance: screenshot_handler
```


# 📡 DATA FLOW

## Web Screenshot Capture Flow

```
User clicks "Capture" button on phone
    ↓
JavaScript emits 'request_screenshot' via WebSocket
    ↓
Flask route handle_screenshot_request() triggered
    ↓
ScreenshotHandler.capture_screenshot() called
    ↓
PIL.ImageGrab captures screen
    ↓
Image encoded to Base64 PNG
    ↓
Result sent via on_screenshot_capture() callback
    ↓
socketio.emit('screenshot_result', response)
    ↓
JavaScript receives and displays image on phone
    ↓
User long-presses to copy image
```

## Live Typing Flow

```
User types on PC
    ↓
KeyboardHandler.on_press() detects keystroke
    ↓
_key_to_char() converts key to character
    ↓
keystroke_callback(char) called → emit_keystroke()
    ↓
socketio.emit('keystroke', {'key': char})
    ↓
JavaScript receives and appends to textarea
```

## Clipboard Sync Flow

```
User clicks "Get from PC" on phone
    ↓
JavaScript calls fetch('/get')
    ↓
Flask route get_clip() executes
    ↓
pyperclip.paste() reads clipboard
    ↓
Returns JSON: {"text": "..."}
    ↓
JavaScript displays in textarea
```


# 🔄 COMPONENT INTERACTION

### app.py ↔ keyboard_handler.py

```python
# In app.py, when client requests live capture:
@socketio.on('start_capture')
def handle_start_capture():
    keyboard_handler.set_keystroke_callback(emit_keystroke)
    keyboard_handler.start_listening()
```

### app.py ↔ screenshot_handler.py

```python
# In app.py, initialization:
screenshot_handler.set_screenshot_callback(on_screenshot_capture)

# In app.py, when user clicks Capture button on phone:
@socketio.on('request_screenshot')
def handle_screenshot_request():
    result = screenshot_handler.capture_screenshot()
    emit('screenshot_result', result, to=None)
```

### app.py ↔ ui.py

```python
# In app.py, serve UI:
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)
```


# 🎯 DESIGN PRINCIPLES

1. **Separation of Concerns**
   - Each module has ONE responsibility
   - app.py = server logic only
   - ui.py = frontend only
   - keyboard_handler.py = keystroke capture only
   - screenshot_handler.py = screenshot + OCR only

2. **Configuration Centralization**
   - All settings in config.py
   - Easy to modify without changing other files
   - Single source of truth

3. **Callback Pattern**
   - Handlers don't directly emit WebSocket events
   - They call callbacks passed to them
   - Loose coupling between modules
   - Easy to test each module independently

4. **Global Instances**
   - keyboard_handler, screenshot_handler defined at module level
   - Imported in app.py
   - Single instance throughout application
   - Thread-safe for concurrent operations


# 🧪 TESTING INDIVIDUAL MODULES

### Test Keyboard Handler
```python
from keyboard_handler import KeyboardHandler

handler = KeyboardHandler()
handler.set_keystroke_callback(lambda char: print(f"Key: {char}"))
handler.start_listening()
# Type something...
handler.stop_listening()
```

### Test Screenshot Handler
```python
from screenshot_handler import ScreenshotHandler

sh = ScreenshotHandler(enable_ocr=True)
result = sh.capture_screenshot()
print(result['ocr_text'])
print(f"Image size: {result['resolution']}")
```

### Test Screenshot Callback
```python
from screenshot_handler import ScreenshotHandler

sh = ScreenshotHandler()
sh.set_screenshot_callback(lambda result: print(f"Screenshot: {result['success']}"))
result = sh.capture_screenshot()
print(f"Image size: {result['resolution']}")
```


# 🔌 ADDING NEW FEATURES

### Adding a new handler (e.g., Clipboard Monitor)

1. Create `clipboard_monitor.py`:
```python
class ClipboardMonitor:
    def __init__(self):
        self.callback = None
        
    def set_callback(self, callback):
        self.callback = callback
        
    def monitor(self):
        # Watch clipboard for changes
        pass
```

2. Update `app.py`:
```python
from clipboard_monitor import ClipboardMonitor

monitor = ClipboardMonitor()
monitor.set_callback(emit_clipboard_change)

@socketio.on('start_monitor')
def handle_start_monitor():
    monitor.monitor()
```

3. Update `ui.py` to add new UI elements

4. Update `config.py` if needed


# 📦 DEPENDENCY MANAGEMENT

Current dependencies:
- `flask`, `flask-socketio` — Web server
- `pyperclip` — Clipboard access
- `pynput` — Keyboard capture
- `pillow` — Screenshot capture
- `python-socketio`, `python-engineio` — WebSocket transport

To add new dependency:
1. Add to `requirements.txt`
2. Import at top of relevant module
3. Handle ImportError gracefully:
   ```python
   try:
       import newlib
       NEWLIB_AVAILABLE = True
   except ImportError:
       NEWLIB_AVAILABLE = False
       print("Warning: newlib not installed")
   ```


# 🎯 PERFORMANCE OPTIMIZATION

Current optimizations:
- Global instances prevent repeated initialization
- Callbacks use event-driven pattern (no polling)
- WebSocket for low-latency updates
- Base64 encoding for image transmission

Future optimizations:
- Partial screenshot support (faster OCR)
- Image compression before sending
- Caching of OCR results
- Thread pools for concurrent operations


# 🔐 ERROR HANDLING

All modules include try-except blocks:
- Graceful degradation (e.g., OCR optional)
- Logged errors to console
- User-friendly error messages
- No silent failures

Example:
```python
try:
    screenshot = ImageGrab.grab()
except Exception as e:
    return {"error": f"Screenshot failed: {str(e)}", "success": False}
```


# 📝 ADDING DOCUMENTATION

For each new module, add:
1. Module docstring at top
2. Class docstrings
3. Method docstrings with parameters
4. Example usage in comments
5. Update this ARCHITECTURE.md file


# 🚀 DEPLOYMENT

Current setup for development/local use.

For production deployment:
1. Use proper WSGI server (gunicorn)
2. Add authentication
3. Rate limiting for WebSocket events
4. Better error handling
5. Logging system
6. Configuration management
