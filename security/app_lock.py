# security/app_lock.py
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from ui.theme import Theme

class AppLockScreen(BoxLayout):
    def __init__(self, on_success_callback, correct_pin="1234", **kwargs):
        super().__init__(orientation='vertical', padding=40, spacing=20, **kwargs)
        self.on_success = on_success_callback
        self.correct_pin = correct_pin

        self.add_widget(Label(text="Enter Master PIN", font_size='22sp', bold=True, color=Theme.TEXT_PRIMARY))

        self.pin_input = TextInput(
            password=True, 
            multiline=False, 
            numeric=True, 
            halign='center',
            font_size='24sp',
            size_hint_y=0.2
        )
        self.add_widget(self.pin_input)

        btn_unlock = Button(text="UNLOCK", background_color=Theme.ACCENT, bold=True, size_hint_y=0.2)
        btn_unlock.bind(on_release=self.check_pin)
        self.add_widget(btn_unlock)

        self.status_label = Label(text="", color=Theme.ERROR)
        self.add_widget(self.status_label)

    def check_pin(self, instance):
        if self.pin_input.text == self.correct_pin:
            self.on_success()
        else:
            self.status_label.text = "Incorrect PIN. Access Denied."
            self.pin_input.text = ""
