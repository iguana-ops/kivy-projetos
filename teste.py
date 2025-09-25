from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
import os

class TestApp(App):
    def build(self):
        layout = FloatLayout()
        caminho_fundo = os.path.join(os.path.dirname(__file__), "fundo2.jpg")
        img = Image(source=caminho_fundo, size_hint=(1,1), allow_stretch=True, keep_ratio=False)
        layout.add_widget(img)
        return layout

TestApp().run()
