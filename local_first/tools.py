"""Additional local tools, all behind the shared pairing gate."""
import asyncio
import contextlib
import json
import os
import time
from typing import Literal
from urllib.parse import urlsplit

import psutil
from fastapi import HTTPException, Request, WebSocket
from fastapi.responses import Response
from pydantic import BaseModel, Field

from .actions import Actions
from .desktop import Desktop
from .storage import Notes


class Permissions(BaseModel):
    control: bool = False
    screen: bool = False
    actions: bool = False
    camera: bool = False


class KeyCommand(BaseModel):
    key: Literal["play", "next", "previous", "mute", "volume-up", "volume-down",
                 "slide-next", "slide-previous", "slide-start", "slide-end", "slide-black",
                 "enter", "backspace", "tab", "escape", "left", "right", "up", "down"]


class PointerCommand(BaseModel):
    action: Literal["move", "left", "right", "scroll"]
    dx: int = Field(default=0, ge=-500, le=500)
    dy: int = Field(default=0, ge=-500, le=500)


class TextCommand(BaseModel):
    text: str = Field(max_length=2000)


class NoteCommand(BaseModel):
    id: str | None = None
    title: str = Field(min_length=1, max_length=120)
    text: str = Field(max_length=100000)
    version: int = Field(default=0, ge=0)


class ActionCommand(BaseModel):
    label: str = Field(min_length=1, max_length=80)
    argv: list[str] = Field(min_length=1, max_length=30)


KEYS = {"play": 0xB3, "next": 0xB0, "previous": 0xB1, "mute": 0xAD,
        "volume-up": 0xAF, "volume-down": 0xAE, "slide-next": 0x22,
        "slide-previous": 0x21, "slide-start": 0x74, "slide-end": 0x1B,
        "slide-black": 0x42, "enter": 0x0D, "backspace": 0x08,
        "tab": 0x09, "escape": 0x1B, "left": 0x25, "right": 0x27,
        "up": 0x26, "down": 0x28}


class ToolState:
    def __init__(self, state_dir):
        state_dir.mkdir(parents=True, exist_ok=True)
        self.permissions = Permissions()
        self.desktop = Desktop()
        self.notes = Notes(state_dir / "notes.sqlite3")
        self.actions = Actions(state_dir)
        self.peers = {}
        self.screen_lock = asyncio.Lock()
        self.last_preview = (0, b"")

    async def revoke(self):
        self.permissions = Permissions()
        self.last_preview = (0, b"")
        for ws in list(self.peers.values()):
            with contextlib.suppress(Exception):
                await ws.close(code=1000)
        self.peers.clear()
        await asyncio.to_thread(self.actions.stop_all)


def install_tools(app, state_dir, is_admin, authorized):
    state = ToolState(state_dir)
    app.state.tools = state

    def admin_only(request):
        if not is_admin(request):
            raise HTTPException(403, "Use the laptop controller for this setting")

    def require(capability):
        if not getattr(state.permissions, capability):
            raise HTTPException(403, f"Enable {capability} on the laptop first")

    async def desktop_call(method, *args):
        try:
            return await asyncio.to_thread(getattr(state.desktop, method), *args)
        except (RuntimeError, OSError) as exc:
            raise HTTPException(503, str(exc)) from exc

    @app.get("/api/tools")
    async def tools_status(request: Request):
        return {"permissions": state.permissions.model_dump(), "windows": os.name == "nt",
                "camera_peers": list(state.peers), "admin": is_admin(request)}

    @app.post("/api/permissions")
    async def permissions(body: Permissions, request: Request):
        admin_only(request)
        previous = state.permissions
        state.permissions = body
        if previous.screen and not body.screen:
            state.last_preview = (0, b"")
        if previous.actions and not body.actions:
            await asyncio.to_thread(state.actions.stop_all)
        if previous.camera and not body.camera:
            for ws in list(state.peers.values()):
                with contextlib.suppress(Exception):
                    await ws.close(code=1000)
            state.peers.clear()
        return body

    @app.post("/api/control/key")
    async def key(body: KeyCommand):
        require("control")
        await desktop_call("key", KEYS[body.key])
        return {"ok": True}

    @app.post("/api/control/text")
    async def text(body: TextCommand):
        require("control")
        await desktop_call("text", body.text)
        return {"ok": True}

    @app.post("/api/control/pointer")
    async def pointer(body: PointerCommand):
        require("control")
        await desktop_call("pointer", body.action, body.dx, body.dy)
        return {"ok": True}

    @app.post("/api/control/lock")
    async def lock():
        require("actions")
        await desktop_call("lock")
        return {"ok": True}

    @app.get("/api/screen")
    async def screen(request: Request, preview: bool = False):
        require("screen")
        async with state.screen_lock:
            # Multiple viewers share a bounded preview capture rate.
            if preview and time.monotonic() - state.last_preview[0] < .45:
                image = state.last_preview[1]
            else:
                image = await desktop_call("screenshot", preview)
                if preview:
                    state.last_preview = (time.monotonic(), image)
            require("screen")
            if not authorized(request):
                raise HTTPException(401)
        headers = {} if preview else {"Content-Disposition": 'attachment; filename="local-first-screenshot.png"'}
        return Response(image, media_type="image/jpeg" if preview else "image/png", headers=headers)

    @app.get("/api/notes")
    async def notes():
        return state.notes.list()

    @app.post("/api/notes")
    async def save_note(body: NoteCommand):
        try:
            return state.notes.save(body.id, body.title, body.text, body.version)
        except ValueError as exc:
            raise HTTPException(409, str(exc)) from exc

    @app.delete("/api/notes/{note_id}")
    async def delete_note(note_id: str, version: int):
        try:
            state.notes.delete(note_id, version)
        except ValueError as exc:
            raise HTTPException(409, str(exc)) from exc
        return {"ok": True}

    @app.get("/api/system")
    async def system():
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage(str(app.state.folder))
        battery = psutil.sensors_battery()
        return {"cpu": psutil.cpu_percent(), "memory": memory.percent,
                "disk_free": disk.free, "disk_total": disk.total,
                "uptime": max(0, time.time() - psutil.boot_time()),
                "battery": None if battery is None else {"percent": battery.percent, "plugged": battery.power_plugged}}

    @app.get("/api/actions")
    async def actions(request: Request):
        # Task output can contain personal data, so it follows the actions switch.
        if not is_admin(request):
            require("actions")
        return state.actions.snapshot(is_admin(request))

    @app.post("/api/actions")
    async def add_action(body: ActionCommand, request: Request):
        admin_only(request)
        if any(len(arg) > 4096 or "\x00" in arg for arg in body.argv):
            raise HTTPException(400, "Invalid argument")
        try:
            return state.actions.save(body.label, body.argv)
        except (ValueError, OSError) as exc:
            raise HTTPException(400, str(exc)) from exc

    @app.delete("/api/actions/{action_id}")
    async def remove_action(action_id: str, request: Request):
        admin_only(request)
        try:
            state.actions.remove(action_id)
        except KeyError:
            raise HTTPException(404, "Action not found")
        return {"ok": True}

    @app.post("/api/actions/{action_id}/run")
    async def run_action(action_id: str):
        require("actions")
        try:
            return state.actions.start(action_id)
        except KeyError:
            raise HTTPException(404, "Action not found")
        except (ValueError, OSError) as exc:
            raise HTTPException(400, str(exc)) from exc

    @app.post("/api/tasks/{run_id}/stop")
    async def stop_task(run_id: str):
        require("actions")
        await asyncio.to_thread(state.actions.stop, run_id)
        return {"ok": True}

    @app.websocket("/ws/camera/{role}")
    async def camera(ws: WebSocket, role: str):
        origin = ws.headers.get("origin")
        if (role not in {"send", "receive"} or not origin
                or urlsplit(origin).netloc != ws.headers.get("host")
                or not authorized(ws) or not state.permissions.camera
                or (role == "receive" and not is_admin(ws))):
            await ws.close(code=1008)
            return
        if role in state.peers:
            await ws.close(code=1008, reason="This camera role is already in use")
            return
        await ws.accept()
        state.peers[role] = ws
        other_role = "receive" if role == "send" else "send"
        try:
            await ws.send_json({"type": "waiting"})
            if other_role in state.peers:
                for peer in list(state.peers.values()):
                    await peer.send_json({"type": "ready"})
            while authorized(ws) and state.permissions.camera:
                try:
                    raw = await asyncio.wait_for(ws.receive_text(), timeout=1)
                except asyncio.TimeoutError:
                    continue
                if len(raw) > 64000:
                    break
                message = json.loads(raw)
                allowed = {"candidate", "offer" if role == "send" else "answer"}
                if not isinstance(message, dict) or message.get("type") not in allowed:
                    break
                other = state.peers.get(other_role)
                if other:
                    await other.send_json(message)
        except (Exception, asyncio.CancelledError):
            pass
        finally:
            if state.peers.get(role) is ws:
                del state.peers[role]
                other = state.peers.get(other_role)
                if other:
                    with contextlib.suppress(Exception):
                        await other.send_json({"type": "left"})
            with contextlib.suppress(Exception):
                await ws.close()

    return state
