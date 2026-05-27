# widgets.py
from kivy.metrics import dp
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


class BarraSuperior(BoxLayout):
    def __init__(self, titulo, manager, destino="inicio", **kwargs):
        super().__init__(size_hint=(1, None), height=dp(64), **kwargs)
        with self.canvas.before:
            Color(*AZUL)
            self._rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._upd, pos=self._upd)

        btn_back = Button(
            text="← Atrás",
            size_hint=(None, 1),
            width=dp(120),
            background_color=AZUL,
            color=BLANCO,
            font_size=dp(16),
        )
        btn_back.bind(on_press=lambda x: setattr(manager, "current", destino))

        lbl = Label(
            text=f"[b]{titulo}[/b]", markup=True, color=BLANCO, font_size=dp(20)
        )
        self.add_widget(btn_back)
        self.add_widget(lbl)

    def _upd(self, inst, val):
        self._rect.size = inst.size
        self._rect.pos = inst.pos


class FilaTabla(BoxLayout):
    def __init__(self, celdas: list, alto=dp(50), alternada=False, **kwargs):
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
                font_size=dp(14),
                halign="center",
                valign="middle",
            )
            lbl.bind(size=lbl.setter("text_size"))
            self.add_widget(lbl)


class TablaEncabezado(BoxLayout):
    def __init__(self, columnas: list, **kwargs):
        super().__init__(
            orientation="horizontal", size_hint=(1, None), height=dp(52), **kwargs
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
                font_size=dp(14),
                halign="center",
                valign="middle",
            )
            lbl.bind(size=lbl.setter("text_size"))
            self.add_widget(lbl)


class TablaScroll(BoxLayout):
    def __init__(self, columnas: list, filas: list, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        self.add_widget(TablaEncabezado(columnas))
        scroll = ScrollView()
        grid = GridLayout(cols=1, size_hint=(1, None), spacing=dp(1))
        grid.bind(minimum_height=grid.setter("height"))

        for i, fila in enumerate(filas):
            grid.add_widget(FilaTabla(fila, alternada=(i % 2 == 0)))

        if not filas:
            grid.add_widget(
                Label(
                    text="Sin registros",
                    color=NEGRO,
                    size_hint=(1, None),
                    height=dp(56),
                )
            )
        scroll.add_widget(grid)
        self.add_widget(scroll)


def popup_confirmar(titulo, mensaje, on_confirmar):
    contenido = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(12))
    contenido.add_widget(Label(text=mensaje, halign="center", font_size=dp(15)))
    btns = BoxLayout(spacing=dp(10), size_hint=(1, None), height=dp(56))
    popup = Popup(title=titulo, content=contenido, size_hint=(0.85, 0.42))

    def confirmar(x):
        popup.dismiss()
        Clock.schedule_once(lambda dt: on_confirmar(), 0)

    btns.add_widget(
        Button(
            text="Cancelar",
            on_press=popup.dismiss,
            background_color=GRIS,
            color=NEGRO,
            font_size=dp(15),
        )
    )
    btns.add_widget(
        Button(
            text="Eliminar",
            on_press=confirmar,
            background_color=ROJO,
            color=BLANCO,
            font_size=dp(15),
        )
    )
    contenido.add_widget(btns)
    popup.open()


def popup_mensaje(titulo, mensaje, color=None):
    color = color or AZUL
    contenido = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(12))
    contenido.add_widget(Label(text=mensaje, halign="center", font_size=dp(14)))
    popup = Popup(title=titulo, content=contenido, size_hint=(0.82, 0.38))
    contenido.add_widget(
        Button(
            text="Aceptar",
            on_press=popup.dismiss,
            background_color=color,
            color=BLANCO,
            size_hint=(1, None),
            height=dp(56),
            font_size=dp(15),
        )
    )
    popup.open()


def campo(label_texto, hint="", multiline=False, input_filter=None) -> tuple:
    row = BoxLayout(
        orientation="vertical",
        size_hint=(1, None),
        height=dp(90) if not multiline else dp(130),
        spacing=dp(4),
    )
    row.add_widget(
        Label(
            text=label_texto,
            size_hint=(1, None),
            height=dp(28),
            color=BLANCO,
            halign="left",
            valign="middle",
            font_size=dp(15),
        )
    )
    ti = TextInput(
        hint_text=hint,
        multiline=multiline,
        input_filter=input_filter,
        size_hint=(1, None),
        height=dp(52) if not multiline else dp(96),
        font_size=dp(15),
    )
    row.add_widget(ti)
    return row, ti
