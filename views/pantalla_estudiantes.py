# pantalla_estudiantes.py
from kivy.metrics import dp
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.graphics import Color, Rectangle
from kivy.utils import get_color_from_hex
from kivy.clock import Clock

from models.modelos import EstudianteModel, CarreraModel
from utils.validaciones import validar_correo, limpiar_texto
from views.widgets import (
    BarraSuperior,
    TablaEncabezado,
    TablaScroll,
    popup_confirmar,
    popup_mensaje,
    campo,
)

AZUL = get_color_from_hex("#1565C0")
VERDE = get_color_from_hex("#2E7D32")
ROJO = get_color_from_hex("#C62828")
BLANCO = get_color_from_hex("#FFFFFF")
NEGRO = get_color_from_hex("#212121")


class PantallaEstudiantes(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_pre_enter(self):
        self._build()

    def _build(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical")
        root.add_widget(BarraSuperior("Estudiantes", self.manager))

        acciones = BoxLayout(
            size_hint=(1, None), height=dp(62), spacing=dp(8), padding=(dp(10), dp(6))
        )
        btn_nuevo = Button(
            text="+ Nuevo",
            background_color=VERDE,
            color=BLANCO,
            size_hint=(None, 1),
            width=dp(130),
            font_size=dp(15),
        )
        btn_nuevo.bind(on_press=self.abrir_form_nuevo)

        self.busqueda = TextInput(
            hint_text="Buscar por nombre o # control...",
            size_hint=(1, 1),
            font_size=dp(14),
            multiline=False,
        )
        self.busqueda.bind(text=self.filtrar)

        acciones.add_widget(btn_nuevo)
        acciones.add_widget(self.busqueda)
        root.add_widget(acciones)

        self.contenedor_tabla = BoxLayout(orientation="vertical")
        self._cargar_tabla()
        root.add_widget(self.contenedor_tabla)
        self.add_widget(root)

    def _cargar_tabla(self, texto=""):
        self.contenedor_tabla.clear_widgets()
        registros = (
            EstudianteModel.buscar_nombre(texto) if texto else EstudianteModel.todos()
        )

        columnas = ["# Control", "Nombre", "Carrera", "Semestre", "Acciones"]
        filas_widgets = BoxLayout(orientation="vertical")
        filas_widgets.add_widget(TablaEncabezado(columnas))

        scroll = ScrollView()
        grid = GridLayout(cols=1, size_hint=(1, None), spacing=dp(1))
        grid.bind(minimum_height=grid.setter("height"))

        for i, est in enumerate(registros):
            fila = BoxLayout(
                size_hint=(1, None),
                height=dp(60),
                spacing=dp(4),
                padding=(dp(4), dp(4)),
            )
            bg = get_color_from_hex("#F0F4FF") if i % 2 == 0 else BLANCO
            with fila.canvas.before:
                Color(*bg)
                r = Rectangle(size=fila.size, pos=fila.pos)
            fila.bind(
                size=lambda inst, v, rect=r: setattr(rect, "size", v),
                pos=lambda inst, v, rect=r: setattr(rect, "pos", v),
            )

            for txt in [
                est["num_control"],
                f"{est['nombre']} {est['apellidos']}",
                est.get("carrera", ""),
                str(est["semestre"]),
            ]:
                lbl = Label(
                    text=str(txt),
                    color=NEGRO,
                    font_size=dp(13),
                    halign="center",
                    valign="middle",
                )
                lbl.bind(size=lbl.setter("text_size"))
                fila.add_widget(lbl)

            btns = BoxLayout(spacing=dp(3), size_hint=(None, 1), width=dp(195))
            b_edit = Button(
                text="Editar", font_size=dp(13), background_color=AZUL, color=BLANCO
            )
            b_cal = Button(
                text="Califs",
                font_size=dp(13),
                background_color=get_color_from_hex("#6A1B9A"),
                color=BLANCO,
            )
            b_del = Button(
                text="Borrar", font_size=dp(13), background_color=ROJO, color=BLANCO
            )

            eid = est["id_estudiante"]
            b_edit.bind(on_press=lambda x, e=est: self.abrir_form_editar(e))
            b_cal.bind(on_press=lambda x, i=eid: self.ver_calificaciones(i))
            b_del.bind(
                on_press=lambda x, i=eid, e=est: popup_confirmar(
                    "Eliminar estudiante",
                    f"¿Eliminar a {e['nombre']} {e['apellidos']}?",
                    lambda: self._eliminar(i),
                )
            )

            btns.add_widget(b_edit)
            btns.add_widget(b_cal)
            btns.add_widget(b_del)
            fila.add_widget(btns)
            grid.add_widget(fila)

        if not registros:
            grid.add_widget(
                Label(
                    text="Sin registros",
                    color=NEGRO,
                    size_hint=(1, None),
                    height=dp(56),
                )
            )

        scroll.add_widget(grid)
        filas_widgets.add_widget(scroll)
        self.contenedor_tabla.add_widget(filas_widgets)

    def filtrar(self, instance, texto):
        self._cargar_tabla(texto)

    def _eliminar(self, id_est):
        EstudianteModel.eliminar(id_est)
        popup_mensaje("Listo", "Estudiante eliminado.", ROJO)
        self._cargar_tabla()

    def abrir_form_nuevo(self, *args):
        self._form_popup()

    def abrir_form_editar(self, est):
        self._form_popup(est)

    def _form_popup(self, est=None):
        carreras = CarreraModel.todos()
        contenido = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(16))
        scroll = ScrollView()
        inner = BoxLayout(orientation="vertical", size_hint=(1, None), spacing=dp(8))
        inner.bind(minimum_height=inner.setter("height"))

        r_ctrl, ti_ctrl = campo("# Control", "21SC001")
        r_nom, ti_nom = campo("Nombre", "Ana")
        r_ape, ti_ape = campo("Apellidos", "García Torres")
        r_mail, ti_mail = campo("Correo", "ana@est.mx")
        r_sem, ti_sem = campo("Semestre", "4", input_filter="int")

        lbl_car = Label(
            text="Carrera",
            size_hint=(1, None),
            height=dp(28),
            color=BLANCO,
            halign="left",
            font_size=dp(15),
        )
        spinner_car = Spinner(
            values=[c["nombre"] for c in carreras],
            size_hint=(1, None),
            height=dp(52),
            text=carreras[0]["nombre"] if carreras else "",
            font_size=dp(14),
        )

        for w in [r_ctrl, r_nom, r_ape, r_mail, r_sem, lbl_car, spinner_car]:
            inner.add_widget(w)

        if est:
            ti_ctrl.text = est.get("num_control", "")
            ti_nom.text = est.get("nombre", "")
            ti_ape.text = est.get("apellidos", "")
            ti_mail.text = est.get("correo", "")
            ti_sem.text = str(est.get("semestre", ""))
            car = next(
                (c for c in carreras if c["id_carrera"] == est.get("id_carrera")), None
            )
            if car:
                spinner_car.text = car["nombre"]

        scroll.add_widget(inner)
        contenido.add_widget(scroll)

        popup = Popup(
            title="Editar estudiante" if est else "Nuevo estudiante",
            content=contenido,
            size_hint=(0.95, 0.92),
        )

        def guardar(x):
            if not validar_correo(ti_mail.text):
                popup_mensaje("Error", "Correo inválido.", ROJO)
                return
            id_car = next(
                (c["id_carrera"] for c in carreras if c["nombre"] == spinner_car.text),
                None,
            )
            if not id_car:
                popup_mensaje("Error", "Selecciona una carrera.", ROJO)
                return
            datos = {
                "num_control": limpiar_texto(ti_ctrl.text),
                "nombre": limpiar_texto(ti_nom.text),
                "apellidos": limpiar_texto(ti_ape.text),
                "correo": limpiar_texto(ti_mail.text),
                "semestre": int(ti_sem.text or 1),
                "id_carrera": id_car,
            }
            try:
                if est:
                    EstudianteModel.actualizar(est["id_estudiante"], datos)
                    popup_mensaje("Listo", "Estudiante actualizado.", VERDE)
                else:
                    EstudianteModel.crear(**datos)
                    popup_mensaje("Listo", "Estudiante registrado.", VERDE)
                popup.dismiss()
                Clock.schedule_once(lambda dt: self._cargar_tabla(), 0)
            except Exception as e:
                popup_mensaje("Error", str(e), ROJO)

        btn_grd = Button(
            text="Guardar",
            background_color=VERDE,
            color=BLANCO,
            size_hint=(1, None),
            height=dp(58),
            font_size=dp(16),
        )
        btn_grd.bind(on_press=guardar)
        contenido.add_widget(btn_grd)
        popup.open()

    def ver_calificaciones(self, id_est):
        cals = EstudianteModel.calificaciones(id_est)
        est = EstudianteModel.por_id(id_est)
        contenido = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(12))
        titulo = f"Calificaciones: {est['nombre']} {est['apellidos']}"
        columnas = ["Materia", "Parcial", "Final", "Obs."]
        filas = [
            [
                c["materia"],
                f"{c['calificacion_parcial']:.1f}"
                if c["calificacion_parcial"] is not None
                else "—",
                f"{c['calificacion_final']:.1f}"
                if c["calificacion_final"] is not None
                else "—",
                c.get("observaciones") or "",
            ]
            for c in cals
        ]
        contenido.add_widget(TablaScroll(columnas, filas))
        popup = Popup(title=titulo, content=contenido, size_hint=(0.97, 0.82))
        btn = Button(
            text="Cerrar",
            size_hint=(1, None),
            height=dp(56),
            background_color=AZUL,
            color=BLANCO,
            font_size=dp(15),
        )
        btn.bind(on_press=popup.dismiss)
        contenido.add_widget(btn)
        popup.open()
