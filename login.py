# login.py
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.metrics import dp, sp
from kivy.core.window import Window
from kivy.utils import platform
from kivy.graphics import Color, RoundedRectangle
from kivy.clock import Clock
from google_auth_oauthlib.flow import InstalledAppFlow
import requests
import os

from home import HomeScreen

# ----------------- CONFIGURAÇÃO FIREBASE -----------------
FIREBASE_API_KEY = "AIzaSyA61W177WJPmWkbryipsPteCbeS0FWOwDQ"
FIREBASE_DB_URL = "https://maisquefitnessapp-5eac0-default-rtdb.firebaseio.com"

def firebase_login(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    return requests.post(url, json=payload)

def firebase_signup(nome, email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        user_id = response.json()['localId']
        data = {"nome": nome, "email": email}
        requests.put(f"{FIREBASE_DB_URL}/usuarios/{user_id}.json", json=data)
    return response

def firebase_reset_password(email):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={FIREBASE_API_KEY}"
    payload = {"requestType": "PASSWORD_RESET", "email": email}
    return requests.post(url, json=payload)

# ----------------- CLASSE LINK CLICÁVEL -----------------
class LinkLabel(ButtonBehavior, Label):
    pass

# ----------------- BOTÃO PERSONALIZADO -----------------
class RoundedButton(ButtonBehavior, BoxLayout):
    def __init__(self, text="", bg_color=(0,0,0,1), text_color=(1,1,1,1), logo=None,
                 stroke_color=None, stroke_width=1, on_press=None,
                 logo_offset_x=0, label_offset_x=0, **kwargs):
        super().__init__(orientation='horizontal', spacing=dp(10), padding=[dp(10), dp(5)], **kwargs)
        self.size_hint_y = None
        self.height = dp(50)
        self.radius = [20]
        self.bg_color = bg_color
        self.stroke_color = stroke_color
        self.stroke_width = stroke_width if stroke_width else 1

        with self.canvas.before:
            if stroke_color:
                Color(*stroke_color)
                self.rect_border = RoundedRectangle(radius=self.radius,
                                                   pos=(self.x, self.y),
                                                   size=(self.width, self.height))
            Color(*bg_color)
            self.rect = RoundedRectangle(radius=self.radius, pos=self.pos, size=self.size)

        self.bind(pos=self.update_rect, size=self.update_rect)

        # LOGO
        if logo:
            logo_container = BoxLayout(size_hint=(None, 1), width=dp(50))
            logo_anchor = AnchorLayout(
                anchor_x='left',
                anchor_y='center',
                padding=[logo_offset_x, 0, 0, 0]
            )
            logo_img = Image(source=logo, size_hint=(None, None), size=(dp(30), dp(30)))
            logo_anchor.add_widget(logo_img)
            logo_container.add_widget(logo_anchor)
            self.add_widget(logo_container)

        # LABEL
        label_container = BoxLayout(size_hint_x=1, padding=[label_offset_x, 0, 0, 0])
        label_anchor = AnchorLayout(anchor_x='center', anchor_y='center')
        self.label = Label(text=text, color=text_color, halign='center', valign='middle', font_size=sp(16))
        self.label.bind(size=self.label.setter('text_size'))
        label_anchor.add_widget(self.label)
        label_container.add_widget(label_anchor)
        self.add_widget(label_container)

        if on_press:
            self.bind(on_press=on_press)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        if hasattr(self, 'rect_border'):
            self.rect_border.pos = (self.x - self.stroke_width, self.y - self.stroke_width)
            self.rect_border.size = (self.width + 2*self.stroke_width, self.height + 2*self.stroke_width)

# ----------------- TELA DE LOGIN -----------------
class LoginScreen(FloatLayout):
    def __init__(self, manager, **kwargs):
        super().__init__(**kwargs)
        self.manager = manager
        self.sm_ref = manager  # referência ao ScreenManager

        if platform == 'android':
            Window.fullscreen = True
        else:
            Window.size = (360, 640)

        caminho_fundo = os.path.join(os.path.dirname(__file__), "fundo2.jpg")
        caminho_logo = os.path.join(os.path.dirname(__file__), "logo.png")

        background = Image(source=caminho_fundo, allow_stretch=True, keep_ratio=False)
        self.add_widget(background)

        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False, bar_width=0)
        container = BoxLayout(orientation="vertical", spacing=dp(15), padding=dp(20), size_hint_y=None)
        container.bind(minimum_height=container.setter("height"))

        # Logo e título
        top_area = BoxLayout(orientation="vertical", spacing=dp(55), padding=[0, dp(120), 0, 0], size_hint_y=None)
        top_area.bind(minimum_height=top_area.setter("height"))
        logo = Image(source=caminho_logo, size_hint=(None, None), size=(dp(250), dp(250)))
        logo_area = AnchorLayout(anchor_x="center", anchor_y="center", padding=[0, 0, 0, dp(30)])
        logo_area.add_widget(logo)
        top_area.add_widget(logo_area)

        title = Label(text="SUA EVOLUÇÃO\nCOMEÇA AQUI!", font_size=sp(20), halign="center",
                      valign="middle", color=(1,1,1,1), size_hint_y=None)
        title.bind(size=title.setter("text_size"))
        title.bind(texture_size=title.setter("size"))
        top_area.add_widget(title)

        subtitle = Label(text="Use o mesmo e-mail de cadastro da academia", font_size=sp(14),
                         halign="center", valign="middle", color=(0.9,0.9,0.9,1), size_hint_y=None)
        subtitle.bind(size=subtitle.setter("text_size"))
        subtitle.bind(texture_size=subtitle.setter("size"))
        top_area.add_widget(subtitle)
        container.add_widget(top_area)

        # Campos
        self.email = TextInput(hint_text="E-mail", multiline=False, size_hint_y=None,
                               height=dp(50), background_color=(0,0,0,0.6), foreground_color=(1,1,1,1),
                               padding_y=(dp(15),dp(15)),cursor_color=(1,1,0,1), font_size=sp(16))
        container.add_widget(self.email)

        self.senha = TextInput(hint_text="Senha", multiline=False, password=True,
                               size_hint_y=None, height=dp(50), background_color=(0,0,0,0.6),
                               foreground_color=(1,1,1,1), padding_y=(dp(15),dp(15)),cursor_color=(1,1,0,1), font_size=sp(16))
        container.add_widget(self.senha)

        self.feedback = Label(text="", size_hint=(1,None), color=(1,0,0,1))
        container.add_widget(self.feedback)

        # Botões
        btn_entrar = RoundedButton(
            text="Entrar",
            bg_color=(0.9,0.8,0,1),
            text_color=(0,0,0,1),
            on_press=self.login
        )
        container.add_widget(btn_entrar)

        btn_google = RoundedButton(
            text="Entrar com Google",
            bg_color=(0,0,0,1),
            text_color=(1,1,1,1),
            logo="googlelogo.png",
            stroke_color=(1,1,1,1),
            stroke_width=1,
            on_press=self.login_google,
            logo_offset_x=200,
            label_offset_x=-40
        )
        container.add_widget(btn_google)

        # Links
        link_criar = LinkLabel(text="[u][color=00ADEF]Criar Conta[/color][/u]", markup=True,
                               font_size=sp(14), halign="center", size_hint_y=None)
        link_criar.bind(size=link_criar.setter("text_size"))
        link_criar.bind(texture_size=link_criar.setter("size"))
        link_criar.bind(on_press=self.abrir_signup)
        container.add_widget(link_criar)

        link_reset = LinkLabel(text="[u][color=00ADEF]Esqueci a senha[/color][/u]", markup=True,
                               font_size=sp(14), halign="center", size_hint_y=None)
        link_reset.bind(size=link_reset.setter("text_size"))
        link_reset.bind(texture_size=link_reset.setter("size"))
        link_reset.bind(on_press=self.abrir_reset_senha)
        container.add_widget(link_reset)

        scroll.add_widget(container)
        self.add_widget(scroll)

    def login(self, instance):
        email = self.email.text.strip()
        senha = self.senha.text.strip()
        if not email or not senha:
            self.feedback.color = (1,0,0,1)
            self.feedback.text = "Preencha todos os campos!"
            return
        res = firebase_login(email, senha)
        if res.status_code == 200:
            self.feedback.color = (0,1,0,1)
            self.feedback.text = "Login realizado com sucesso!"
            Clock.schedule_once(self.entrar_home, 2)
        else:
            erro = res.json().get("error", {}).get("message", "")
            if "INVALID_EMAIL" in erro:
                self.feedback.text = "E-mail inválido!"
            elif "EMAIL_NOT_FOUND" in erro:
                self.feedback.text = "E-mail não cadastrado!"
            elif "INVALID_PASSWORD" in erro:
                self.feedback.text = "Senha incorreta!"
            else:
                self.feedback.text = "Usuário ou senha inválidos"
            self.feedback.color = (1,0,0,1)

    def login_google(self, instance):
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                "client_secret.json",
                scopes=["email", "profile", "openid"]
            )
            creds = flow.run_local_server(port=0)
            id_token = creds.id_token

            url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithIdp?key={FIREBASE_API_KEY}"
            payload = {
                "postBody": f"id_token={id_token}&providerId=google.com",
                "requestUri": "http://localhost",
                "returnIdpCredential": True,
                "returnSecureToken": True
            }
            res = requests.post(url, json=payload)
            if res.status_code == 200:
                user_data = res.json()
                self.feedback.color = (0,1,0,1)
                self.feedback.text = f"Login Google realizado! Bem-vindo(a) {user_data.get('displayName','')}"
                user_id = user_data['localId']
                email = user_data['email']
                nome = user_data.get('displayName','Usuário')
                requests.put(f"{FIREBASE_DB_URL}/usuarios/{user_id}.json", json={"nome": nome, "email": email})
                Clock.schedule_once(self.entrar_home, 2)
            else:
                self.feedback.color = (1,0,0,1)
                self.feedback.text = "Erro no login Google"
        except Exception as e:
            self.feedback.color = (1,0,0,1)
            self.feedback.text = f"Erro: {str(e)}"

    def entrar_home(self, dt):
        if not any(screen.name == 'home' for screen in self.sm_ref.screens):
            home_screen = Screen(name='home')
            home_screen.add_widget(HomeScreen(manager=self.sm_ref))
            self.sm_ref.add_widget(home_screen)
        self.sm_ref.transition.direction = 'left'
        self.sm_ref.current = 'home'

    def abrir_signup(self, instance):
        self.sm_ref.transition.direction = "left"
        self.sm_ref.current = 'signup'

    def abrir_reset_senha(self, instance):
        self.sm_ref.transition.direction = "left"
        self.sm_ref.current = 'reset_password'

# ----------------- TELA DE CADASTRO -----------------
class SignupScreen(FloatLayout):
    def __init__(self, manager, **kwargs):
        super().__init__(**kwargs)
        self.manager = manager
        self._touch_start_x = 0

        if platform == 'android':
            Window.fullscreen = True
        else:
            Window.size = (360, 640)

        caminho_fundo = os.path.join(os.path.dirname(__file__), "fundo2.jpg")
        background = Image(source=caminho_fundo, allow_stretch=True, keep_ratio=False)
        self.add_widget(background)

        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False, bar_width=0)
        container = BoxLayout(orientation="vertical", spacing=dp(15), padding=dp(20), size_hint_y=None)
        container.bind(minimum_height=container.setter("height"))

        self.nome = TextInput(hint_text="Digite seu nome", multiline=False, size_hint_y=None,
                              height=dp(50), background_color=(0,0,0,0.6), foreground_color=(1,1,1,1),
                              padding_y=(dp(15),dp(15)),cursor_color=(1,1,0,1), font_size=sp(16))
        container.add_widget(self.nome)

        self.email = TextInput(hint_text="Digite seu e-mail", multiline=False, size_hint_y=None,
                               height=dp(50), background_color=(0,0,0,0.6), foreground_color=(1,1,1,1),
                               padding_y=(dp(15),dp(15)),cursor_color=(1,1,0,1), font_size=sp(16))
        container.add_widget(self.email)

        self.senha = TextInput(hint_text="Digite sua senha", multiline=False, password=True,
                               size_hint_y=None, height=dp(50), background_color=(0,0,0,0.6),
                               foreground_color=(1,1,1,1), padding_y=(dp(15),dp(15)),cursor_color=(1,1,0,1), font_size=sp(16))
        container.add_widget(self.senha)

        self.senha2 = TextInput(hint_text="Confirme sua senha", multiline=False, password=True,
                                size_hint_y=None, height=dp(50), background_color=(0,0,0,0.6),
                                foreground_color=(1,1,1,1), padding_y=(dp(15),dp(15)),cursor_color=(1,1,0,1), font_size=sp(16))
        container.add_widget(self.senha2)

        self.feedback = Label(text="", size_hint=(1,None), color=(1,0,0,1))
        container.add_widget(self.feedback)

        btn_criar = RoundedButton(text="Criar", bg_color=(0.9,0.8,0,1), text_color=(0,0,0,1), on_press=self.criar_conta)
        container.add_widget(btn_criar)

        link_voltar = LinkLabel(text="[u][color=00ADEF]Voltar para Login[/color][/u]", markup=True,
                                font_size=sp(14), halign="center", size_hint_y=None)
        link_voltar.bind(size=link_voltar.setter("text_size"))
        link_voltar.bind(texture_size=link_voltar.setter("size"))
        link_voltar.bind(on_press=self.voltar_login)
        container.add_widget(link_voltar)

        link_reset = LinkLabel(text="[u][color=00ADEF]Esqueci a senha[/color][/u]", markup=True,
                               font_size=sp(14), halign="center", size_hint_y=None)
        link_reset.bind(size=link_reset.setter("text_size"))
        link_reset.bind(texture_size=link_reset.setter("size"))
        link_reset.bind(on_press=self.abrir_reset_senha)
        container.add_widget(link_reset)

        scroll.add_widget(container)
        self.add_widget(scroll)

    def on_touch_down(self, touch):
        self._touch_start_x = touch.x
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        dx = touch.x - self._touch_start_x
        if dx < -50:  # deslizou mais de 50 pixels para a esquerda
            self.voltar_login(touch)
            return True
        return super().on_touch_move(touch)
    
    def voltar_login(self, instance):
        self.manager.transition.direction = "right"
        self.manager.current = 'login'

    def criar_conta(self, instance):
        nome = self.nome.text.strip()
        email = self.email.text.strip()
        senha = self.senha.text.strip()
        senha2 = self.senha2.text.strip()

        if not nome or not email or not senha or not senha2:
            self.feedback.color = (1,0,0,1)
            self.feedback.text = "Preencha todos os campos!"
            return

        if senha != senha2:
            self.feedback.color = (1,0,0,1)
            self.feedback.text = "As senhas não coincidem!"
            return

        res = firebase_signup(nome, email, senha)
        if res.status_code == 200:
            self.feedback.color = (0,1,0,1)
            self.feedback.text = "Conta criada com sucesso!"
        else:
            erro = res.json().get("error", {}).get("message", "")
            if "EMAIL_EXISTS" in erro:
                self.feedback.text = "E-mail já cadastrado!"
            elif "INVALID_EMAIL" in erro:
                self.feedback.text = "E-mail inválido!"
            elif "WEAK_PASSWORD" in erro:
                self.feedback.text = "Senha muito fraca! (mínimo 6 caracteres)"
            else:
                self.feedback.text = "Erro ao criar conta. Tente novamente."
            self.feedback.color = (1,0,0,1)

    def abrir_reset_senha(self, instance):
        self.manager.transition.direction = "left"
        self.manager.current = 'reset_password'

# ----------------- TELA DE REDEFINIÇÃO DE SENHA -----------------
class ResetPasswordScreen(FloatLayout):
    def __init__(self, manager, **kwargs):
        super().__init__(**kwargs)
        self.manager = manager
        self._touch_start_x = 0

        if platform == 'android':
            Window.fullscreen = True
        else:
            Window.size = (360, 640)

        caminho_fundo = os.path.join(os.path.dirname(__file__), "fundo2.jpg")
        background = Image(source=caminho_fundo, allow_stretch=True, keep_ratio=False)
        self.add_widget(background)

        container = BoxLayout(orientation="vertical", spacing=dp(15), padding=dp(20), size_hint=(1, None))
        container.bind(minimum_height=container.setter("height"))

        title = Label(text="Redefinir Senha", font_size=sp(22), halign="center", valign="middle", color=(1,1,1,1))
        title.bind(size=title.setter("text_size"))
        container.add_widget(title)

        self.email = TextInput(hint_text="Digite seu e-mail", multiline=False, size_hint_y=None,
                               height=dp(50), background_color=(0,0,0,0.6), foreground_color=(1,1,1,1),
                               padding_y=(dp(15),dp(15)), cursor_color=(1,1,0,1), font_size=sp(16))
        container.add_widget(self.email)

        self.feedback = Label(text="", size_hint=(1,None), color=(1,0,0,1))
        container.add_widget(self.feedback)

        btn_enviar = RoundedButton(text="Enviar link de redefinição", bg_color=(0.9,0.8,0,1),
                                   text_color=(0,0,0,1), on_press=self.enviar_link)
        container.add_widget(btn_enviar)

        link_voltar = LinkLabel(text="[u][color=00ADEF]Voltar para Login[/color][/u]", markup=True,
                                font_size=sp(14), halign="center", size_hint_y=None)
        link_voltar.bind(size=link_voltar.setter("text_size"))
        link_voltar.bind(texture_size=link_voltar.setter("size"))
        link_voltar.bind(on_press=self.voltar_login)
        container.add_widget(link_voltar)

        scroll = ScrollView(size_hint=(1,1), do_scroll_x=False, bar_width=0)
        scroll.add_widget(container)
        self.add_widget(scroll)

    def on_touch_down(self, touch):
        self._touch_start_x = touch.x
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        dx = touch.x - self._touch_start_x
        if dx < -50:  # deslizou mais de 50 pixels para a esquerda
            self.voltar_login(touch)
            return True
        return super().on_touch_move(touch)

    def voltar_login(self, instance):
        self.manager.transition.direction = "right"
        self.manager.current = 'login'

    def enviar_link(self, instance):
        email = self.email.text.strip()
        if not email:
            self.feedback.color = (1,0,0,1)
            self.feedback.text = "Digite seu e-mail!"
            return
        res = firebase_reset_password(email)
        if res.status_code == 200:
            self.feedback.color = (0,1,0,1)
            self.feedback.text = "E-mail de redefinição enviado! Verifique sua caixa de entrada."
        else:
            self.feedback.color = (1,0,0,1)
            erro = res.json().get("error", {}).get("message", "")
            if "EMAIL_NOT_FOUND" in erro:
                self.feedback.text = "E-mail não cadastrado!"
            else:
                self.feedback.text = "Erro ao enviar e-mail. Tente novamente."

    def voltar_login(self, instance):
        self.manager.transition.direction = "right"
        self.manager.current = 'login'

# ----------------- APP PRINCIPAL -----------------
class MyApp(App):
    def build(self):
        sm = ScreenManager()

        login_screen = Screen(name='login')
        login_screen.add_widget(LoginScreen(manager=sm))
        sm.add_widget(login_screen)

        signup_screen = Screen(name='signup')
        signup_screen.add_widget(SignupScreen(manager=sm))
        sm.add_widget(signup_screen)

        reset_screen = Screen(name='reset_password')
        reset_screen.add_widget(ResetPasswordScreen(manager=sm))
        sm.add_widget(reset_screen)

        return sm

if __name__ == "__main__":
    MyApp().run()