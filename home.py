#home.py
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import AsyncImage
from kivy.uix.popup import Popup
from kivy.properties import BooleanProperty
import requests

# ----------------- Menu lateral -----------------
class SideMenu(BoxLayout):
    visible = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', size_hint=(0.6, 1), pos_hint={'right': 0}, **kwargs)
        self.spacing = 10
        self.padding = 20
        self.add_widget(Button(text="Configurações", size_hint_y=None, height=50))
        self.add_widget(Button(text="Pagamentos", size_hint_y=None, height=50))
        self.add_widget(Button(text="Fale conosco", size_hint_y=None, height=50))
        self.add_widget(Button(text="Sobre o app", size_hint_y=None, height=50))

    def toggle(self):
        self.visible = not self.visible
        self.pos_hint = {'right': 1} if self.visible else {'right': 0}

# ----------------- Detalhes do Exercício -----------------
class ExercicioDetalhes(BoxLayout):
    def __init__(self, nome, gif_url=None, parent_tab=None, **kwargs):
        super().__init__(orientation='vertical', spacing=10, padding=10, **kwargs)
        self.parent_tab = parent_tab

        voltar_btn = Button(text="← Voltar", size_hint_y=None, height=50)
        voltar_btn.bind(on_press=lambda x: self.parent_tab.show_exercicios_lista())
        self.add_widget(voltar_btn)

        self.add_widget(Label(text=nome, font_size=24, size_hint_y=None, height=40))
        self.add_widget(Label(text="Tempo de descanso: 60-90s\nExecução: 3 séries de 10 repetições",
                              size_hint_y=None, height=80))
        if gif_url:
            self.add_widget(AsyncImage(source=gif_url, allow_stretch=True, keep_ratio=True))

# ----------------- Aba Exercícios -----------------
class ExerciciosTab(BoxLayout):
    def __init__(self, admin=False, **kwargs):
        super().__init__(orientation='vertical', spacing=10, padding=10, **kwargs)
        self.admin = admin
        self.gif_links = {}

        self.search_input = TextInput(hint_text="Buscar exercício...", size_hint_y=None, height=40, multiline=False)
        self.search_input.bind(text=self.on_search_text)
        self.add_widget(self.search_input)

        if self.admin:
            add_btn = Button(text="Adicionar Exercício", size_hint_y=None, height=50)
            add_btn.bind(on_press=self.show_add_exercicio_popup)
            self.add_widget(add_btn)

        self.content_area = BoxLayout()
        self.add_widget(self.content_area)

        self.carregar_exercicios()
        self.show_exercicios_lista()

    def carregar_exercicios(self):
        url = "https://maisquefitnessapp-5eac0-default-rtdb.firebaseio.com/exercicios.json"
        try:
            res = requests.get(url)
            data = res.json() or {}
            self.gif_links = data
        except Exception as e:
            print("Erro ao carregar exercícios:", e)
            self.gif_links = {}

    def on_search_text(self, instance, value):
        self.show_exercicios_lista(filter_text=value)

    def show_exercicios_lista(self, filter_text=""):
        self.content_area.clear_widgets()
        scroll = ScrollView()
        container = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        container.bind(minimum_height=container.setter('height'))

        for nome, gif_url in self.gif_links.items():
            if filter_text.lower() in nome.lower():
                btn = Button(text=nome, size_hint_y=None, height=50)
                btn.bind(on_press=lambda x, n=nome: self.show_detalhes_exercicio(n))
                container.add_widget(btn)

        scroll.add_widget(container)
        self.content_area.add_widget(scroll)

    def show_detalhes_exercicio(self, nome_exercicio):
        self.content_area.clear_widgets()
        gif_url = self.gif_links.get(nome_exercicio)
        self.content_area.add_widget(ExercicioDetalhes(nome_exercicio, gif_url=gif_url, parent_tab=self))

    def show_add_exercicio_popup(self, *args):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        nome_input = TextInput(hint_text="Nome do exercício", multiline=False)
        url_input = TextInput(hint_text="URL do GIF", multiline=False)
        save_btn = Button(text="Salvar", size_hint_y=None, height=50)

        layout.add_widget(nome_input)
        layout.add_widget(url_input)
        layout.add_widget(save_btn)

        popup = Popup(title="Adicionar Exercício", content=layout, size_hint=(0.8, 0.5))

        def salvar_exercicio(instance):
            nome = nome_input.text.strip()
            url = url_input.text.strip()
            if nome:
                try:
                    requests.patch(
                        "https://maisquefitnessapp-5eac0-default-rtdb.firebaseio.com/exercicios.json",
                        json={nome: url}
                    )
                except Exception as e:
                    print("Erro ao salvar no Firebase:", e)
                self.gif_links[nome] = url
                self.show_exercicios_lista()
                popup.dismiss()

        save_btn.bind(on_press=salvar_exercicio)
        popup.open()

# ----------------- Aba Treino -----------------
class TreinoTab(BoxLayout):
    def __init__(self, admin=False, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.admin = admin
        top_bar = BoxLayout(size_hint_y=None, height=50, spacing=5, padding=5)
        btn_ficha = Button(text="Minha ficha")
        btn_exercicios = Button(text="Exercícios")
        btn_treinos = Button(text="Treinos")
        top_bar.add_widget(btn_ficha)
        top_bar.add_widget(btn_exercicios)
        top_bar.add_widget(btn_treinos)
        self.add_widget(top_bar)

        self.content_area = BoxLayout()
        self.add_widget(self.content_area)

        btn_ficha.bind(on_press=lambda x: self.show_content("Minha ficha"))
        btn_exercicios.bind(on_press=lambda x: self.show_content("Exercícios"))
        btn_treinos.bind(on_press=lambda x: self.show_content("Treinos"))

        self.show_content("Minha ficha")

    def show_content(self, name):
        self.content_area.clear_widgets()
        if name == "Exercícios":
            self.content_area.add_widget(ExerciciosTab(admin=self.admin))
        else:
            self.content_area.add_widget(Label(text=f"{name} - Conteúdo aqui", font_size=24))

# ----------------- Tela principal -----------------
class HomeScreen(FloatLayout):
    def __init__(self, manager=None, admin=False, **kwargs):
        super().__init__(**kwargs)
        self.manager = manager
        self.admin = admin

        self.content_area = BoxLayout(orientation='vertical', size_hint=(1, 0.9))
        self.add_widget(self.content_area)

        bottom_bar = BoxLayout(size_hint=(1, 0.1), orientation='horizontal', spacing=5, padding=5)
        self.btn_dieta = Button(text="Dieta")
        self.btn_treino = Button(text="Treino")
        self.btn_perfil = Button(text="Perfil")
        bottom_bar.add_widget(self.btn_dieta)
        bottom_bar.add_widget(self.btn_treino)
        bottom_bar.add_widget(self.btn_perfil)
        self.add_widget(bottom_bar)

        self.side_menu = SideMenu()
        self.add_widget(self.side_menu)

        menu_button = Button(text="☰", size_hint=(None, None), size=(50, 50),
                             pos_hint={'right': 0.98, 'top': 0.98})
        menu_button.bind(on_press=lambda x: self.side_menu.toggle())
        self.add_widget(menu_button)

        self.btn_treino.bind(on_press=lambda x: self.show_screen("Treino"))
        self.btn_dieta.bind(on_press=lambda x: self.show_screen("Dieta"))
        self.btn_perfil.bind(on_press=lambda x: self.show_screen("Perfil"))

        self.show_screen("Treino")

    def show_screen(self, screen_name):
        self.content_area.clear_widgets()
        if screen_name == "Treino":
            self.content_area.add_widget(TreinoTab(admin=self.admin))
        else:
            self.content_area.add_widget(Label(text=f"{screen_name} - Conteúdo aqui", font_size=24))