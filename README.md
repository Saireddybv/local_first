# 🐕 Puppy — Wireless Clipboard Sync & Screenshot Sharing

Transfer text between your Windows PC and iPhone/Android **instantly**, capture and share screenshots, all without cloud storage or complicated setup. Just copy on your PC, paste on your phone over WiFi.

## ✨ Features

- **📋 Clipboard Sync** — Copy on Windows (Ctrl+C) → Paste on iPhone/Android
- **⌨️ Live Typing Capture** — See everything you type on your PC appear on your phone in real-time
- **📸 Screenshot Sharing** — Capture and display screen instantly on your phone
- **🔒 Local WiFi Only** — No cloud, no data tracking, 100% private
- **📱 Zero Apps Needed** — Works in any phone browser (Safari, Chrome)
- **⚡ No Setup Hassle** — Just run `run.bat` and open a URL
- **🎨 Three-Panel UI** — Clipboard, Live Typing, and Screenshot panels

## 🚀 Quick Start (30 seconds)

### Windows
1. Install Python (if not already installed)
2. Double-click **`run.bat`**
3. You'll see: `Server running at http://192.168.X.X:5055`

### iPhone/Android
1. Make sure your phone is on **same WiFi** as your PC
2. Open Safari (iPhone) or Chrome (Android)
3. Go to: `http://192.168.X.X:5055` (replace with your PC's IP)
4. Bookmark for quick access!

## 📖 How to Use

### Mode 1: Clipboard Sync (Left Panel)
```
1. Copy anything on your PC (Ctrl+C)
   → Email, Teams chat, code, URLs, anything works
2. Tap "⬇️ Get from PC" on your phone
3. Text appears instantly
4. Tap "📲 Copy" to add to phone clipboard
5. Paste normally (long-press → Paste)
```

### Mode 2: Live Typing (Middle Panel)
```
1. Tap "Live ON" button on your phone
2. Start typing ANYWHERE on your PC
   → Notepad, VS Code, Slack, email — it captures everything
3. Your text appears live on the phone screen
4. Tap "Copy" to copy what you typed
5. Tap "Clear" to reset
```

### Mode 3: Screenshot Sharing (Right Panel)
```
1. Open http://192.168.X.X:5055 on your phone
2. Tap "Capture" button
3. PC screen is captured instantly
4. Image appears on your phone
5. Long-press the image to copy it
6. Paste in messages, notes, or any app
7. Tap "Clear" to remove the image
```

**Screenshot Features:**
- Instant capture and display
- Full screen resolution
- Works on Windows and Mac
- No text extraction needed
- Perfect for sharing visuals

## 🛠️ Installation

### Method 1: Automatic (Windows) ⭐
Simply double-click:
```
run.bat
```

### Method 2: Manual Setup
```bash
# 1. Install dependencies
python -m pip install -r requirements.txt

# 2. Start server
python app.py
```

### Method 3: First-Time Setup (If Missing Dependencies)
```bash
# Windows: Run this in PowerShell as Administrator
pip install flask flask-socketio pyperclip pynput pillow
```

### Find Your PC's IP Address
Open PowerShell and run:
```bash
ipconfig
```
Look for **IPv4 Address** (e.g., `192.168.1.42`)

## 🔧 System Requirements

- **Windows 10/11** with Python 3.7+
- **iPhone** (any iOS with Safari) or **Android** (any phone with browser)
- Both devices on **same WiFi network**
- Port 5055 available (can be changed in code)

## ❓ FAQ

| Question | Answer |
|----------|--------|
| **Will it work from Teams/Gmail/Chrome?** | Yes! Ctrl+C from anywhere works |
| **Is it fast?** | Instant — Clipboard & typing <100ms, Screenshots <1 second |
| **What about security?** | Local WiFi only, nothing stored, nothing sent to cloud |
| **Can multiple people use it?** | Yes, same network, any number of phones |
| **Does it work over internet?** | No, WiFi only (intentional for privacy) |
| **Can I transfer files?** | Currently text and images only |
| **How many images can I capture?** | Unlimited — images stored in memory only, not on disk |
| **What browsers are supported?** | Safari (iOS), Chrome, Firefox, Edge — all work great |
| **Can I change the port?** | Yes, edit `config.py` → `FLASK_PORT` |

## 🐛 Troubleshooting

**"Cannot connect to server"**
- ✅ Both devices on same WiFi?
- ✅ Using correct IP? (Run `ipconfig` on PC)
- ✅ Did you include `:5055` at the end?

**"Windows Firewall is blocking"**
- Allow `python.exe` through Windows Defender Firewall

**"Server won't start"**
- Make sure port 5055 is free (no other app using it)
- Try: `netstat -ano | findstr :5055`

**"Live typing not working"**
- Make sure you clicked "Live ON" button
- Try pressing keys in a text app (Notepad, browser)

**"Screenshot not appearing"**
- ✅ Refresh browser (F5 or Cmd+R)
- ✅ Restart server (Ctrl+C then `python app.py`)
- ✅ Check browser console for errors

**"Long-press copy not working"**
- Use Safari on iPhone (best compatibility)
- Try Chrome or Firefox if Safari doesn't work
- Hold finger on image for 1-2 seconds

**"Screenshot button does nothing"**
- Make sure WebSocket is connected (check browser console)
- Try refreshing the page
- Check if Pillow is installed: `pip list | findstr pillow`

## 🏗️ Project Structure

```
puppy/
├── app.py                      # Main Flask + WebSocket server
├── config.py                   # Configuration & constants
├── keyboard_handler.py         # Keyboard event handling
├── screenshot_handler.py       # Screenshot capture & OCR
├── ui.py                       # HTML/CSS/JS templates
├── requirements.txt            # Python dependencies
├── run.bat                     # Windows quick-start launcher
├── README.md                   # This file
└── .gitignore                  # Git ignore rules
```

### File Responsibilities:
- **app.py** — Flask routes, WebSocket events, server setup
- **config.py** — All settings (ports, screenshot timeout)
- **keyboard_handler.py** — Keyboard listener & keystroke capture
- **screenshot_handler.py** — Screenshot capture and web interface management
- **ui.py** — HTML template with 3-panel interface
- **requirements.txt** — Python package dependencies

## 📦 Dependencies

- **Flask** — Web server framework
- **flask-socketio** — WebSocket for real-time updates
- **pyperclip** — Read Windows clipboard
- **pynput** — Capture keyboard events
- **Pillow** — Image processing (screenshots)
- **python-socketio** & **python-engineio** — WebSocket transport layer

## 🎯 How It Works Under the Hood

1. **Clipboard Sync**: `pyperclip` reads your Windows clipboard when you tap "Get from PC"
2. **Live Typing**: `pynput.Listener` captures all keystrokes and sends via WebSocket
3. **Screenshots**: `PIL.ImageGrab` captures the full screen (built-in Python)
4. **Real-time Updates**: WebSocket connection between PC and phone for instant updates
5. **Web UI**: Vanilla JavaScript for responsive three-panel interface
6. **Image Transmission**: Base64 encoding for cross-platform compatibility

## 🔮 Planned Features

- [ ] Clipboard history (last 20 items)
- [ ] Auto-sync mode (sync every 5 seconds)
- [ ] Dark mode
- [ ] File transfer
- [ ] Voice input
- [ ] Sync between multiple phones

## 🤝 Contributing

Found a bug? Have an idea? **Pull requests welcome!**

1. Fork the repo
2. Create a branch: `git checkout -b feature/your-feature`
3. Commit: `git commit -am 'Add feature'`
4. Push: `git push origin feature/your-feature`
5. Open a Pull Request

## 📄 License

MIT License — Use, modify, and share freely!

## 🙋 Support

**Having issues?** Check the [Troubleshooting](#-troubleshooting) section or open an issue.

---

**Made with ❤️ for seamless PC-to-Phone text transfer**
