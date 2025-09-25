# main.py
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition, SlideTransition
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.utils import platform
from kivy.animation import Animation
from kivy.clock import Clock
import os

from login import LoginScreen, SignupScreen, ResetPasswordScreen
from home import HomeScreen

# ----------------- SPLASH SCREEN -----------------
class SplashScreen(FloatLayout):
    def __init__(self, manager, **kwargs):
        super().__init__(**kwargs)
        self.manager = manager

        caminho_fundo = os.path.join(os.path.dirname(__file__), "fundo2.jpg")
        caminho_logo = os.path.join(os.path.dirname(__file__), "logo.png")

        # Fundo esticado
        background = Image(
            source=caminho_fundo,
            size_hint=(1, 1),
            allow_stretch=True,
            keep_ratio=False,
            opacity=0
        )
        self.add_widget(background)
        self.fundo = background  # referência para animação

        # Logo centralizado
        logo = Image(
            source=caminho_logo,
            size_hint=(None, None),
            size=(dp(200), dp(200)),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            opacity=0
        )
        self.add_widget(logo)
        self.logo = logo

        # Label
        label = Label(
            text="Academia",
            font_size=sp(24),
            color=(1,1,1,1),
            pos_hint={'center_x': 0.5, 'center_y': 0.45},
            opacity=0
        )
        self.add_widget(label)
        self.label = label

        # Fade-in sequência
        fade_in = Animation(opacity=1, duration=1.5)
        fade_in.start(self.fundo)
        Clock.schedule_once(lambda dt: fade_in.start(self.logo), 0.1)
        Clock.schedule_once(lambda dt: fade_in.start(self.label), 0.2)

        # Fade-out após 4s
        Clock.schedule_once(self.start_fade_out, 4)

    def start_fade_out(self, dt):
        fade_out = Animation(opacity=0, duration=1.0)
        fade_out.start(self.fundo)
        fade_out.start(self.logo)
        fade_out.start(self.label)
        Clock.schedule_once(self.go_to_login, 1.0)

    def go_to_login(self, dt):
        self.manager.transition = FadeTransition(duration=0.7)
        self.manager.current = 'login'
        Clock.schedule_once(lambda _: setattr(self.manager, "transition", SlideTransition()), 0.7)

# ----------------- APP PRINCIPAL -----------------
class MyApp(App):
    def build(self):
        if platform == 'android':
            Window.fullscreen = True
        else:
            Window.size = (360, 640)

        sm = ScreenManager(transition=FadeTransition(duration=0.7))

        # Splash
        splash_screen = Screen(name='splash')
        splash_screen.add_widget(SplashScreen(manager=sm))
        sm.add_widget(splash_screen)

        # Login
        login_screen = Screen(name='login')
        login_screen.add_widget(LoginScreen(manager=sm))
        sm.add_widget(login_screen)

        # Signup
        signup_screen = Screen(name='signup')
        signup_screen.add_widget(SignupScreen(manager=sm))
        sm.add_widget(signup_screen)

        # Reset password
        reset_screen = Screen(name='reset_password')
        reset_screen.add_widget(ResetPasswordScreen(manager=sm))
        sm.add_widget(reset_screen)

        # Home
        home_screen = Screen(name='home')
        home_screen.add_widget(HomeScreen(manager=sm, admin=True))
        sm.add_widget(home_screen)

        sm.current = 'splash'
        return sm

if __name__ == "__main__":
    MyApp().run()