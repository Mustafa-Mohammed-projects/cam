import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.utils import platform

from security.crypto_engine import CryptoEngine
from camera.camera_engine import CustomCameraView
from gallery.gallery_engine import GalleryView
from settings.settings_engine import SettingsView


class SecurePhotoVaultApp(App):
    def build(self):
        self.title = "SecurePhoto Vault"

        # Base Application Storage Setup
        if platform == 'android':
            from android.storage import app_storage_path
            self.storage_path = os.path.join(app_storage_path(), "vault")
        else:
            self.storage_path = os.path.join(os.getcwd(), "vault")

        os.makedirs(self.storage_path, exist_ok=True)

        # Instantiating Zero-Trust Crypto Engine
        self.crypto_engine = CryptoEngine()

        # Root UI Shell
        root = BoxLayout(orientation='vertical')

        # Screen Manager
        self.sm = ScreenManager(transition=FadeTransition(duration=0.2))

        # 1. Camera Screen
        self.cam_screen = Screen(name='camera')
        self.camera_view = CustomCameraView(self.crypto_engine, self.storage_path)
        
        # إيقاف التفعيل التلقائي للكاميرا لمنع الكراش قبل الحصول على الصلاحيات
        if platform == 'android':
            self.camera_view.camera.play = False

        self.cam_screen.add_widget(self.camera_view)
        self.sm.add_widget(self.cam_screen)

        # 2. Gallery Screen
        self.gal_screen = Screen(name='gallery')
        self.gallery_view = GalleryView(self.crypto_engine, self.storage_path)
        self.gal_screen.add_widget(self.gallery_view)
        self.sm.add_widget(self.gal_screen)

        # 3. Settings Screen
        self.settings_screen = Screen(name='settings')
        self.settings_view = SettingsView(self.crypto_engine, self.storage_path)
        self.settings_screen.add_widget(self.settings_view)
        self.sm.add_widget(self.settings_screen)

        root.add_widget(self.sm)

        # Bottom Navigation Bar
        nav_bar = BoxLayout(size_hint_y=0.08, background_color=(0.1, 0.1, 0.1, 1))

        btn_cam = Button(text="CAMERA", background_color=(0.1, 0.1, 0.1, 1))
        btn_cam.bind(on_release=lambda x: self.switch_tab('camera'))

        btn_gal = Button(text="GALLERY", background_color=(0.1, 0.1, 0.1, 1))
        btn_gal.bind(on_release=lambda x: self.switch_tab('gallery'))

        btn_set = Button(text="SETTINGS", background_color=(0.1, 0.1, 0.1, 1))
        btn_set.bind(on_release=lambda x: self.switch_tab('settings'))

        nav_bar.add_widget(btn_cam)
        nav_bar.add_widget(btn_gal)
        nav_bar.add_widget(btn_set)

        root.add_widget(nav_bar)

        # تطبيق الحماية وتطبيق طلب الصلاحيات على Android
        if platform == 'android':
            self._apply_android_security_flags()
            self._request_android_permissions()

        return root

    def _request_android_permissions(self):
        """طلب الصلاحيات ديناميكياً وتشغيل الكاميرا فقط بعد الموافقة"""
        try:
            from android.permissions import request_permissions, Permission

            def permission_callback(permissions, grants):
                if all(grants):
                    # تفعيل الكاميرا بعد السماح بالصلاحيات
                    self.camera_view.camera.play = True

            permissions = [
                Permission.CAMERA,
                Permission.READ_MEDIA_IMAGES
            ]
            request_permissions(permissions, permission_callback)
        except Exception as e:
            print(f"Permission Request Error: {e}")

    def _apply_android_security_flags(self):
        """تطبيق حماية الشاشة (منع Lqtat/تسجيل الشاشة) عبر UI Thread"""
        try:
            from android.runnable import run_on_ui_thread
            from jnius import autoclass

            @run_on_ui_thread
            def set_flags():
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                WindowManager = autoclass('android.view.WindowManager$LayoutParams')
                activity = PythonActivity.mActivity
                activity.getWindow().addFlags(WindowManager.FLAG_SECURE)

            set_flags()
        except Exception as e:
            print(f"Failed to set FLAG_SECURE: {e}")

    def switch_tab(self, tab_name: str):
        if tab_name == 'gallery':
            self.gallery_view.refresh_gallery()
        elif tab_name == 'settings':
            self.settings_view.update_stats()
        self.sm.current = tab_name


if __name__ == '__main__':
    SecurePhotoVaultApp().run()
