# Architecture

One FastAPI application hosts local HTML/CSS/JavaScript, pairing, Files, Clip and an authenticated audio WebSocket. Uvicorn exposes one port. The loopback controller URL opens on startup; its secret is not printed in access logs. QR generation uses installed Python code and an SVG served locally.

Files stream to temporary files and are published without overwrite in the configured folder. FastAPI FileResponse supplies downloads and range support. Clip uses versioned updates and two-second polling, with a 400 ms typing debounce. Explicit laptop clipboard actions use pyperclip. Audio reuses the original bounded-queue WASAPI capture engine; the browser schedules PCM stereo chunks using Web Audio.

Pair requests expire after two minutes. Status reports recent phone polling rather than guaranteeing physical device presence. State belongs to one process; do not deploy multiple workers. Sessions and text disappear on restart. There is no database or cloud dependency.

## Extended modules

- `tools.py` installs routes and camera signaling using the server's existing authorization functions. Pydantic models constrain commands and sizes; capability switches default off.
- `desktop.py` isolates Win32 SendInput/LockWorkStation and Pillow screen capture. Tests replace this adapter instead of operating the developer's desktop.
- `storage.py` implements SQLite notes with version checks and closed per-operation connections.
- `actions.py` persists laptop-defined executable/argument lists. It launches without a shell, captures bounded output, and tracks exit state. A maximum of four processes run at once; the last 50 task records are retained in memory.
- `tls.py` creates a personal CA and a server certificate with LAN/loopback IP SANs. Trust installation is performed by the owner, not the app.
- `static/tools.js` manages the extra controls and peer-to-peer WebRTC. Signaling permits one phone sender and one loopback laptop receiver; leaving, revocation or permission removal tears down the feed.

Screen previews use authenticated finite image requests at up to 2 fps, avoiding unbounded video buffering and allowing permission checks for each frame. Notes survive restarts but the pad stays temporary. Task progress means actual process state/output, not integration with arbitrary third-party progress bars.
