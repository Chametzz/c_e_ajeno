# pantalla_calificaciones.py
from kivy.metrics import dp
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Rectangle
from kivy.utils import get_color_from_hex

from models.modelos import CalificacionModel
from utils.validaciones import calificacion_a_letra
from views.widgets import BarraSuperior, TablaEncabezado

AZUL = get_color_from_hex("#1565C0")
BLANCO = get_color_from_hex("#FFFFFF")
NEGRO = get_color_from_hex("#212121")
VERDE = get_color_from_hex("#2E7D32")
ROJO = get_color_from_hex("#C62828")


def _color_cal(val):
    if val is None:
        return get_color_from_hex("#9E9E9E")
    if val >= 90:
        return get_color_from_hex("#1B5E20")
    if val >= 70:
        return get_color_from_hex("#1565C0")
    return get_color_from_hex("#B71C1C")


class PantallaCalificaciones(Screen):
    def on_pre_enter(self):
        self._build()

    def _build(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical")
        root.add_widget(BarraSuperior("Calificaciones", self.manager))

        barra = BoxLayout(
            size_hint=(1, None), height=dp(62), spacing=dp(8), padding=(dp(10), dp(6))
        )
        self.ti_busq = TextInput(
            hint_text="Buscar estudiante o materia...",
            multiline=False,
            font_size=dp(14),
        )
        self.ti_busq.bind(text=lambda inst, v: self._cargar(v))
        barra.add_widget(self.ti_busq)
        root.add_widget(barra)

        self.contenedor = BoxLayout(orientation="vertical")
        self._cargar()
        root.add_widget(self.contenedor)
        self.add_widget(root)

    def _cargar(self, filtro=""):
        self.contenedor.clear_widgets()
        datos = CalificacionModel.todas()

        if filtro:
            fl = filtro.lower()
            datos = [
                d
                for d in datos
                if fl in d.get("estudiante", "").lower()
                or fl in d.get("materia", "").lower()
            ]

        cols = ["Estudiante", "Materia", "Periodo", "Parcial", "Final", "Letra"]
        outer = BoxLayout(orientation="vertical")
        outer.add_widget(TablaEncabezado(cols))

        scroll = ScrollView()
        grid = GridLayout(cols=1, size_hint=(1, None), spacing=dp(1))
        grid.bind(minimum_height=grid.setter("height"))

        for i, d in enumerate(datos):
            fila = BoxLayout(
                size_hint=(1, None),
                height=dp(56),
                spacing=dp(2),
                padding=(dp(4), dp(2)),
            )
            bg = get_color_from_hex("#F0F4FF") if i % 2 == 0 else BLANCO
            with fila.canvas.before:
                Color(*bg)
                r = Rectangle(size=fila.size, pos=fila.pos)
            fila.bind(
                size=lambda inst, v, rect=r: setattr(rect, "size", v),
                pos=lambda inst, v, rect=r: setattr(rect, "pos", v),
            )

            parcial = d.get("calificacion_parcial")
            final = d.get("calificacion_final")
            letra = calificacion_a_letra(final) if final is not None else "—"

            datos_fila = [
                d.get("estudiante", ""),
                d.get("materia", ""),
                d.get("periodo", ""),
                f"{parcial:.1f}" if parcial is not None else "—",
                f"{final:.1f}" if final is not None else "—",
                letra,
            ]
            for j, txt in enumerate(datos_fila):
                color = _color_cal(final) if j == 4 else NEGRO
                lbl = Label(
                    text=str(txt),
                    color=color,
                    font_size=dp(13),
                    halign="center",
                    valign="middle",
                )
                lbl.bind(size=lbl.setter("text_size"))
                fila.add_widget(lbl)

            grid.add_widget(fila)

        if not datos:
            grid.add_widget(
                Label(
                    text="Sin calificaciones registradas",
                    color=NEGRO,
                    size_hint=(1, None),
                    height=dp(56),
                )
            )

        scroll.add_widget(grid)
        outer.add_widget(scroll)
        self.contenedor.add_widget(outer)
