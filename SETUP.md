"""
🚀 FIRST-TIME SETUP GUIDE
========================

Follow these steps to get Puppy running on your PC for the first time.
"""

# STEP 1: INSTALL PYTHON

✅ Check if Python is installed:
   - Open PowerShell
   - Type: python --version
   - You should see: Python 3.8+ (or higher)

❌ Python not installed?
   - Download from: https://www.python.org/downloads/
   - ✓ Check "Add Python to PATH" during installation
   - Restart PowerShell after installing


# STEP 2: INSTALL DEPENDENCIES

Run ONE of these commands in PowerShell:

Option A (Recommended - Automatic):
   cd C:\Users\YOUR_NAME\Desktop\clip\puppy
   python -m pip install -r requirements.txt

Option B (Manual - If option A fails):
   pip install flask==3.0.0
   pip install pyperclip==1.8.2
   pip install pynput==1.7.6
   pip install flask-socketio==5.3.5
   pip install pillow==10.1.0


# STEP 3: START THE SERVER

Double-click: run.bat

You should see:
```
================================================
🐕 Puppy Clipboard Sync - Setup
================================================
🚀 Starting Puppy Clipboard Sync...
📡 Server: http://0.0.0.0:5055
⌨️  Keyboard Capture: Available
📸 Screenshot: Available

 * Running on http://192.168.X.X:5055
```

✅ If you see this, it's working!


# STEP 4: FIND YOUR PC'S IP ADDRESS

Open PowerShell and type:
```
ipconfig
```

Look for **IPv4 Address** - it should look like:
   192.168.1.42
   or
   192.168.0.15

Note this down! You'll need it on your phone.


# STEP 5: OPEN ON YOUR PHONE

✅ Make sure your phone is on the SAME WiFi as your PC

Open Safari (iPhone) or Chrome (Android):
   http://192.168.X.X:5055

Replace 192.168.X.X with your PC's IP address from Step 4!

Example:
   http://192.168.1.42:5055


# STEP 6: TEST THE FEATURES

📋 **Clipboard Sync:**
   1. Copy something on PC (Ctrl+C)
   2. Tap "Get from PC" button on phone
   3. Text appears instantly!

⌨️ **Live Typing:**
   1. Tap "Live ON" button on phone
   2. Start typing on PC (in Notepad or any app)
   3. See your typing live on phone!

📸 **Screenshot Capture:**
   1. Tap "Capture" button on phone
   2. PC screen is captured
   3. Image appears on phone
   4. Long-press image to copy it!


# ⚠️ TROUBLESHOOTING

**Server won't start?**
→ Make sure Python is installed (python --version)
→ Check if port 5055 is in use
→ Try running in PowerShell directly: python app.py

**Can't connect from phone?**
→ Are you on same WiFi as PC?
→ Did you use correct IP address?
→ Try ping: ping [your-pc-ip]
→ Check firewall settings

**Live typing not working?**
→ Click "Live ON" button on phone
→ Make sure you're typing in a text box
→ Try typing in Notepad

**Screenshot not appearing?**
→ Refresh browser (F5 or Cmd+R)
→ Restart server (Ctrl+C → run.bat)
→ Check browser console for errors

**Long-press not copying?**
→ Use Safari browser (recommended)
→ Hold finger on image for 1-2 seconds
→ Try different browser if Safari doesn't work


# 🎉 YOU'RE DONE!

Your Puppy is now ready to sync!

Keep the PowerShell window open while using.
To stop: Press Ctrl+C in PowerShell.

For more help, see:
- README.md — Feature overview
- SCREENSHOT_GUIDE.md — Screenshot help
- ARCHITECTURE.md — Technical details


# 📱 BOOKMARK ON PHONE

For quick access, bookmark the URL on your phone:
1. Enter: http://192.168.X.X:5055
2. Press share icon
3. Select "Add Bookmark" or "Add to Home Screen"
4. Name it "Puppy"
5. Done! Easy access next time


# 🔧 FILE STRUCTURE

After setup, your folder should have:

puppy/
├── app.py                 ✅ Main server
├── config.py              ✅ Settings
├── keyboard_handler.py    ✅ Keyboard capture
├── screenshot_handler.py  ✅ Screenshot capture
├── ui.py                  ✅ Web interface
├── requirements.txt       ✅ Dependencies list
├── run.bat                ✅ Quick start
├── README.md              📖 Documentation
├── SCREENSHOT_GUIDE.md    📖 Screenshot help
├── ARCHITECTURE.md        📖 Technical docs
└── SETUP.md               📖 Setup guide
