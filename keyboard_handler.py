"""
Keyboard event handling and monitoring
"""

from pynput import keyboard
import threading
from typing import Callable, Optional

class KeyboardHandler:
    """Handles global keyboard events and hotkeys"""
    
    def __init__(self):
        self.listener: Optional[keyboard.Listener] = None
        self.listening = False
        self.keystroke_callback: Optional[Callable] = None
        self.hotkey_callbacks = {}
        
    def set_keystroke_callback(self, callback: Callable):
        """Set callback for regular keystrokes"""
        self.keystroke_callback = callback
        
    def register_hotkey(self, hotkey_name: str, callback: Callable):
        """Register a callback for a specific hotkey"""
        self.hotkey_callbacks[hotkey_name] = callback
        
    def start_listening(self):
        """Start listening to keyboard events"""
        if not self.listening:
            self.listening = True
            try:
                self.listener = keyboard.Listener(on_press=self._on_press)
                self.listener.start()
                print("✅ Keyboard listener started")
            except Exception as e:
                print(f"❌ Failed to start keyboard listener: {e}")
                self.listening = False
                
    def stop_listening(self):
        """Stop listening to keyboard events"""
        if self.listening and self.listener:
            self.listening = False
            self.listener.stop()
            print("✅ Keyboard listener stopped")
            
    def _on_press(self, key):
        """Handle key press events"""
        try:
            # Check for hotkeys
            self._check_hotkeys(key)
            
            # Call keystroke callback
            if self.keystroke_callback and self.listening:
                char = self._key_to_char(key)
                if char:
                    self.keystroke_callback(char)
        except Exception as e:
            print(f"Error capturing key: {e}")
            
    def _check_hotkeys(self, key):
        """Check if a hotkey combination is pressed"""
        # This is a simplified version - for production, use pynput's hotkey support
        # For now, we'll handle the screenshot hotkey separately
        pass
        
    def _key_to_char(self, key) -> str:
        """Convert key to character"""
        try:
            if hasattr(key, 'char') and key.char:
                return key.char
            else:
                special_keys = {
                    'space': ' ',
                    'enter': '\n',
                    'tab': '\t',
                    'backspace': '\b',
                }
                key_name = str(key).replace("Key.", "").lower()
                return special_keys.get(key_name, '')
        except:
            return ''


# Global instance
keyboard_handler = KeyboardHandler()
