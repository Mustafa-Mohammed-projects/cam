import os
import io
from PIL import Image as PILImage, ImageEnhance, ImageFilter

from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image as KivyImage
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.core.image import Image as CoreImage

class GalleryView(BoxLayout):
    def __init__(self, crypto_engine, storage_path, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.crypto_engine = crypto_engine
        self.storage_path = storage_path

        # Grid view container
        self.scroll = ScrollView()
        self.grid = GridLayout(cols=3, spacing=5, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)
        
        self.add_widget(self.scroll)

    def refresh_gallery(self):
        """Scans folder and generates decrypted thumbnails in memory."""
        self.grid.clear_widgets()
        if not os.path.exists(self.storage_path):
            return

        for fname in sorted(os.listdir(self.storage_path), reverse=True):
            if fname.endswith('.spv'):
                full_path = os.path.join(self.storage_path, fname)
                thumb_widget = self._create_thumbnail_widget(full_path)
                if thumb_widget:
                    self.grid.add_widget(thumb_widget)

    def _create_thumbnail_widget(self, spv_path: str):
        try:
            # Decrypt in memory
            raw_bytes, _ = self.crypto_engine.read_encrypted_file(spv_path)
            
            # Downscale for thumbnail in RAM
            buf = io.BytesIO(raw_bytes)
            pil_img = PILImage.open(buf)
            pil_img.thumbnail((250, 250))
            
            out_buf = io.BytesIO()
            pil_img.save(out_buf, format='PNG')
            out_buf.seek(0)

            # Load directly into Kivy CoreImage Texture
            core_img = CoreImage(out_buf, ext='png')
            btn = Button(size_hint_y=None, height=250)
            img_widget = KivyImage(texture=core_img.texture, allow_stretch=True, keep_ratio=True)
            btn.add_widget(img_widget)
            img_widget.size = btn.size
            img_widget.pos = btn.pos

            btn.bind(on_release=lambda x: self.open_full_viewer(spv_path))
            return btn
        except Exception as e:
            print(f"Error loading thumbnail: {e}")
            return None

    def open_full_viewer(self, spv_path: str):
        """Opens decrypted image viewer modal with real-time memory filters."""
        raw_bytes, metadata = self.crypto_engine.read_encrypted_file(spv_path)
        
        buf = io.BytesIO(raw_bytes)
        core_img = CoreImage(buf, ext='png')

        content = BoxLayout(orientation='vertical')
        viewer_img = KivyImage(texture=core_img.texture, allow_stretch=True)
        content.add_widget(viewer_img)

        # Filters Bar
        filter_bar = BoxLayout(size_hint_y=0.15, spacing=5)
        
        btn_bw = Button(text="B&W")
        btn_bw.bind(on_release=lambda x: self._apply_filter(spv_path, viewer_img, "BW"))
        
        btn_sepia = Button(text="Sepia")
        btn_sepia.bind(on_release=lambda x: self._apply_filter(spv_path, viewer_img, "SEPIA"))

        filter_bar.add_widget(btn_bw)
        filter_bar.add_widget(btn_sepia)
        content.add_widget(filter_bar)

        popup = Popup(title=os.path.basename(spv_path), content=content, size_hint=(0.95, 0.95))
        popup.open()

    def _apply_filter(self, spv_path: str, img_widget: KivyImage, filter_type: str):
        """Applies filter in RAM and updates view without writing raw data to disk."""
        raw_bytes, _ = self.crypto_engine.read_encrypted_file(spv_path)
        pil_img = PILImage.open(io.BytesIO(raw_bytes))

        if filter_type == "BW":
            pil_img = pil_img.convert("L")
        elif filter_type == "SEPIA":
            # Grayscale to sepia tint matrix transformation
            pil_img = pil_img.convert("L").convert("RGB")
            r, g, b = pil_img.split()
            r = r.point(lambda i: i * 0.9)
            g = g.point(lambda i: i * 0.7)
            b = b.point(lambda i: i * 0.4)
            pil_img = PILImage.merge("RGB", (r, g, b))

        out_buf = io.BytesIO()
        pil_img.save(out_buf, format='PNG')
        out_buf.seek(0)
        
        core_img = CoreImage(out_buf, ext='png')
        img_widget.texture = core_img.texture
