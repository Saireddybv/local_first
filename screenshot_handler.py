"""
Screenshot capture and image handling
"""

import os
import base64
from typing import Optional, Dict
from datetime import datetime
import threading
from queue import Queue

try:
    from PIL import ImageGrab
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False


class ScreenshotHandler:
    """Handles screenshot capture"""
    
    def __init__(self):
        self.last_screenshot: Optional[Dict] = None
        self.screenshot_callback = None
        
        # Check dependencies
        self._check_dependencies()
        
    def _check_dependencies(self):
        """Check if required libraries are available"""
        if not PILLOW_AVAILABLE:
            print("⚠️  Pillow not installed. Screenshots will be unavailable.")
            print("   Install with: pip install pillow")
            
    def set_screenshot_callback(self, callback):
        """Set callback for when screenshot is ready"""
        self.screenshot_callback = callback
        
    def capture_screenshot(self) -> Optional[Dict]:
        """Capture a screenshot"""
        if not PILLOW_AVAILABLE:
            return {"error": "Pillow is not installed", "success": False}
            
        try:
            # Capture screenshot
            screenshot = ImageGrab.grab()
            
            # Convert to base64 for transmission
            import io
            img_byte_arr = io.BytesIO()
            screenshot.save(img_byte_arr, format='PNG')
            img_base64 = base64.b64encode(img_byte_arr.getvalue()).decode()
            
            result = {
                "success": True,
                "timestamp": datetime.now().isoformat(),
                "image_base64": img_base64,
                "resolution": screenshot.size
            }
            
            self.last_screenshot = result
            
            # Call callback if set
            if self.screenshot_callback:
                self.screenshot_callback(result)
                
            return result
            
        except Exception as e:
            error_msg = f"Screenshot capture failed: {str(e)}"
            print(f"❌ {error_msg}")
            return {"error": error_msg, "success": False}
            
    def get_last_screenshot_image(self) -> Optional[str]:
        """Get base64 encoded image from last screenshot"""
        if self.last_screenshot and self.last_screenshot.get("image_base64"):
            return self.last_screenshot["image_base64"]
        return None


# Global instance
screenshot_handler = ScreenshotHandler()
