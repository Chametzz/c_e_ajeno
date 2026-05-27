# pantallas_catalogo.py
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Rectangle
from kivy.utils import get_color_from_hex

from models.modelos import (
    ProfesorModel,
    MateriaModel,
    AulaModel,
    PeriodoModel,
    CarreraModel,
)
from utils.validaciones import validar_correo, validar_fecha, limpiar_texto
from views.widgets import (
    BarraSuperior,
    TablaScroll,
    TablaEncabezado,
    popup_confirmar,
    popup_mensaje,
    campo,
)

AZUL = get_color_from_hex("#1565C0")
VERDE = get_color_from_hex("#2E7D32")
ROJO = get_color_from_hex("#C62828")
BLANCO = get_color_from_hex("#FFFFFF")
NEGRO = get_color_from_hex("#212121")


def _grid_con_botones(registros, columnas_data, on_editar, on_borrar):
    outer = BoxLayout(orientation="vertical")
    outer.add_widget(TablaEncabezado(list(columnas_data.keys()) + ["Acciones"]))

    scroll = ScrollView()
    grid = GridLayout(cols=1, size_hint=(1, None), spacing=dp(1))
    grid.bind(minimum_height=grid.setter("height"))

    for i, reg in enumerate(registros):
        fila = BoxLayout(
            size_hint=(1, None), height=dp(60), spacing=dp(4), padding=(dp(4), dp(4))
        )
        bg = get_color_from_hex("#F0F4FF") if i % 2 == 0 else BLANCO
        with fila.canvas.before:
            Color(*bg)
            r = Rectangle(size=fila.size, pos=fila.pos)
        fila.bind(
            size=lambda inst, v, rect=r: setattr(rect, "size", v),
            pos=lambda inst, v, rect=r: setattr(rect, "pos", v),
        )

        for fn in columnas_data.values():
            txt = fn(reg) if callable(fn) else str(reg.get(fn, ""))
            lbl = Label(
                text=str(txt),
                color=NEGRO,
                font_size=dp(13),
                halign="center",
                valign="middle",
            )
            lbl.bind(size=lbl.setter("text_size"))
            fila.add_widget(lbl)

        btns = BoxLayout(spacing=dp(4), size_hint=(None, 1), width=dp(150))
        b_e = Button(
            text="Editar", font_size=dp(13), background_color=AZUL, color=BLANCO
        )
        b_d = Button(
            text="Borrar", font_size=dp(13), background_color=ROJO, color=BLANCO
        )
        b_e.bind(on_press=lambda x, r=reg: on_editar(r))
        b_d.bind(on_press=lambda x, r=reg: on_borrar(r))
        btns.add_widget(b_e)
        btns.add_widget(b_d)
        fila.add_widget(btns)
        grid.add_widget(fila)

    if not registros:
        grid.add_widget(
            Label(text="Sin registros", color=NEGRO, size_hint=(1, None), height=dp(50))
        )

    scroll.add_widget(grid)
    outer.add_widget(scroll)
    return outer


class PantallaProfesores(Screen):
    def on_pre_enter(self):
        self._build()

    def _build(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical")
        root.add_widget(BarraSuperior("Profesores", self.manager))

        acciones = BoxLayout(
            size_hint=(1, None), height=dp(62), spacing=dp(8), padding=(dp(10), dp(6))
        )
        btn_n = Button(
            text="+ Nuevo",
            background_color=VERDE,
            color=BLANCO,
            size_hint=(None, 1),
            width=dp(130),
        )
        btn_n.bind(on_press=lambda x: self._form())
        acciones.add_widget(btn_n)
        root.add_widget(acciones)

        profs = ProfesorModel.todos()
        cols = {
            "# Empleado": lambda r: r["num_empleado"],
            "Nombre": lambda r: f"{r['nombre']} {r['apellidos']}",
            "Especialidad": lambda r: r.get("especialidad") or "—",
        }
        root.add_widget(_grid_con_botones(profs, cols, self._form, self._borrar))
        self.add_widget(root)

    def _borrar(self, reg):
        def confirmar_eliminacion():
            try:
                ProfesorModel.eliminar(reg["id_profesor"])
                popup_mensaje("Listo", "Profesor eliminado.", VERDE)
                Clock.schedule_once(lambda dt: self._build(), 0)
            except Exception as e:
                popup_mensaje("Error", str(e), ROJO)

        popup_confirmar(
            "Eliminar",
            f"¿Eliminar a {reg['nombre']} {reg.get('apellidos', '')}?",
            confirmar_eliminacion,
        )

    def _form(self, reg=None):
        contenido = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(16))
        r1, ti_emp = campo("# Empleado", "EMP-004")
        r2, ti_nom = campo("Nombre", "Juan")
        r3, ti_ape = campo("Apellidos", "Pérez López")
        r4, ti_mail = campo("Correo", "jperez@inst.mx")
        r5, ti_esp = campo("Especialidad", "Redes")

        for w in [r1, r2, r3, r4, r5]:
            contenido.add_widget(w)

        if reg:
            ti_emp.text = reg.get("num_empleado", "")
            ti_nom.text = reg.get("nombre", "")
            ti_ape.text = reg.get("apellidos", "")
            ti_mail.text = reg.get("correo", "")
            ti_esp.text = reg.get("especialidad", "")

        popup = Popup(title="Profesor", content=contenido, size_hint=(0.9, 0.75))

        def guardar(x):
            if not validar_correo(ti_mail.text):
                popup_mensaje("Error", "Correo inválido.", ROJO)
                return
            datos = {
                "num_empleado": limpiar_texto(ti_emp.text),
                "nombre": limpiar_texto(ti_nom.text),
                "apellidos": limpiar_texto(ti_ape.text),
                "correo": limpiar_texto(ti_mail.text),
                "especialidad": limpiar_texto(ti_esp.text),
            }
            try:
                if reg:
                    ProfesorModel.actualizar(reg["id_profesor"], datos)
                else:
                    ProfesorModel.crear(**datos)
                popup.dismiss()
                self._build()
                popup_mensaje("Listo", "Guardado correctamente.", VERDE)
            except Exception as e:
                popup_mensaje("Error", str(e), ROJO)

        btn = Button(
            text="Guardar",
            background_color=VERDE,
            color=BLANCO,
            size_hint=(1, None),
            height=dp(58),
            font_size=dp(16),
        )
        btn.bind(on_press=guardar)
        contenido.add_widget(btn)
        popup.open()


class PantallaMaterias(Screen):
    def on_pre_enter(self):
        self._build()

    def _build(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical")
        root.add_widget(BarraSuperior("Materias", self.manager))

        acciones = BoxLayout(
            size_hint=(1, None), height=dp(62), spacing=dp(8), padding=(dp(10), dp(6))
        )
        btn_n = Button(
            text="+ Nueva",
            background_color=VERDE,
            color=BLANCO,
            size_hint=(None, 1),
            width=dp(130),
        )
        btn_n.bind(on_press=lambda x: self._form())
        acciones.add_widget(btn_n)
        root.add_widget(acciones)

        mats = MateriaModel.todos()
        cols = {
            "Clave": lambda r: r["clave"],
            "Nombre": lambda r: r["nombre"],
            "Créditos": lambda r: r["creditos"],
            "Semestre": lambda r: r["semestre"],
            "Carrera": lambda r: r.get("carrera", ""),
        }
        root.add_widget(_grid_con_botones(mats, cols, self._form, self._borrar))
        self.add_widget(root)

    def _borrar(self, reg):
        def confirmar_eliminacion():
            try:
                MateriaModel.eliminar(reg["id_materia"])
                popup_mensaje("Listo", "materia eliminada.", VERDE)
                Clock.schedule_once(lambda dt: self._build(), 0)
            except Exception as e:
                popup_mensaje("Error", str(e), ROJO)

        popup_confirmar(
            "Eliminar", f"¿Eliminar a {reg['nombre']}?", confirmar_eliminacion
        )

    def _form(self, reg=None):
        carreras = CarreraModel.todos()
        contenido = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(16))
        r1, ti_clave = campo("Clave", "SC-403")
        r2, ti_nom = campo("Nombre", "Estructuras de Datos")
        r3, ti_cred = campo("Créditos", "5", input_filter="int")
        r4, ti_sem = campo("Semestre", "4", input_filter="int")

        lbl_c = Label(
            text="Carrera",
            size_hint=(1, None),
            height=dp(28),
            color=BLANCO,
            halign="left",
        )
        sp_c = Spinner(
            values=[c["nombre"] for c in carreras],
            text=carreras[0]["nombre"] if carreras else "",
            size_hint=(1, None),
            height=dp(52),
            font_size=dp(14),
        )

        for w in [r1, r2, r3, r4, lbl_c, sp_c]:
            contenido.add_widget(w)

        if reg:
            ti_clave.text = reg.get("clave", "")
            ti_nom.text = reg.get("nombre", "")
            ti_cred.text = str(reg.get("creditos", ""))
            ti_sem.text = str(reg.get("semestre", ""))
            car = next(
                (c for c in carreras if c["id_carrera"] == reg.get("id_carrera")), None
            )
            if car:
                sp_c.text = car["nombre"]

        popup = Popup(title="Materia", content=contenido, size_hint=(0.9, 0.82))

        def guardar(x):
            id_car = next(
                (c["id_carrera"] for c in carreras if c["nombre"] == sp_c.text), None
            )
            if not id_car:
                popup_mensaje("Error", "Selecciona una carrera.", ROJO)
                return
            datos = {
                "clave": limpiar_texto(ti_clave.text),
                "nombre": limpiar_texto(ti_nom.text),
                "creditos": int(ti_cred.text or 0),
                "semestre": int(ti_sem.text or 1),
                "id_carrera": id_car,
            }
            try:
                if reg:
                    MateriaModel.actualizar(reg["id_materia"], datos)
                else:
                    MateriaModel.crear(**datos)
                popup.dismiss()
                self._build()
                popup_mensaje("Listo", "Guardado.", VERDE)
            except Exception as e:
                popup_mensaje("Error", str(e), ROJO)

        btn = Button(
            text="Guardar",
            background_color=VERDE,
            color=BLANCO,
            size_hint=(1, None),
            height=dp(58),
            font_size=dp(16),
        )
        btn.bind(on_press=guardar)
        contenido.add_widget(btn)
        popup.open()


class PantallaAulas(Screen):
    def on_pre_enter(self):
        self._build()

    def _build(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical")
        root.add_widget(BarraSuperior("Aulas", self.manager))

        acciones = BoxLayout(
            size_hint=(1, None), height=dp(62), spacing=dp(8), padding=(dp(10), dp(6))
        )
        btn_n = Button(
            text="+ Nueva",
            background_color=VERDE,
            color=BLANCO,
            size_hint=(None, 1),
            width=dp(130),
        )
        btn_n.bind(on_press=lambda x: self._form())
        acciones.add_widget(btn_n)
        root.add_widget(acciones)

        aulas = AulaModel.todos()
        cols = {
            "Clave": lambda r: r["clave"],
            "Edificio": lambda r: r["edificio"],
            "Capacidad": lambda r: r["capacidad"],
            "Tipo": lambda r: r["tipo"],
        }
        root.add_widget(_grid_con_botones(aulas, cols, self._form, self._borrar))
        self.add_widget(root)

    def _borrar(self, reg):
        def confirmar():
            try:
                AulaModel.eliminar(reg["id_aula"])
                popup_mensaje("Listo", "Aula eliminada.", VERDE)
                Clock.schedule_once(lambda dt: self._build(), 0)
            except Exception as e:
                popup_mensaje("Error", str(e), ROJO)

        popup_confirmar("Eliminar", f"¿Eliminar aula {reg['clave']}?", confirmar)

    def _form(self, reg=None):
        contenido = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(16))
        r1, ti_clave = campo("Clave", "A-102")
        r2, ti_edif = campo("Edificio", "Edificio A")
        r3, ti_cap = campo("Capacidad", "35", input_filter="int")

        lbl_t = Label(
            text="Tipo",
            size_hint=(1, None),
            height=dp(28),
            color=BLANCO,
            halign="left",
            font_size=dp(15),
        )
        sp_t = Spinner(
            values=["salon", "laboratorio", "taller", "auditorio"],
            text="salon",
            size_hint=(1, None),
            height=dp(52),
            font_size=dp(14),
        )

        for w in [r1, r2, r3, lbl_t, sp_t]:
            contenido.add_widget(w)

        if reg:
            ti_clave.text = reg.get("clave", "")
            ti_edif.text = reg.get("edificio", "")
            ti_cap.text = str(reg.get("capacidad", ""))
            sp_t.text = reg.get("tipo", "salon")

        popup = Popup(title="Aula", content=contenido, size_hint=(0.88, 0.72))

        def guardar(x):
            datos = {
                "clave": limpiar_texto(ti_clave.text),
                "edificio": limpiar_texto(ti_edif.text),
                "capacidad": int(ti_cap.text or 0),
                "tipo": sp_t.text,
            }
            try:
                if reg:
                    AulaModel.actualizar(reg["id_aula"], datos)
                else:
                    AulaModel.crear(**datos)
                popup.dismiss()
                self._build()
                popup_mensaje("Listo", "Guardado.", VERDE)
            except Exception as e:
                popup_mensaje("Error", str(e), ROJO)

        btn = Button(
            text="Guardar",
            background_color=VERDE,
            color=BLANCO,
            size_hint=(1, None),
            height=dp(58),
            font_size=dp(16),
        )
        btn.bind(on_press=guardar)
        contenido.add_widget(btn)
        popup.open()


class PantallaPeriodos(Screen):
    def on_pre_enter(self):
        self._build()

    def _build(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical")
        root.add_widget(BarraSuperior("Periodos Semestrales", self.manager))

        acciones = BoxLayout(
            size_hint=(1, None), height=dp(62), spacing=dp(8), padding=(dp(10), dp(6))
        )
        btn_n = Button(
            text="+ Nuevo",
            background_color=VERDE,
            color=BLANCO,
            size_hint=(None, 1),
            width=dp(130),
        )
        btn_n.bind(on_press=lambda x: self._form())
        acciones.add_widget(btn_n)
        root.add_widget(acciones)

        periodos = PeriodoModel.todos()
        cols = {
            "Nombre": lambda r: r["nombre"],
            "Inicio": lambda r: r["fecha_inicio"],
            "Fin": lambda r: r["fecha_fin"],
            "Estado": lambda r: r["estado"],
        }
        root.add_widget(_grid_con_botones(periodos, cols, self._form, self._borrar))
        self.add_widget(root)

    def _borrar(self, reg):
        def confirmar():
            try:
                PeriodoModel.eliminar(reg["id_periodo"])
                popup_mensaje("Listo", "periodo eliminado.", VERDE)
                Clock.schedule_once(lambda dt: self._build(), 0)
            except Exception as e:
                popup_mensaje("Error", str(e), ROJO)

        popup_confirmar("Eliminar", f"¿Eliminar periodo {reg['nombre']}?", confirmar)

    def _form(self, reg=None):
        contenido = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(16))
        r1, ti_nom = campo("Nombre", "Agosto-Diciembre 2026")
        r2, ti_ini = campo("Fecha inicio", "2026-08-10")
        r3, ti_fin = campo("Fecha fin", "2026-12-18")

        lbl_e = Label(
            text="Estado",
            size_hint=(1, None),
            height=dp(28),
            color=BLANCO,
            halign="left",
        )
        sp_e = Spinner(
            values=["activo", "cerrado", "pendiente"],
            text="activo",
            size_hint=(1, None),
            height=dp(52),
            font_size=dp(14),
        )

        for w in [r1, r2, r3, lbl_e, sp_e]:
            contenido.add_widget(w)

        if reg:
            ti_nom.text = reg.get("nombre", "")
            ti_ini.text = reg.get("fecha_inicio", "")
            ti_fin.text = reg.get("fecha_fin", "")
            sp_e.text = reg.get("estado", "activo")

        popup = Popup(
            title="Periodo semestral", content=contenido, size_hint=(0.9, 0.72)
        )

        def guardar(x):
            if not (validar_fecha(ti_ini.text) and validar_fecha(ti_fin.text)):
                popup_mensaje("Error", "Fechas inválidas. Usa YYYY-MM-DD.", ROJO)
                return
            datos = {
                "nombre": limpiar_texto(ti_nom.text),
                "fecha_inicio": ti_ini.text,
                "fecha_fin": ti_fin.text,
                "estado": sp_e.text,
            }
            try:
                if reg:
                    PeriodoModel.actualizar(reg["id_periodo"], datos)
                else:
                    PeriodoModel.crear(**datos)
                popup.dismiss()
                self._build()
                popup_mensaje("Listo", "Guardado.", VERDE)
            except Exception as e:
                popup_mensaje("Error", str(e), ROJO)

        btn = Button(
            text="Guardar",
            background_color=VERDE,
            color=BLANCO,
            size_hint=(1, None),
            height=dp(58),
            font_size=dp(16),
        )
        btn.bind(on_press=guardar)
        contenido.add_widget(btn)
        popup.open()
