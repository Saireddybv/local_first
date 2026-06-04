"""
SCREENSHOT CAPTURE FEATURE GUIDE
================================

This guide explains how to use the Screenshot feature in Puppy.
"""

# 🎯 QUICK START

1. Make sure server is running (double-click `run.bat`)
2. Open http://192.168.X.X:5055 on your phone
3. In the right panel "📸 Screenshot", tap "Capture"
4. Your PC screen will be captured instantly
5. Image appears on your phone screen
6. Long-press the image and select "Copy" to copy it

✅ That's it!


# 📱 HOW TO USE

**On Your Phone:**
1. Tap "Capture" button → Screen capture starts
2. Wait for image to appear (1-2 seconds)
3. Long-press the image to see the context menu
4. Select "Copy" or "Copy Image" from the menu
5. Paste wherever you need it (messages, notes, etc.)
6. Tap "Clear" to remove the image

**Display Features:**
- Shows full screenshot of your PC
- Image automatically sized to fit phone screen
- Rounded corners and shadow for clean look
- Stays until you tap "Clear"


# ⚙️ CONFIGURATION

Edit `config.py` to customize:

```python
ENABLE_SCREENSHOT = True       # Enable/disable feature
SCREENSHOT_TIMEOUT = 10        # Seconds before timeout
```

**Important:** Restart server after making config changes:
```
python app.py
```


# 🎨 FEATURES

✅ Instant screenshot capture (< 1 second)
✅ Full screen resolution captured
✅ Works on both Windows and Mac
✅ Web interface (no hotkey needed)
✅ Native long-press copy workflow
✅ Base64 image encoding for web transmission
✅ Displays perfectly on mobile Safari


# 🔧 TECHNICAL DETAILS

**Image Format:**
- Captured as PNG
- Encoded as Base64
- Transmitted via WebSocket
- Displays in browser
- Not saved to disk

**Performance:**
- Capture time: 500-1000ms
- Network transfer: <500ms
- Memory: ~1-5MB per screenshot
- No disk storage used

**Browser Compatibility:**
- ✅ Safari (iPhone) - Recommended
- ✅ Chrome (Android)
- ✅ Firefox
- ✅ Edge


# 💡 PRO TIPS

1. **Long-press not working?**
   - Make sure you're using Safari on iPhone
   - Hold your finger on the image for 1-2 seconds
   - Alternative: Try Chrome if Safari doesn't work

2. **Image too small?**
   - Zoom in on your phone (pinch to zoom)
   - Image scales with screen size

3. **Multiple captures?**
   - Each new capture replaces the old one
   - Tap "Clear" to remove before capturing again

4. **Capture partial screen?**
   - Currently captures full screen only
   - Take screenshot first, then crop on phone


# 🚨 TROUBLESHOOTING

**Image not appearing?**
- Check if server is running
- Refresh browser (F5 or Cmd+R on phone)
- Check browser console for errors
- Restart server

**Can't copy image?**
- Try Safari browser (best compatibility)
- Make sure to hold long-press for 1-2 seconds
- Try different browser if Safari doesn't work

**Capture takes too long?**
- That's normal (1-2 seconds is standard)
- Check WiFi connection quality
- Restart server if consistently slow

**Getting timeouts?**
- Increase SCREENSHOT_TIMEOUT in config.py
- Default is 10 seconds
- Restart server after changing


# 📝 NOTES

- Screenshots are temporary (deleted after session)
- No files saved to disk
- No OCR or text extraction
- Perfect for sharing quick visual information
- Works on same local WiFi network only

✅ Real-time results via WebSocket
✅ Screenshot preview on phone


# ⚡ PERFORMANCE

Typical times on modern PC:
- Screenshot capture: 0.5 seconds
- OCR processing: 2-3 seconds
- Total: 2.5-3.5 seconds

Faster on:
- Shorter text content
- Machines with better processors
- When using only part of screen (future feature)


# 🔍 TROUBLESHOOTING

**Hotkey not triggering?**
→ Check Windows Firewall allows python.exe
→ Try a different hotkey combination
→ Restart the server

**OCR shows no text?**
→ Make sure Tesseract is installed properly
→ Try a simple image first (text-rich screenshot)
→ Check console for error messages

**Slow OCR?**
→ OCR is CPU-intensive, slower on older machines
→ Disable OCR in `config.py` if needed
→ Use just the manual screenshot button


# 🚀 ADVANCED

To disable OCR and just capture screenshots:
```python
# In config.py
ENABLE_OCR = False
```

To manually trigger screenshot from phone:
1. Tap "📸 Capture Now" button
2. Results appear in the OCR text box


# 📊 WHAT DATA IS SENT

When you use the screenshot feature:
- PC captures full screen image
- Image is encoded as Base64
- Image + extracted text are sent to phone via WebSocket
- Nothing is stored, saved, or sent to cloud
- Only visible on phone's browser


# 🔒 PRIVACY

✅ All processing happens locally on your PC
✅ No internet connection required
✅ No data leaves your local WiFi network
✅ No user tracking or analytics
✅ Images not stored anywhere
✅ Completely offline after server stops
