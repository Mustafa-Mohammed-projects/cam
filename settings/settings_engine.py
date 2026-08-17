# settings/settings_engine.py
import os
import zipfile
import io
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.switch import Switch
from kivy.uix.popup import Popup
from ui.theme import Theme

class SettingsView(BoxLayout):
    def __init__(self, crypto_engine, storage_path, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=15, **kwargs)
        self.crypto_engine = crypto_engine
        self.storage_path = storage_path

        # Title
        self.add_widget(Label(
            text="Secure Vault Settings", 
            font_size='20sp', 
            bold=True, 
            color=Theme.TEXT_PRIMARY,
            size_hint_y=0.1
        ))

        # Storage Stats
        self.stats_label = Label(text="Calculating storage...", size_hint_y=0.1, color=Theme.TEXT_SECONDARY)
        self.add_widget(self.stats_label)

        # Export encrypted images to ZIP
        btn_export = Button(
            text="Export All (.spv) to ZIP", 
            background_color=Theme.ACCENT, 
            size_hint_y=0.12,
            bold=True
        )
        btn_export.bind(on_release=self.export_to_zip)
        self.add_widget(btn_export)

        # Clear Vault (Self-Destruct Data)
        btn_wipe = Button(
            text="Wipe All Vault Data", 
            background_color=Theme.ERROR, 
            size_hint_y=0.12,
            bold=True
        )
        btn_wipe.bind(on_release=self.wipe_vault)
        self.add_widget(btn_wipe)

        self.add_widget(BoxLayout(size_hint_y=0.56)) # Spacer
        self.update_stats()

    def update_stats(self):
        if not os.path.exists(self.storage_path):
            return
        files = [f for f in os.listdir(self.storage_path) if f.endswith('.spv')]
        total_size = sum(os.path.getsize(os.path.join(self.storage_path, f)) for f in files)
        size_mb = total_size / (1024 * 1024)
        self.stats_label.text = f"Encrypted Photos: {len(files)} | Size: {size_mb:.2f} MB"

    def export_to_zip(self, instance):
        zip_path = os.path.join(self.storage_path, "Vault_Backup.zip")
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for root, _, files in os.walk(self.storage_path):
                for file in files:
                    if file.endswith('.spv'):
                        zipf.write(os.path.join(root, file), arcname=file)
        
        popup = Popup(
            title="Backup Complete", 
            content=Label(text=f"Exported to:\n{zip_path}"),
            size_hint=(0.8, 0.4)
        )
        popup.open()

    def wipe_vault(self, instance):
        for f in os.listdir(self.storage_path):
            file_p = os.path.join(self.storage_path, f)
            if os.path.isfile(file_p):
                os.remove(file_p)
        self.update_stats()
