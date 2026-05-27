
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.metrics import dp

class MenuDocente(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(20))

        opciones = [
            ("Consultar grupos", "grupos"),
            ("Registrar calificaciones", "calificaciones"),
        ]

        for texto, pantalla in opciones:

            btn = Button(text=texto, size_hint=(1,None), height=dp(50))
            btn.bind(on_press=lambda x, p=pantalla: self.ir(p))

            layout.add_widget(btn)

        salir = Button(text="Cerrar sesión", size_hint=(1,None), height=dp(50))
        salir.bind(on_press=lambda x: self.logout())

        layout.add_widget(salir)

        self.add_widget(layout)

    def ir(self, pantalla):
        self.manager.current = pantalla

    def logout(self):
        from kivy.app import App
        app = App.get_running_app()
        app.rol_actual = ""
        app.usuario_actual = ""
        self.manager.current = "login"
