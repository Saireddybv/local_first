"""
UI templates and frontend components
"""

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>🐕 Puppy - Clipboard Sync</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { 
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      min-height: 100vh;
      padding: 10px;
      display: flex;
    }
    .main-container { 
      display: flex; 
      gap: 10px; 
      width: 100%; 
      max-width: 1400px;
      margin: 0 auto;
    }
    .panel { 
      background: white; 
      padding: 20px; 
      border-radius: 15px; 
      box-shadow: 0 8px 32px rgba(0,0,0,0.1);
      flex: 1; 
      display: flex; 
      flex-direction: column;
      min-height: 600px;
    }
    .buttons-row { 
      display: flex; 
      gap: 8px; 
      margin-bottom: 15px; 
      flex-wrap: wrap; 
    }
    button { 
      padding: 10px 15px; 
      font-size: 13px; 
      cursor: pointer; 
      border: none; 
      border-radius: 8px; 
      background: linear-gradient(135deg, #667eea, #764ba2);
      color: white; 
      font-weight: 600; 
      flex: 1; 
      min-width: 80px; 
      white-space: nowrap;
      transition: all 0.3s ease;
    }
    button:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4); }
    button:active { transform: translateY(0); }
    .toggle-btn { background: linear-gradient(135deg, #f093fb, #f5576c); }
    .toggle-btn.active { background: linear-gradient(135deg, #4facfe, #00f2fe); }
    button.screenshot-btn { background: linear-gradient(135deg, #43e97b, #38f9d7); }
    textarea { 
      width: 100%; 
      flex: 1; 
      font-size: 14px; 
      padding: 12px; 
      border: 1px solid #e0e0e0; 
      border-radius: 8px; 
      box-sizing: border-box; 
      resize: none; 
      font-family: 'Monaco', 'Menlo', monospace;
      background: #fafafa;
    }
    .status { 
      color: #999; 
      margin-top: 10px; 
      font-weight: 500; 
      font-size: 12px;
    }
    .status.error { color: #e74c3c !important; }
    .status.warning { color: #f39c12 !important; }
    .status.success { color: #27ae60 !important; }
    h3 { 
      color: #333; 
      margin: 0 0 15px 0; 
      font-size: 18px; 
      border-bottom: 3px solid #667eea; 
      padding-bottom: 10px; 
    }
    .mode-label { 
      font-size: 12px; 
      color: #999; 
      margin-top: 8px; 
    }
    .panel-divider { 
      width: 1px; 
      background: #e0e0e0; 
    }
    .hotkey-info {
      background: #f0f0f0;
      padding: 10px;
      border-radius: 6px;
      font-size: 11px;
      color: #666;
      margin-top: 10px;
      border-left: 3px solid #667eea;
    }
    .screenshot-preview {
      max-width: 100%;
      max-height: 200px;
      border-radius: 8px;
      margin-top: 10px;
      display: none;
    }
    @media (max-width: 1024px) { 
      .main-container { flex-direction: column; }
      .panel { min-height: 400px; }
    }
  </style>
</head>
<body>
  <div class="main-container">
    <!-- Left Panel: Clipboard -->
    <div class="panel">
      <h3>📋 Clipboard from PC</h3>
      <div class="buttons-row">
        <button onclick="fetchClip()">⬇️ Get from PC</button>
        <button onclick="copyToPhone()">📲 Copy</button>
      </div>
      <textarea id="clipboardBox" placeholder="Click 'Get from PC' to fetch clipboard content..."></textarea>
      <div id="clipStatus" class="status"></div>
    </div>

    <!-- Middle Panel: Live Typing -->
    <div class="panel">
      <h3>⌨️ Live Typing</h3>
      <div class="buttons-row">
        <button class="toggle-btn" id="toggleBtn" onclick="toggleLiveCapture()">Live ON</button>
        <button onclick="clearLiveBox()">Clear</button>
        <button onclick="copyLiveBox()">Copy</button>
      </div>
      <textarea id="liveBox" placeholder="Enable 'Live' to capture all typing from your PC..."></textarea>
      <div id="liveStatus" class="status"></div>
      <div class="mode-label" id="modeLabel"></div>
    </div>

    <!-- Right Panel: Screenshot -->
    <div class="panel">
      <h3>📸 Screenshot</h3>
      <div class="buttons-row">
        <button class="screenshot-btn" onclick="captureScreenshot()">Capture</button>
        <button onclick="clearScreenshot()">Clear</button>
      </div>
      <div id="screenshotContainer" style="display: none; flex: 1; display: flex; flex-direction: column; justify-content: center; align-items: center;">
        <img id="screenshotImage" style="max-width: 100%; max-height: 100%; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);" alt="Screenshot">
      </div>
      <textarea id="screenshotPlaceholder" style="flex: 1;" placeholder="Click 'Capture' to take a screenshot. Long-press the image to copy it..."></textarea>
      <div id="screenshotStatus" class="status"></div>
    </div>
  </div>

  <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
  <script>
    let socket = null;
    let isLiveCapturing = false;

    function initWebSocket() {
      socket = io();
      socket.on('connect', () => {
        console.log('✅ Connected to server');
      });
      socket.on('keystroke', (data) => {
        const liveBox = document.getElementById('liveBox');
        if (data.key === '\b') {
          liveBox.value = liveBox.value.slice(0, -1);
        } else {
          liveBox.value += data.key;
        }
        liveBox.scrollTop = liveBox.scrollHeight;
      });
      socket.on('live_status', (data) => {
        document.getElementById('modeLabel').innerText = '🔴 Status: ' + data.status;
      });
      socket.on('screenshot_result', (data) => {
        if (data.success) {
          const container = document.getElementById('screenshotContainer');
          const placeholder = document.getElementById('screenshotPlaceholder');
          const img = document.getElementById('screenshotImage');
          
          if (data.image_base64) {
            img.src = 'data:image/png;base64,' + data.image_base64;
            container.style.display = 'flex';
            placeholder.style.display = 'none';
          }
          document.getElementById('screenshotStatus').innerText = '✅ Screenshot captured!';
          document.getElementById('screenshotStatus').className = 'status success';
        } else {
          document.getElementById('screenshotStatus').innerText = '❌ ' + (data.error || 'Capture failed');
          document.getElementById('screenshotStatus').className = 'status error';
        }
      });
    }

    function fetchClip() {
      document.getElementById('clipStatus').innerText = '⏳ Fetching...';
      document.getElementById('clipStatus').className = 'status';
      fetch('/get').then(r => r.json()).then(d => {
        document.getElementById('clipboardBox').value = d.text;
        document.getElementById('clipStatus').innerText = '✅ Fetched!';
        document.getElementById('clipStatus').className = 'status success';
      }).catch(e => {
        document.getElementById('clipStatus').innerText = '❌ Connection error';
        document.getElementById('clipStatus').className = 'status error';
      });
    }

    function copyToPhone() {
      const text = document.getElementById('clipboardBox').value;
      if (!text) {
        document.getElementById('clipStatus').innerText = '❌ No text to copy';
        document.getElementById('clipStatus').className = 'status error';
        return;
      }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(() => {
          document.getElementById('clipStatus').innerText = '✅ Copied to phone!';
          document.getElementById('clipStatus').className = 'status success';
        }).catch(() => {
          fallbackCopy(text, 'clipboardBox', 'clipStatus');
        });
      } else {
        fallbackCopy(text, 'clipboardBox', 'clipStatus');
      }
    }

    function fallbackCopy(text, elementId, statusId) {
      const textarea = document.getElementById(elementId);
      textarea.select();
      try {
        document.execCommand('copy');
        document.getElementById(statusId).innerText = '✅ Copied!';
        document.getElementById(statusId).className = 'status success';
      } catch (err) {
        document.getElementById(statusId).innerText = '❌ Copy failed';
        document.getElementById(statusId).className = 'status error';
      }
    }

    function toggleLiveCapture() {
      isLiveCapturing = !isLiveCapturing;
      const btn = document.getElementById('toggleBtn');
      if (isLiveCapturing) {
        btn.innerText = 'Live OFF';
        btn.classList.add('active');
        document.getElementById('liveBox').value = '';
        document.getElementById('liveStatus').innerText = '🔴 Capturing keystrokes...';
        document.getElementById('liveStatus').className = 'status warning';
        socket.emit('start_capture');
      } else {
        btn.innerText = 'Live ON';
        btn.classList.remove('active');
        document.getElementById('liveStatus').innerText = '⚪ Capture disabled';
        document.getElementById('liveStatus').className = 'status';
        document.getElementById('modeLabel').innerText = '';
        socket.emit('stop_capture');
      }
    }

    function clearLiveBox() {
      document.getElementById('liveBox').value = '';
      document.getElementById('liveStatus').innerText = '';
    }

    function copyLiveBox() {
      const text = document.getElementById('liveBox').value;
      if (!text) {
        document.getElementById('liveStatus').innerText = '❌ No text to copy';
        document.getElementById('liveStatus').className = 'status error';
        return;
      }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(() => {
          document.getElementById('liveStatus').innerText = '✅ Copied!';
          document.getElementById('liveStatus').className = 'status success';
        }).catch(() => {
          fallbackCopy(text, 'liveBox', 'liveStatus');
        });
      } else {
        fallbackCopy(text, 'liveBox', 'liveStatus');
      }
    }

    function captureScreenshot() {
      document.getElementById('screenshotStatus').innerText = '⏳ Capturing...';
      document.getElementById('screenshotStatus').className = 'status';
      socket.emit('request_screenshot');
    }

    function clearScreenshot() {
      document.getElementById('screenshotContainer').style.display = 'none';
      document.getElementById('screenshotPlaceholder').style.display = 'block';
      document.getElementById('screenshotImage').src = '';
      document.getElementById('screenshotStatus').innerText = '';
    }

    window.addEventListener('load', () => {
      initWebSocket();
      fetchClip();
    });
  </script>
</body>
</html>
"""
