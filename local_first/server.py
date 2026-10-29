from __future__ import annotations
import asyncio
import contextlib
import io
import os
import secrets
import time
from pathlib import Path
from urllib.parse import urlsplit
import qrcode
import qrcode.image.svg
from fastapi import FastAPI, Request, HTTPException, WebSocket
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from .audio import AudioBridge, AudioConfig
from .tools import install_tools

STATIC = Path(__file__).parent / "static"

def create_app(data_dir=None, state_dir=None):
    default = Path("D:/Local First Files") if os.name == "nt" and Path("D:/").exists() else Path.home() / "Local First Files"
    folder = Path(data_dir or os.environ.get("LOCAL_FIRST_DATA", default))
    folder.mkdir(parents=True, exist_ok=True)
    admin = secrets.token_urlsafe(32)
    invite = secrets.token_urlsafe(24)
    sessions = {}
    pending = {}
    pad = {"text": "", "version": 0}
    bridge = AudioBridge(AudioConfig())
    @contextlib.asynccontextmanager
    async def lifespan(app):
        bridge.start()
        try:
            yield
        finally:
            await app.state.tools.revoke()
            bridge.stop()
    app = FastAPI(title="Local First", lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)
    app.state.admin = admin
    app.state.invite = invite
    app.state.folder = folder
    app.state.public_url = "http://127.0.0.1:8000"
    app.mount("/static", StaticFiles(directory=STATIC), name="static")

    def is_admin(request):
        return request.cookies.get("lf_admin") == admin and request.client.host in ("127.0.0.1", "::1", "testclient")
    def authorized(request):
        token = request.cookies.get("lf_session")
        if is_admin(request):
            return True
        if token in sessions:
            sessions[token] = time.monotonic()
            return True
        return False
    @app.middleware("http")
    async def guard(request, call_next):
        origin = request.headers.get("origin")
        if origin and urlsplit(origin).netloc != request.headers.get("host"):
            return Response("Cross-origin request rejected", status_code=403)
        if request.url.path.startswith("/api/") and request.url.path not in ("/api/pair", "/api/pair-status"):
            if not authorized(request):
                return Response("Pair this device first", status_code=401)
        result = await call_next(request)
        result.headers["Cache-Control"] = "no-store"
        result.headers["X-Content-Type-Options"] = "nosniff"
        result.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data: blob:; connect-src 'self'; media-src 'self' blob:; frame-ancestors 'none'"
        return result
    @app.get("/")
    async def home():
        return FileResponse(STATIC / "index.html")
    @app.get("/admin/{token}")
    async def login(token: str, request: Request):
        if token != admin or request.client.host not in ("127.0.0.1", "::1", "testclient"):
            raise HTTPException(403)
        response = FileResponse(STATIC / "index.html")
        response.set_cookie("lf_admin", admin, httponly=True, samesite="strict")
        return response
    @app.post("/api/pair")
    async def pair(request: Request):
        body = await request.json()
        if body.get("invite") != invite:
            raise HTTPException(403, "Scan the current laptop QR code")
        now = time.monotonic()
        for key in list(pending):
            if now - pending[key]["created"] > 120:
                del pending[key]
        if len(pending) >= 20:
            raise HTTPException(429, "Too many pairing requests")
        token = secrets.token_urlsafe(24)
        code = str(secrets.randbelow(900000) + 100000)
        pending[token] = {"code": code, "created": now}
        response = Response(content='{"code":"' + code + '"}', media_type="application/json")
        response.set_cookie("lf_session", token, httponly=True, samesite="strict")
        return response
    @app.get("/api/pair-status")
    async def pair_status(request: Request):
        return {"paired": authorized(request)}
    @app.get("/api/status")
    async def status(request: Request):
        local = is_admin(request)
        return {"admin": local, "phones": sum(time.monotonic()-v < 10 for v in sessions.values()),
                "audio": bridge.status(), "pad": pad,
                "pending": [{"id": k, "code": v["code"]} for k,v in pending.items() if time.monotonic()-v["created"] < 120] if local else [],
                "url": app.state.public_url + "/#invite=" + invite if local else None,
                "folder": str(folder) if local else None}
    @app.post("/api/approve/{token}")
    async def approve(token: str, request: Request):
        if not is_admin(request):
            raise HTTPException(403)
        record = pending.pop(token, None)
        if not record or time.monotonic()-record["created"] > 120:
            raise HTTPException(404, "Pairing expired; scan again")
        sessions[token] = time.monotonic()
        return {"ok": True}
    @app.get("/api/qr")
    async def qr(request: Request):
        if not is_admin(request):
            raise HTTPException(403)
        image = qrcode.make(app.state.public_url + "/#invite=" + invite, image_factory=qrcode.image.svg.SvgPathImage)
        stream = io.BytesIO()
        image.save(stream)
        return Response(stream.getvalue(), media_type="image/svg+xml")
    @app.post("/api/stop")
    async def stop(request: Request):
        nonlocal invite
        if not is_admin(request):
            raise HTTPException(403)
        await app.state.tools.revoke()
        sessions.clear()
        pending.clear()
        invite = secrets.token_urlsafe(24)
        pad.update(text="", version=pad["version"]+1)
        return {"ok": True}
    @app.get("/api/files")
    async def files():
        return [{"name": p.name, "size": p.stat().st_size} for p in folder.iterdir() if p.is_file() and not p.is_symlink() and not p.name.startswith(".")]
    def safe_path(name):
        if not name or name != Path(name).name or any(c in name for c in '/\\:') or name.startswith('.') or name.endswith((' ', '.')):
            raise HTTPException(400, "Invalid filename")
        if any(ord(c) < 32 or c in '<>"|?*' for c in name) or name.split('.')[0].upper() in {'CON', 'PRN', 'AUX', 'NUL', *('COM'+str(i) for i in range(1,10)), *('LPT'+str(i) for i in range(1,10))}:
            raise HTTPException(400, "Invalid Windows filename")
        path = folder / name
        if path.is_symlink() or path.resolve().parent != folder.resolve():
            raise HTTPException(400, "Invalid path")
        return path
    @app.get("/api/files/{name}")
    async def download(name: str):
        path = safe_path(name)
        if not path.is_file():
            raise HTTPException(404)
        return FileResponse(path, filename=path.name)
    @app.delete("/api/files/{name}")
    async def remove(name: str):
        path = safe_path(name)
        if not path.is_file():
            raise HTTPException(404)
        try:
            path.unlink()
        except PermissionError:
            raise HTTPException(409, "File is in use; try again shortly")
        return {"ok": True}
    @app.put("/api/files/{name}")
    async def upload(name: str, request: Request):
        target = safe_path(name)
        temp = folder / ("." + secrets.token_hex(16) + ".part")
        size = 0
        try:
            with temp.open("xb") as out:
                async for chunk in request.stream():
                    if not authorized(request):
                        raise HTTPException(401)
                    size += len(chunk)
                    if size > 10 * 1024**3:
                        raise HTTPException(413, "Maximum file size is 10 GiB")
                    out.write(chunk)
            try:
                os.link(temp, target)
            except FileExistsError:
                raise HTTPException(409, "File already exists; rename it and retry")
        finally:
            temp.unlink(missing_ok=True)
        return {"ok": True}
    @app.post("/api/pad")
    async def update_pad(request: Request):
        body = await request.json()
        if not isinstance(body.get("text"), str) or len(body["text"]) > 100000:
            raise HTTPException(400, "Text limit is 100,000 characters")
        if body.get("version") != pad["version"]:
            raise HTTPException(409, "Pad changed on the other device. Copy your draft before reloading.")
        pad.update(text=body["text"], version=pad["version"]+1)
        return pad
    @app.post("/api/clipboard/{action}")
    async def clipboard(action: str, request: Request):
        if not is_admin(request):
            raise HTTPException(403)
        import pyperclip
        try:
            if action == "read":
                pad.update(text=pyperclip.paste()[:100000], version=pad["version"]+1)
            elif action == "write":
                pyperclip.copy(pad["text"])
            else:
                raise HTTPException(404)
        except pyperclip.PyperclipException:
            raise HTTPException(503, "Windows clipboard unavailable")
        return pad
    @app.websocket("/ws/audio")
    async def audio(ws: WebSocket):
        origin = ws.headers.get("origin")
        if not origin or urlsplit(origin).netloc != ws.headers.get("host") or not authorized(ws):
            await ws.close(code=1008)
            return
        await ws.accept()
        client, queue = bridge.add_client(asyncio.get_running_loop())
        await ws.send_json({"type":"config", "sample_rate":48000,"channels":2})
        try:
            while authorized(ws):
                try:
                    packet = await asyncio.wait_for(queue.get(), timeout=1)
                except asyncio.TimeoutError:
                    continue
                if packet.startswith(b'{"type": "error"'):
                    await ws.send_text(packet.decode())
                else:
                    await ws.send_bytes(packet)
        except Exception:
            pass
        finally:
            bridge.remove_client(client)
            with contextlib.suppress(Exception):
                await ws.close()
    install_tools(app, Path(state_dir) if state_dir else folder / ".local-first", is_admin, authorized)
    return app
