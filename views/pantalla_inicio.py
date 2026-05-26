"""
views/pantalla_inicio.py
Pantalla de inicio y menú principal.
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle
from kivy.utils import get_color_from_hex


AZUL = get_color_from_hex("#1565C0")
AZUL_DARK = get_color_from_hex("#0D47A1")
BLANCO = get_color_from_hex("#FFFFFF")
GRIS = get_color_from_hex("#F5F5F5")


def boton_menu(texto, color=AZUL, on_press=None):
    btn = Button(
        text=texto,
        size_hint=(1, None),
        height=54,
        background_color=color,
        color=BLANCO,
        font_size=16,
        bold=True,
    )
    if on_press:
        btn.bind(on_press=on_press)
    return btn


class PantallaInicio(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="vertical", spacing=0)

        # Encabezado
        header = BoxLayout(size_hint=(1, None), height=80, padding=(20, 10))
        with header.canvas.before:
            Color(*AZUL_DARK)
            self._rect = Rectangle(size=header.size, pos=header.pos)
        header.bind(size=self._update_rect, pos=self._update_rect)

        title = Label(
            text="[b]Control Escolar[/b]",
            markup=True,
            font_size=22,
            color=BLANCO,
            halign="left",
            valign="middle",
        )
        title.bind(size=title.setter("text_size"))
        header.add_widget(title)
        root.add_widget(header)

        # Menú

        scroll = ScrollView()
        menu = BoxLayout(
            orientation="vertical", spacing=12, padding=(30, 30), size_hint=(1, None)
        )
        menu.bind(minimum_height=menu.setter("height"))
        opciones = [
            ("Estudiantes", "estudiantes"),
            ("Profesores", "profesores"),
            ("Carreras", "carreras"),
            ("Materias", "materias"),
            ("Aulas", "aulas"),
            ("Periodos", "periodos"),
            ("Grupos", "grupos"),
            ("Calificaciones", "calificaciones"),
            ("Reportes", "reportes"),
        ]
        for texto, pantalla in opciones:
            btn = boton_menu(texto, on_press=lambda x, p=pantalla: self.ir_a(p))
            menu.add_widget(btn)

        scroll.add_widget(menu)
        root.add_widget(scroll)
        # root.add_widget(menu)
        self.add_widget(root)

    def _update_rect(self, instance, value):
        self._rect.pos = instance.pos
        self._rect.size = instance.size

    def ir_a(self, pantalla):
        self.manager.current = pantalla
