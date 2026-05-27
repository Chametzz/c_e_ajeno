"""
views/pantalla_reportes.py
Reportes básicos del sistema de control escolar.
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout     import BoxLayout
from kivy.uix.scrollview    import ScrollView
from kivy.uix.button        import Button
from kivy.uix.label         import Label
from kivy.uix.spinner       import Spinner
from kivy.uix.popup         import Popup
from kivy.utils             import get_color_from_hex

from models.modelos import (EstudianteModel, GrupoModel, CalificacionModel,
                             ProfesorModel, CarreraModel, MateriaModel)
from views.widgets  import (BarraSuperior, TablaScroll, popup_mensaje)

AZUL   = get_color_from_hex("#1565C0")
VERDE  = get_color_from_hex("#2E7D32")
BLANCO = get_color_from_hex("#FFFFFF")
NEGRO  = get_color_from_hex("#212121")


class PantallaReportes(Screen):
    def on_pre_enter(self): self._build()

    def _build(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical")
        root.add_widget(BarraSuperior("Reportes", self.manager))

        scroll = ScrollView()
        menu   = BoxLayout(orientation="vertical", spacing=14,
                           padding=(20, 20), size_hint=(1, None))
        menu.bind(minimum_height=menu.setter("height"))

        reportes = [
            ("📋  Todas las calificaciones",      self._rep_calificaciones),
            ("👥  Estudiantes por grupo",          self._rep_est_grupo),
            ("📚  Materias por carrera",           self._rep_mat_carrera),
            ("👨‍🏫  Grupos por profesor",           self._rep_grupos_prof),
            ("🏆  Promedio general por materia",  self._rep_promedios),
        ]

        for texto, fn in reportes:
            btn = Button(
                text=texto, size_hint=(1, None), height=64,
                background_color=AZUL, color=BLANCO, font_size=16,
            )
            btn.bind(on_press=lambda x, f=fn: f())
            menu.add_widget(btn)

        scroll.add_widget(menu)
        root.add_widget(scroll)
        self.add_widget(root)

    # ── Reporte 1: todas las calificaciones ────────
    def _rep_calificaciones(self):
        datos = CalificacionModel.todas()
        cols  = ["Estudiante", "Materia", "Profesor", "Parcial", "Final", "Periodo"]
        filas = [
            [d.get("estudiante",""), d.get("materia",""), d.get("profesor",""),
             f"{d['calificacion_parcial']:.1f}" if d.get("calificacion_parcial") is not None else "—",
             f"{d['calificacion_final']:.1f}"   if d.get("calificacion_final")   is not None else "—",
             d.get("periodo","")]
            for d in datos
        ]
        self._popup_tabla("Todas las calificaciones", cols, filas)

    # ── Reporte 2: estudiantes por grupo ───────────
    def _rep_est_grupo(self):
        grupos = GrupoModel.todos()
        if not grupos:
            popup_mensaje("Info", "No hay grupos registrados.", AZUL); return

        contenido = BoxLayout(orientation="vertical", spacing=12, padding=16)
        lbl = Label(text="Selecciona grupo:", size_hint=(1, None),
                    height=32, color=NEGRO, font_size=15)
        sp  = Spinner(
            values=[f"{g['id_grupo']} | {g.get('materia','')} - {g.get('horario','')}"
                    for g in grupos],
            text="", size_hint=(1, None), height=52, font_size=14,
        )
        if grupos: sp.text = sp.values[0]
        contenido.add_widget(lbl)
        contenido.add_widget(sp)

        popup = Popup(title="Reporte por grupo", content=contenido,
                      size_hint=(0.92, 0.38))

        def ver(x):
            idx    = sp.values.index(sp.text)
            id_grp = grupos[idx]["id_grupo"]
            ests   = GrupoModel.estudiantes(id_grp)
            cols   = ["# Control", "Estudiante"]
            filas  = [[e["num_control"], e["estudiante"]] for e in ests]
            popup.dismiss()
            self._popup_tabla(f"Estudiantes: {grupos[idx].get('materia','')}", cols, filas)

        btn = Button(text="Ver reporte", background_color=AZUL, color=BLANCO,
                     size_hint=(1, None), height=56, font_size=15)
        btn.bind(on_press=ver)
        contenido.add_widget(btn)
        popup.open()

    # ── Reporte 3: materias por carrera ────────────
    def _rep_mat_carrera(self):
        carreras = CarreraModel.todos()
        if not carreras:
            popup_mensaje("Info", "No hay carreras.", AZUL); return

        contenido = BoxLayout(orientation="vertical", spacing=12, padding=16)
        lbl = Label(text="Selecciona carrera:", size_hint=(1, None),
                    height=32, color=NEGRO, font_size=15)
        sp  = Spinner(values=[c["nombre"] for c in carreras],
                      text=carreras[0]["nombre"] if carreras else "",
                      size_hint=(1, None), height=52, font_size=14)
        contenido.add_widget(lbl)
        contenido.add_widget(sp)

        popup = Popup(title="Materias por carrera", content=contenido,
                      size_hint=(0.92, 0.36))

        def ver(x):
            idx    = sp.values.index(sp.text)
            id_car = carreras[idx]["id_carrera"]
            mats   = MateriaModel.por_carrera(id_car)
            cols   = ["Clave", "Materia", "Créditos", "Semestre"]
            filas  = [[m["clave"], m["nombre"], m["creditos"], m["semestre"]] for m in mats]
            popup.dismiss()
            self._popup_tabla(f"Materias: {sp.text}", cols, filas)

        btn = Button(text="Ver reporte", background_color=AZUL, color=BLANCO,
                     size_hint=(1, None), height=56, font_size=15)
        btn.bind(on_press=ver)
        contenido.add_widget(btn)
        popup.open()

    # ── Reporte 4: grupos por profesor ─────────────
    def _rep_grupos_prof(self):
        profs = ProfesorModel.todos()
        if not profs:
            popup_mensaje("Info", "No hay profesores.", AZUL); return

        contenido = BoxLayout(orientation="vertical", spacing=12, padding=16)
        lbl = Label(text="Selecciona profesor:", size_hint=(1, None),
                    height=32, color=NEGRO, font_size=15)
        sp  = Spinner(
            values=[f"{p['nombre']} {p['apellidos']}" for p in profs],
            text=f"{profs[0]['nombre']} {profs[0]['apellidos']}" if profs else "",
            size_hint=(1, None), height=52, font_size=14,
        )
        contenido.add_widget(lbl)
        contenido.add_widget(sp)

        popup = Popup(title="Grupos por profesor", content=contenido,
                      size_hint=(0.92, 0.36))

        def ver(x):
            idx     = sp.values.index(sp.text)
            id_pr   = profs[idx]["id_profesor"]
            horario = ProfesorModel.horario(id_pr)
            cols    = ["Materia", "Aula", "Horario", "Periodo"]
            filas   = [[h.get("materia",""), h.get("aula",""),
                        h.get("horario",""), h.get("periodo","")] for h in horario]
            popup.dismiss()
            self._popup_tabla(f"Grupos de {sp.text}", cols, filas)

        btn = Button(text="Ver reporte", background_color=AZUL, color=BLANCO,
                     size_hint=(1, None), height=56, font_size=15)
        btn.bind(on_press=ver)
        contenido.add_widget(btn)
        popup.open()

    # ── Reporte 5: promedio por materia ────────────
    def _rep_promedios(self):
        from database.conexion import get_connection
        with get_connection() as conn:
            rows = conn.execute("""
                SELECT m.nombre AS materia,
                       ROUND(AVG(c.calificacion_final), 2) AS promedio,
                       COUNT(c.id_calificacion) AS total
                FROM calificacion c
                JOIN grupo_estudiante ge ON ge.id_grupo_est = c.id_grupo_est
                JOIN grupo g ON g.id_grupo = ge.id_grupo
                JOIN materia m ON m.id_materia = g.id_materia
                WHERE c.calificacion_final IS NOT NULL
                GROUP BY m.id_materia
                ORDER BY promedio DESC
            """).fetchall()
            datos = [dict(r) for r in rows]

        cols  = ["Materia", "Promedio final", "Estudiantes evaluados"]
        filas = [[d["materia"], f"{d['promedio']:.2f}", d["total"]] for d in datos]
        self._popup_tabla("Promedio general por materia", cols, filas)

    # ── Popup genérico de tabla ────────────────────
    def _popup_tabla(self, titulo, cols, filas):
        contenido = BoxLayout(orientation="vertical", spacing=8, padding=12)
        contenido.add_widget(TablaScroll(cols, filas))
        popup = Popup(title=titulo, content=contenido, size_hint=(0.97, 0.88))
        btn = Button(text="Cerrar", background_color=AZUL, color=BLANCO,
                     size_hint=(1, None), height=56, font_size=15)
        btn.bind(on_press=popup.dismiss)
        contenido.add_widget(btn)
        popup.open()
