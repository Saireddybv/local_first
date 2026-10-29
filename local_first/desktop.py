"""Small Windows adapter. Importing this module never controls the desktop."""
import ctypes
import io
import os
from ctypes import wintypes


class Desktop:
    def _user32(self):
        if os.name != "nt":
            raise RuntimeError("This control requires an unlocked Windows desktop")
        return ctypes.WinDLL("user32", use_last_error=True)

    def _send(self, kind, **values):
        # ULONG_PTR must have pointer width, including on 64-bit Windows.
        class Mouse(ctypes.Structure):
            _fields_ = [("dx", wintypes.LONG), ("dy", wintypes.LONG),
                        ("mouseData", wintypes.DWORD), ("dwFlags", wintypes.DWORD),
                        ("time", wintypes.DWORD), ("dwExtraInfo", ctypes.c_size_t)]
        class Keyboard(ctypes.Structure):
            _fields_ = [("wVk", wintypes.WORD), ("wScan", wintypes.WORD),
                        ("dwFlags", wintypes.DWORD), ("time", wintypes.DWORD),
                        ("dwExtraInfo", ctypes.c_size_t)]
        class Payload(ctypes.Union):
            _fields_ = [("mi", Mouse), ("ki", Keyboard)]
        class Input(ctypes.Structure):
            _fields_ = [("type", wintypes.DWORD), ("payload", Payload)]
        item = Input(type=kind)
        setattr(item.payload, "mi" if kind == 0 else "ki",
                (Mouse if kind == 0 else Keyboard)(**values))
        api = self._user32()
        api.SendInput.argtypes = [wintypes.UINT, ctypes.POINTER(Input), ctypes.c_int]
        api.SendInput.restype = wintypes.UINT
        if api.SendInput(1, ctypes.byref(item), ctypes.sizeof(Input)) != 1:
            raise RuntimeError("Windows blocked input. Unlock the desktop and focus a non-administrator app.")

    def key(self, code):
        self._send(1, wVk=code)
        self._send(1, wVk=code, dwFlags=2)

    def text(self, value):
        raw = value.encode("utf-16-le")
        for index in range(0, len(raw), 2):
            code = int.from_bytes(raw[index:index + 2], "little")
            self._send(1, wScan=code, dwFlags=4)
            self._send(1, wScan=code, dwFlags=6)

    def pointer(self, action, dx=0, dy=0):
        if action == "move":
            self._send(0, dx=dx, dy=dy, dwFlags=1)
        elif action == "scroll":
            self._send(0, mouseData=(dy * 120) & 0xffffffff, dwFlags=0x0800)
        else:
            down, up = (2, 4) if action == "left" else (8, 16)
            self._send(0, dwFlags=down)
            self._send(0, dwFlags=up)

    def lock(self):
        if not self._user32().LockWorkStation():
            raise RuntimeError("Windows could not lock this session")

    def screenshot(self, preview=False):
        from PIL import ImageGrab
        image = ImageGrab.grab(all_screens=True)
        if preview:
            image.thumbnail((1440, 900))
        output = io.BytesIO()
        image.convert("RGB").save(output, format="JPEG" if preview else "PNG")
        return output.getvalue()
