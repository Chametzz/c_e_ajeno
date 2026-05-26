"""
views/widgets.py
Componentes reutilizables: tabla, formulario, barra de acción.
"""

from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.utils import get_color_from_hex
from kivy.graphics import Color, Rectangle


AZUL = get_color_from_hex("#1565C0")
ROJO = get_color_from_hex("#C62828")
VERDE = get_color_from_hex("#2E7D32")
GRIS = get_color_from_hex("#EEEEEE")
BLANCO = get_color_from_hex("#FFFFFF")
NEGRO = get_color_from_hex("#212121")


# ─────────────────────────────────────────
#  Barra de navegación superior
# ─────────────────────────────────────────
class BarraSuperior(BoxLayout):
    def __init__(self, titulo, manager, destino="inicio", **kwargs):
        super().__init__(size_hint=(1, None), height=56, **kwargs)
        with self.canvas.before:
            Color(*AZUL)
            self._rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._upd, pos=self._upd)

        btn_back = Button(
            text="← Atrás",
            size_hint=(None, 1),
            width=100,
            background_color=AZUL,
            color=BLANCO,
            font_size=14,
            font_name="seguiemj",
        )
        btn_back.bind(on_press=lambda x: setattr(manager, "current", destino))

        lbl = Label(text=f"[b]{titulo}[/b]", markup=True, color=BLANCO, font_size=18)
        self.add_widget(btn_back)
        self.add_widget(lbl)

    def _upd(self, inst, val):
        self._rect.size = inst.size
        self._rect.pos = inst.pos


# ─────────────────────────────────────────
#  Tabla de datos
# ─────────────────────────────────────────
class FilaTabla(BoxLayout):
    def __init__(self, celdas: list, alto=40, alternada=False, **kwargs):
        super().__init__(
            orientation="horizontal", size_hint=(1, None), height=alto, **kwargs
        )
        bg = get_color_from_hex("#F0F4FF") if alternada else BLANCO
        with self.canvas.before:
            Color(*bg)
            self._rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(
            size=lambda i, v: setattr(self._rect, "size", v),
            pos=lambda i, v: setattr(self._rect, "pos", v),
        )

        for celda in celdas:
            lbl = Label(
                text=str(celda) if celda is not None else "—",
                color=NEGRO,
                font_size=13,
                halign="center",
                valign="middle",
            )
            lbl.bind(size=lbl.setter("text_size"))
            self.add_widget(lbl)


class TablaEncabezado(BoxLayout):
    def __init__(self, columnas: list, **kwargs):
        super().__init__(
            orientation="horizontal", size_hint=(1, None), height=44, **kwargs
        )
        with self.canvas.before:
            Color(*get_color_from_hex("#1E3A5F"))
            self._rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(
            size=lambda i, v: setattr(self._rect, "size", v),
            pos=lambda i, v: setattr(self._rect, "pos", v),
        )
        for col in columnas:
            lbl = Label(
                text=f"[b]{col}[/b]",
                markup=True,
                color=BLANCO,
                font_size=13,
                halign="center",
                valign="middle",
            )
            lbl.bind(size=lbl.setter("text_size"))
            self.add_widget(lbl)


class TablaScroll(BoxLayout):
    """Tabla con scroll, encabezado fijo y filas alternadas."""

    def __init__(self, columnas: list, filas: list, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        self.add_widget(TablaEncabezado(columnas))
        scroll = ScrollView()
        grid = GridLayout(cols=1, size_hint=(1, None), spacing=1)
        grid.bind(minimum_height=grid.setter("height"))

        for i, fila in enumerate(filas):
            grid.add_widget(FilaTabla(fila, alternada=(i % 2 == 0)))

        if not filas:
            grid.add_widget(
                Label(text="Sin registros", color=NEGRO, size_hint=(1, None), height=50)
            )
        scroll.add_widget(grid)
        self.add_widget(scroll)


# ─────────────────────────────────────────
#  Popup de confirmación
# ─────────────────────────────────────────
"""def popup_confirmar(titulo, mensaje, on_confirmar):
    contenido = BoxLayout(orientation="vertical", padding=20, spacing=12)
    contenido.add_widget(Label(text=mensaje, halign="center"))
    btns = BoxLayout(spacing=10, size_hint=(1, None), height=44)

    popup = Popup(title=titulo, content=contenido, size_hint=(0.8, 0.4))

    def confirmar(x):
        popup.dismiss()
        on_confirmar()

    btns.add_widget(Button(text="Cancelar", on_press=popup.dismiss,
                            background_color=GRIS, color=NEGRO))
    btns.add_widget(Button(text="Eliminar", on_press=confirmar,
                            background_color=ROJO, color=BLANCO))
    contenido.add_widget(btns)
    popup.open()"""


def popup_confirmar(titulo, mensaje, on_confirmar):
    contenido = BoxLayout(orientation="vertical", padding=20, spacing=12)
    contenido.add_widget(Label(text=mensaje, halign="center"))
    btns = BoxLayout(spacing=10, size_hint=(1, None), height=44)
    popup = Popup(title=titulo, content=contenido, size_hint=(0.8, 0.4))

    def confirmar(x):
        popup.dismiss()
        Clock.schedule_once(
            lambda dt: on_confirmar(), 0
        )  # ← diferir al siguiente frame

    btns.add_widget(
        Button(
            text="Cancelar", on_press=popup.dismiss, background_color=GRIS, color=NEGRO
        )
    )
    btns.add_widget(
        Button(text="Eliminar", on_press=confirmar, background_color=ROJO, color=BLANCO)
    )
    contenido.add_widget(btns)
    popup.open()


# ─────────────────────────────────────────
#  Popup de mensaje (éxito / error)
# ─────────────────────────────────────────
def popup_mensaje(titulo, mensaje, color=None):
    color = color or AZUL
    contenido = BoxLayout(orientation="vertical", padding=20, spacing=12)
    contenido.add_widget(Label(text=mensaje, halign="center"))
    popup = Popup(title=titulo, content=contenido, size_hint=(0.75, 0.35))
    contenido.add_widget(
        Button(
            text="Aceptar",
            on_press=popup.dismiss,
            background_color=color,
            color=BLANCO,
            size_hint=(1, None),
            height=44,
        )
    )
    popup.open()


# ─────────────────────────────────────────
#  Campo de formulario
# ─────────────────────────────────────────
def campo(label_texto, hint="", multiline=False, input_filter=None) -> tuple:
    """Retorna (BoxLayout_campo, TextInput)."""
    row = BoxLayout(
        orientation="vertical",
        size_hint=(1, None),
        height=80 if not multiline else 120,
        spacing=4,
    )
    row.add_widget(
        Label(
            text=label_texto,
            size_hint=(1, None),
            height=24,
            color=BLANCO,
            halign="left",
            valign="middle",
            font_size=14,
        )
    )
    ti = TextInput(
        hint_text=hint,
        multiline=multiline,
        input_filter=input_filter,
        size_hint=(1, None),
        height=44 if not multiline else 88,
        font_size=14,
    )
    row.add_widget(ti)
    return row, ti
