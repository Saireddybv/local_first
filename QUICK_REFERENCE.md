"""
⚡ QUICK REFERENCE CARD
======================
Keep this handy for common commands and features.
"""

# 🚀 START & STOP

**OPTION 1: Normal (Shows Console Window)**
   Start: Double-click run.bat
   Stop:  Press Ctrl+C in the window

**OPTION 2: Hidden (Silent Background) ⭐**
   Start: Double-click run_silent.bat
          → Server runs invisibly
          → Window closes automatically
   
   Stop:  Double-click kill_server.bat
          → Confirms server stopped
   
   Check: Double-click check_server.bat
          → Shows if server is running


# 📝 IMPORTANT FILES

config.py
   - Toggle screenshot: ENABLE_SCREENSHOT = True
   - Set timeout: SCREENSHOT_TIMEOUT = 10 seconds
   - Change port: FLASK_PORT = 5055

app.py
   - Main server file
   - Don't modify unless you know Python

ui.py
   - Web interface colors and layout
   - Change gradient colors here

keyboard_handler.py
   - Keystroke capture logic
   - Thread-safe for concurrent use

screenshot_handler.py
   - Screenshot + OCR logic
   - Hotkey listener management


# 🎮 FEATURES CHEATSHEET

┌─ CLIPBOARD (📋) ────────────────────────┐
│ Get from PC:  Ctrl+C on PC              │
│ Copy to Phone: Tap "Get from PC" button  │
│ Speed: Instant                          │
└─────────────────────────────────────────┘

┌─ LIVE TYPING (⌨️) ──────────────────────┐
│ Start: Tap "Live ON" on phone           │
│ Type anywhere on PC                      │
│ See live on phone in real-time          │
│ Stop: Tap "Live OFF"                    │
└─────────────────────────────────────────┘

┌─ SCREENSHOT (📸) ──────────────────────┐
│ Capture: Tap "Capture" button on phone  │
│ Display: Shows live screenshot image     │
│ Copy: Long-press image and select copy   │
│ Clear: Tap "Clear" to remove image      │
│ Speed: <1 second                        │
└─────────────────────────────────────────┘


# 🔧 TROUBLESHOOTING QUICK FIXES

Problem               │ Solution
──────────────────────┼─────────────────────────
Capture button gone   │ Refresh browser (F5 or Cmd+R)
Can't connect phone   │ Check IP: ipconfig
                      │ Use same WiFi as PC
Image not displaying  │ Check browser console for errors
                      │ Restart server and try again
Live typing slow      │ Check if "Live ON" is active
Long-press not work   │ Native browser feature, try Safari
Port 5055 in use      │ Change FLASK_PORT in config.py


# 📱 ON YOUR PHONE

URL: http://[YOUR-PC-IP]:5055

Example:
   http://192.168.1.42:5055

Find your IP:
   ipconfig → IPv4 Address


# 🔐 CONFIGURATION QUICK EDIT

Change Port (in config.py):
   FLASK_PORT = 5055
   FLASK_PORT = 8080  (alternative)

Disable OCR (in config.py):
   ENABLE_OCR = True   → ENABLE_OCR = False


# 📊 PROJECT FILES AT A GLANCE

Core Files:
   ✅ app.py - Main server (don't touch unless needed)
   ✅ config.py - Settings (simple and clean)
   ✅ keyboard_handler.py - Keystroke capture
   ✅ screenshot_handler.py - Screenshot capture
   ✅ ui.py - Web interface
   ✅ run.bat - Quick start (double-click)
   ✅ requirements.txt - Dependencies list

Documentation:
   📖 README.md - Main guide
   📖 SETUP.md - First-time setup
   📖 SCREENSHOT_GUIDE.md - Screenshot help
   📖 ARCHITECTURE.md - Technical docs
   📖 CHANGES.md - What's new
   📖 QUICK_REFERENCE.md - This file!


# ⚙️ INSTALLATION CHECKLIST

□ Python installed (python --version)
□ Dependencies installed (pip install -r requirements.txt)
□ Server starts without errors (python app.py)
□ Can connect from phone (http://IP:5055)
□ All three panels visible on phone
□ Screenshot capture works (click Capture button)
□ Long-press copy works on image


# 💾 COMMON EDITS

Most Common Edit:
   → config.py (change port if 5055 is busy)

If Screenshot Doesn't Work:
   → Refresh browser page
   → Restart server
   → Check browser console for errors

If Image Won't Copy:
   → Use Safari browser (best compatibility)
   → Try different browser if needed
   → Use native long-press feature

If Connection Issues:
   → Verify same WiFi network
   → Check firewall allows python.exe
   → Verify correct IP address


# 🎯 FEATURE MATRIX

Feature              │ Speed  │ WebButton │ Requires
─────────────────────┼────────┼───────────┼──────────
Clipboard Sync       │ <100ms │ Yes       │ pyperclip
Live Typing          │ <50ms  │ Yes       │ pynput
Screenshot Capture   │ <1s    │ Yes       │ pillow


# 🏆 BEST PRACTICES

✅ DO:
   - Keep server running while using
   - Bookmark the URL on phone
   - Use same WiFi for all devices
   - Use Safari for best compatibility
   - Test features after setup

❌ DON'T:
   - Modify app.py unless you know Python
   - Close PowerShell while in use
   - Use different WiFi networks
   - Run multiple servers on port 5055
   - Take screenshots of fullscreen videos


# 🚨 DEBUG MODE

To see detailed logs:
   Edit config.py:
   DEBUG = True

Then restart server:
   python app.py

Check console for detailed error messages


# 📞 SUPPORT

For help, see:
   - README.md → FAQ section
   - SETUP.md → Troubleshooting
   - SCREENSHOT_GUIDE.md → Feature help
   - ARCHITECTURE.md → Technical help
   - Check console output for error messages


# 📦 BACKUP & RESTORE

Backup your settings:
   Copy config.py to safe location

Restore settings:
   Edit config.py values back

Factory reset:
   Delete config.py, use defaults


# 🎨 CUSTOMIZATION IDEAS

1. Change UI Colors
   Edit gradient in ui.py (line ~33)

2. Add New Hotkey
   Edit config.py and screenshot_handler.py

3. Support Different Language OCR
   Edit screenshot_handler.py (line ~52)

4. Change Port Number
   Edit config.py (FLASK_PORT)

5. Disable Certain Features
   Edit config.py and comment out in app.py
