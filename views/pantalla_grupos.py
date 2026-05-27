# pantalla_grupos.py
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.graphics import Color, Rectangle
from kivy.utils import get_color_from_hex

from models.modelos import (
    GrupoModel,
    MateriaModel,
    ProfesorModel,
    AulaModel,
    PeriodoModel,
    EstudianteModel,
)
from utils.validaciones import limpiar_texto
from views.widgets import (
    BarraSuperior,
    TablaEncabezado,
    popup_confirmar,
    popup_mensaje,
    campo,
)

AZUL = get_color_from_hex("#1565C0")
VERDE = get_color_from_hex("#2E7D32")
ROJO = get_color_from_hex("#C62828")
MORADO = get_color_from_hex("#6A1B9A")
BLANCO = get_color_from_hex("#FFFFFF")
NEGRO = get_color_from_hex("#212121")


class PantallaGrupos(Screen):
    def on_pre_enter(self):
        self._build()

    def _build(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical")
        root.add_widget(BarraSuperior("Grupos", self.manager))

        acciones = BoxLayout(
            size_hint=(1, None), height=dp(62), spacing=dp(8), padding=(dp(10), dp(6))
        )
        btn_n = Button(
            text="+ Nuevo",
            background_color=VERDE,
            color=BLANCO,
            size_hint=(None, 1),
            width=dp(130),
            font_size=dp(15),
        )
        btn_n.bind(on_press=lambda x: self._form())
        acciones.add_widget(btn_n)
        root.add_widget(acciones)

        grupos = GrupoModel.todos()
        cols = [
            "Materia",
            "Profesor",
            "Aula",
            "Horario",
            "Periodo",
            "Alumnos",
            "Acciones",
        ]

        outer = BoxLayout(orientation="vertical")
        outer.add_widget(TablaEncabezado(cols))

        scroll = ScrollView()
        grid = GridLayout(cols=1, size_hint=(1, None), spacing=dp(1))
        grid.bind(minimum_height=grid.setter("height"))

        for i, g in enumerate(grupos):
            fila = BoxLayout(
                size_hint=(1, None),
                height=dp(62),
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
                g.get("materia", ""),
                g.get("profesor", ""),
                g.get("aula", ""),
                g.get("horario", ""),
                g.get("periodo", ""),
                str(g.get("num_estudiantes", 0)),
            ]:
                lbl = Label(
                    text=str(txt),
                    color=NEGRO,
                    font_size=dp(12),
                    halign="center",
                    valign="middle",
                )
                lbl.bind(size=lbl.setter("text_size"))
                fila.add_widget(lbl)

            btns = BoxLayout(spacing=dp(3), size_hint=(None, 1), width=dp(195))
            b_ins = Button(
                text="Inscribir",
                font_size=dp(13),
                background_color=MORADO,
                color=BLANCO,
            )
            b_cal = Button(
                text="Califs", font_size=dp(13), background_color=AZUL, color=BLANCO
            )
            b_del = Button(
                text="Borrar", font_size=dp(13), background_color=ROJO, color=BLANCO
            )

            gid = g["id_grupo"]
            b_ins.bind(on_press=lambda x, i=gid: self._inscribir(i))
            b_cal.bind(on_press=lambda x, i=gid: self._calificaciones(i))
            b_del.bind(
                on_press=lambda x, i=gid, gn=g.get("materia", ""): popup_confirmar(
                    "Eliminar grupo",
                    f"¿Eliminar grupo de {gn}?",
                    lambda: [
                        GrupoModel.eliminar(i),
                        Clock.schedule_once(lambda dt: self._build(), 0),
                    ],
                )
            )
            btns.add_widget(b_ins)
            btns.add_widget(b_cal)
            btns.add_widget(b_del)
            fila.add_widget(btns)
            grid.add_widget(fila)

        if not grupos:
            grid.add_widget(
                Label(
                    text="Sin grupos registrados",
                    color=NEGRO,
                    size_hint=(1, None),
                    height=dp(56),
                )
            )
        scroll.add_widget(grid)
        outer.add_widget(scroll)
        root.add_widget(outer)
        self.add_widget(root)

    def _form(self):
        materias = MateriaModel.todos()
        profesores = ProfesorModel.todos()
        aulas = AulaModel.todos()
        periodos = PeriodoModel.todos()

        contenido = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(16))
        r1, ti_hor = campo("Horario", "Lun-Mie 07:00-09:00")

        def spinner(label, items):
            lbl = Label(
                text=label,
                size_hint=(1, None),
                height=dp(28),
                color=BLANCO,
                halign="left",
                font_size=dp(15),
            )
            sp = Spinner(
                values=items,
                text=items[0] if items else "",
                size_hint=(1, None),
                height=dp(52),
                font_size=dp(14),
            )
            return lbl, sp

        lbl_m, sp_m = spinner(
            "Materia", [f"{m['clave']} - {m['nombre']}" for m in materias]
        )
        lbl_p, sp_p = spinner(
            "Profesor",
            [
                f"{p['num_empleado']} - {p['nombre']} {p['apellidos']}"
                for p in profesores
            ],
        )
        lbl_a, sp_a = spinner(
            "Aula", [f"{a['clave']} - {a['edificio']}" for a in aulas]
        )
        lbl_per, sp_per = spinner("Periodo", [pe["nombre"] for pe in periodos])

        for w in [r1, lbl_m, sp_m, lbl_p, sp_p, lbl_a, sp_a, lbl_per, sp_per]:
            contenido.add_widget(w)

        popup = Popup(title="Nuevo grupo", content=contenido, size_hint=(0.95, 0.92))

        def guardar(x):
            try:
                id_mat = materias[sp_m.values.index(sp_m.text)]["id_materia"]
                id_pro = profesores[sp_p.values.index(sp_p.text)]["id_profesor"]
                id_aul = aulas[sp_a.values.index(sp_a.text)]["id_aula"]
                id_per = periodos[sp_per.values.index(sp_per.text)]["id_periodo"]
                GrupoModel.crear(
                    limpiar_texto(ti_hor.text), id_mat, id_pro, id_aul, id_per
                )
                popup.dismiss()
                Clock.schedule_once(lambda dt: self._build(), 0)
                popup_mensaje("Listo", "Grupo creado.", VERDE)
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

    def _inscribir(self, id_grupo):
        estudiantes = EstudianteModel.todos()
        inscritos = {e["id_estudiante"] for e in GrupoModel.estudiantes(id_grupo)}
        disponibles = [e for e in estudiantes if e["id_estudiante"] not in inscritos]

        if not disponibles:
            popup_mensaje("Info", "Todos los estudiantes ya están inscritos.", AZUL)
            return

        contenido = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(16))
        lbl = Label(
            text="Selecciona estudiante:",
            size_hint=(1, None),
            height=dp(32),
            color=NEGRO,
            font_size=dp(15),
        )
        sp = Spinner(
            values=[
                f"{e['num_control']} - {e['nombre']} {e['apellidos']}"
                for e in disponibles
            ],
            text=f"{disponibles[0]['num_control']} - {disponibles[0]['nombre']} {disponibles[0]['apellidos']}",
            size_hint=(1, None),
            height=dp(52),
            font_size=dp(14),
        )
        contenido.add_widget(lbl)
        contenido.add_widget(sp)

        popup = Popup(
            title="Inscribir estudiante", content=contenido, size_hint=(0.90, 0.38)
        )

        def confirmar(x):
            idx = sp.values.index(sp.text)
            id_est = disponibles[idx]["id_estudiante"]
            try:
                GrupoModel.inscribir_estudiante(id_grupo, id_est)
                popup.dismiss()
                Clock.schedule_once(lambda dt: self._build(), 0)
                popup_mensaje("Listo", "Estudiante inscrito.", VERDE)
            except Exception as e:
                popup_mensaje("Error", str(e), ROJO)

        btn = Button(
            text="Inscribir",
            background_color=MORADO,
            color=BLANCO,
            size_hint=(1, None),
            height=dp(58),
            font_size=dp(16),
        )
        btn.bind(on_press=confirmar)
        contenido.add_widget(btn)
        popup.open()

    def _calificaciones(self, id_grupo):
        from models.modelos import CalificacionModel

        cals = CalificacionModel.por_grupo(id_grupo)

        contenido = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(12))
        scroll = ScrollView()
        grid = GridLayout(cols=1, size_hint=(1, None), spacing=dp(2))
        grid.bind(minimum_height=grid.setter("height"))

        enc = BoxLayout(size_hint=(1, None), height=dp(52))
        with enc.canvas.before:
            Color(*get_color_from_hex("#1E3A5F"))
            rect = Rectangle(size=enc.size, pos=enc.pos)
        enc.bind(
            size=lambda inst, v, r=rect: setattr(r, "size", v),
            pos=lambda inst, v, r=rect: setattr(r, "pos", v),
        )
        for t in ["Estudiante", "Parcial", "Final", "Obs"]:
            enc.add_widget(
                Label(text=f"[b]{t}[/b]", markup=True, color=BLANCO, font_size=dp(14))
            )
        grid.add_widget(enc)

        for c in cals:
            fila = BoxLayout(size_hint=(1, None), height=dp(56), spacing=dp(4))

            def _cal_str(v):
                return str(v) if v is not None else ""

            ti_p = TextInput(
                text=_cal_str(c["calificacion_parcial"]),
                input_filter="float",
                font_size=dp(14),
                multiline=False,
                size_hint=(1, 1),
            )
            ti_f = TextInput(
                text=_cal_str(c["calificacion_final"]),
                input_filter="float",
                font_size=dp(14),
                multiline=False,
                size_hint=(1, 1),
            )
            ti_o = TextInput(
                text=c.get("observaciones") or "",
                font_size=dp(13),
                multiline=False,
                size_hint=(2, 1),
            )

            lbl_e = Label(
                text=c.get("estudiante", ""),
                color=NEGRO,
                font_size=dp(13),
                size_hint=(2, 1),
            )

            btn_s = Button(
                text="💾",
                size_hint=(None, 1),
                width=dp(52),
                background_color=VERDE,
                color=BLANCO,
                font_size=dp(18),
            )
            cid = c["id_calificacion"]
            btn_s.bind(
                on_press=lambda x, cid=cid, tp=ti_p, tf=ti_f, to=ti_o: (
                    self._guardar_cal(cid, tp.text, tf.text, to.text)
                )
            )

            fila.add_widget(lbl_e)
            fila.add_widget(ti_p)
            fila.add_widget(ti_f)
            fila.add_widget(ti_o)
            fila.add_widget(btn_s)
            grid.add_widget(fila)

        scroll.add_widget(grid)
        contenido.add_widget(scroll)

        popup = Popup(
            title="Calificaciones del grupo", content=contenido, size_hint=(0.97, 0.88)
        )
        btn_c = Button(
            text="Cerrar",
            background_color=AZUL,
            color=BLANCO,
            size_hint=(1, None),
            height=dp(56),
            font_size=dp(15),
        )
        btn_c.bind(on_press=popup.dismiss)
        contenido.add_widget(btn_c)
        popup.open()

    def _guardar_cal(self, id_cal, parcial, final, obs):
        from models.modelos import CalificacionModel
        from utils.validaciones import validar_calificacion

        p = float(parcial) if validar_calificacion(parcial) else None
        f = float(final) if validar_calificacion(final) else None
        CalificacionModel.actualizar(id_cal, p, f, obs)
        popup_mensaje("Listo", "Calificación guardada.", VERDE)
