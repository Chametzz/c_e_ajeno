from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.metrics import dp

from database.conexion import conectar

# Mapa de rol -> nombre de pantalla del menú
MENU_POR_ROL = {
    "admin": "menu_admin",
    "docente": "menu_docente",
    "estudiante": "menu_estudiante",
}


class LoginScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(
            orientation="vertical",
            spacing=dp(15),
            padding=dp(30)
        )

        titulo = Label(
            text="CONTROL ESCOLAR",
            font_size=dp(28)
        )

        self.usuario = TextInput(
            hint_text="Usuario",
            multiline=False
        )

        self.password = TextInput(
            hint_text="Contraseña",
            password=True,
            multiline=False
        )

        self.msg = Label(text="")

        btn = Button(
            text="Iniciar sesión",
            size_hint=(1, None),
            height=dp(50)
        )

        btn.bind(on_press=self.login)

        layout.add_widget(titulo)
        layout.add_widget(self.usuario)
        layout.add_widget(self.password)
        layout.add_widget(btn)
        layout.add_widget(self.msg)

        self.add_widget(layout)

    def on_pre_enter(self):
        # Limpiar campos cada vez que se muestra el login
        self.usuario.text = ""
        self.password.text = ""
        self.msg.text = ""

    def login(self, instance):
        user = self.usuario.text.strip()
        pwd = self.password.text

        if not user or not pwd:
            self.msg.text = "Por favor ingresa usuario y contraseña"
            return

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT rol FROM usuarios WHERE usuario=? AND password=?",
            (user, pwd)
        )

        resultado = cursor.fetchone()
        conn.close()

        if resultado:
            rol = resultado[0]

            # Guardar rol en la App para que las demás pantallas lo usen
            app = App.get_running_app()
            app.rol_actual = rol
            app.usuario_actual = user

            destino = MENU_POR_ROL.get(rol)
            if destino:
                self.manager.current = destino
            else:
                self.msg.text = f"Rol desconocido: {rol}"
        else:
            self.msg.text = "Usuario o contraseña incorrectos"
