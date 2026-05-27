# pantalla_calificaciones.py
from kivy.app import App
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Rectangle
from kivy.utils import get_color_from_hex

from models.modelos import CalificacionModel
from utils.validaciones import calificacion_a_letra, validar_calificacion
from views.widgets import BarraSuperior, TablaEncabezado, popup_mensaje

AZUL   = get_color_from_hex("#1565C0")
BLANCO = get_color_from_hex("#FFFFFF")
NEGRO  = get_color_from_hex("#212121")
VERDE  = get_color_from_hex("#2E7D32")
ROJO   = get_color_from_hex("#C62828")
GRIS   = get_color_from_hex("#F0F4FF")


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

    def _rol(self):
        app = App.get_running_app()
        return getattr(app, "rol_actual", "estudiante")

    def _build(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical")
        root.add_widget(BarraSuperior("Calificaciones", self.manager))

        # Barra de búsqueda
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

        puede_editar = self._rol() in ("admin", "docente")

        datos = CalificacionModel.todas_con_id()

        if filtro:
            fl = filtro.lower()
            datos = [
                d for d in datos
                if fl in d.get("estudiante", "").lower()
                or fl in d.get("materia", "").lower()
            ]

        if puede_editar:
            # Columnas con campos editables
            cols = ["Estudiante", "Materia", "Periodo", "Parcial", "Final", "Obs.", "Guardar"]
        else:
            cols = ["Estudiante", "Materia", "Periodo", "Parcial", "Final", "Letra"]

        outer = BoxLayout(orientation="vertical")
        outer.add_widget(TablaEncabezado(cols))

        scroll = ScrollView()
        grid = GridLayout(cols=1, size_hint=(1, None), spacing=dp(2))
        grid.bind(minimum_height=grid.setter("height"))

        for i, d in enumerate(datos):
            if puede_editar:
                fila = self._fila_editable(d, i)
            else:
                fila = self._fila_lectura(d, i)
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

    def _fila_editable(self, d, idx):
        """Fila con TextInput para parcial, final, obs y botón guardar."""
        fila = BoxLayout(
            size_hint=(1, None),
            height=dp(58),
            spacing=dp(3),
            padding=(dp(4), dp(2)),
        )
        bg = GRIS if idx % 2 == 0 else BLANCO
        with fila.canvas.before:
            Color(*bg)
            r = Rectangle(size=fila.size, pos=fila.pos)
        fila.bind(
            size=lambda inst, v, rect=r: setattr(rect, "size", v),
            pos=lambda inst, v, rect=r: setattr(rect, "pos", v),
        )

        def lbl(texto, sh=(1.6, 1)):
            l = Label(text=str(texto) if texto is not None else "—",
                      color=NEGRO, font_size=dp(12),
                      halign="center", valign="middle",
                      size_hint=sh)
            l.bind(size=l.setter("text_size"))
            return l

        def _str(v):
            return str(v) if v is not None else ""

        ti_p = TextInput(
            text=_str(d.get("calificacion_parcial")),
            hint_text="Parcial",
            input_filter="float",
            font_size=dp(13),
            multiline=False,
            size_hint=(0.9, 1),
        )
        ti_f = TextInput(
            text=_str(d.get("calificacion_final")),
            hint_text="Final",
            input_filter="float",
            font_size=dp(13),
            multiline=False,
            size_hint=(0.9, 1),
        )
        ti_o = TextInput(
            text=d.get("observaciones") or "",
            hint_text="Obs.",
            font_size=dp(12),
            multiline=False,
            size_hint=(1.4, 1),
        )

        btn = Button(
            text="Guardar",
            size_hint=(None, 1),
            width=dp(48),
            background_color=VERDE,
            color=BLANCO,
            font_size=dp(18),
        )
        cid = d["id_calificacion"]
        btn.bind(
            on_press=lambda x, cid=cid, tp=ti_p, tf=ti_f, to=ti_o:
                self._guardar(cid, tp.text, tf.text, to.text)
        )

        fila.add_widget(lbl(d.get("estudiante", "")))
        fila.add_widget(lbl(d.get("materia", ""), sh=(1.2, 1)))
        fila.add_widget(lbl(d.get("periodo", ""), sh=(1.0, 1)))
        fila.add_widget(ti_p)
        fila.add_widget(ti_f)
        fila.add_widget(ti_o)
        fila.add_widget(btn)
        return fila

    def _fila_lectura(self, d, idx):
        """Fila de solo lectura para estudiantes."""
        fila = BoxLayout(
            size_hint=(1, None),
            height=dp(56),
            spacing=dp(2),
            padding=(dp(4), dp(2)),
        )
        bg = GRIS if idx % 2 == 0 else BLANCO
        with fila.canvas.before:
            Color(*bg)
            r = Rectangle(size=fila.size, pos=fila.pos)
        fila.bind(
            size=lambda inst, v, rect=r: setattr(rect, "size", v),
            pos=lambda inst, v, rect=r: setattr(rect, "pos", v),
        )

        parcial = d.get("calificacion_parcial")
        final   = d.get("calificacion_final")
        letra   = calificacion_a_letra(final) if final is not None else "—"

        datos_fila = [
            d.get("estudiante", ""),
            d.get("materia", ""),
            d.get("periodo", ""),
            f"{parcial:.1f}" if parcial is not None else "—",
            f"{final:.1f}"   if final   is not None else "—",
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
        return fila

    def _guardar(self, id_cal, parcial_txt, final_txt, obs):
        p = float(parcial_txt) if validar_calificacion(parcial_txt) else None
        f = float(final_txt)   if validar_calificacion(final_txt)   else None

        if parcial_txt.strip() and p is None:
            popup_mensaje("Error", "Parcial inválido (0-100).", ROJO)
            return
        if final_txt.strip() and f is None:
            popup_mensaje("Error", "Final inválido (0-100).", ROJO)
            return

        CalificacionModel.actualizar(id_cal, p, f, obs)
        popup_mensaje("Guardado", "Calificación actualizada correctamente.", VERDE)
        # Recargar tabla después del popup
        Clock.schedule_once(lambda dt: self._cargar(
            self.ti_busq.text if hasattr(self, "ti_busq") else ""
        ), 0.3)
