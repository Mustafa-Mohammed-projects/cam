import os
import time
import io
from PIL import Image as PILImage

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.camera import Camera
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.graphics import Color, Rectangle, Line
from kivy.clock import Clock

class CustomCameraView(BoxLayout):
    def __init__(self, crypto_engine, storage_path, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.crypto_engine = crypto_engine
        self.storage_path = storage_path
        
        # Camera Preview
        self.camera = Camera(play=True, resolution=(1920, 1080), index=0)
        self.add_widget(self.camera)

        # Overlay Controls
        controls = BoxLayout(size_hint_y=0.15, padding=10, spacing=10)
        
        self.capture_btn = Button(
            text="CAPTURE", 
            background_color=(0.42, 0.38, 1.0, 1.0),
            bold=True
        )
        self.capture_btn.bind(on_press=self.capture_photo_memory)
        controls.add_widget(self.capture_btn)

        self.add_widget(controls)

    def capture_photo_memory(self, instance):
        """Extracts pixels directly from texture and encrypts in-memory."""
        texture = self.camera.texture
        if not texture:
            return

        # 1. Grab raw pixels directly from Kivy texture
        size = texture.size
        pixels = texture.pixels
        
        # 2. Convert to PNG buffer in RAM via PIL
        pil_image = PILImage.frombytes(mode='RGBA', size=size, data=pixels)
        pil_image = pil_image.transpose(PILImage.FLIP_TOP_BOTTOM) # Adjust Kivy coordinate orientation
        
        buffer = io.BytesIO()
        pil_image.save(buffer, format='PNG', compress_level=1)
        raw_bytes = buffer.getvalue()
        buffer.close()

        # 3. Encrypt payload
        metadata = {
            "timestamp": time.time(),
            "device": "Android Target",
            "resolution": f"{size[0]}x{size[1]}"
        }
        encrypted_spv = self.crypto_engine.encrypt_image_bytes(raw_bytes, metadata)

        # 4. Save to disk as .spv
        filename = f"IMG_{int(time.time())}.spv"
        full_path = os.path.join(self.storage_path, filename)
        self.crypto_engine.save_encrypted_file(encrypted_spv, full_path)
        
        # Visual shutter flash effect
        self._trigger_flash_animation()

    def _trigger_flash_animation(self):
        with self.canvas.foreground:
            Color(1, 1, 1, 0.7)
            rect = Rectangle(pos=self.pos, size=self.size)
        Clock.schedule_once(lambda dt: self.canvas.foreground.remove(rect), 0.1)
