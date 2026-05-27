"""
views/pantalla_carreras.py
CRUD completo de carreras con visualización de sus materias.
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout     import BoxLayout
from kivy.uix.scrollview    import ScrollView
from kivy.uix.gridlayout    import GridLayout
from kivy.uix.button        import Button
from kivy.uix.label         import Label
from kivy.uix.popup         import Popup
from kivy.graphics          import Color, Rectangle
from kivy.utils             import get_color_from_hex
from kivy.clock             import Clock

from models.modelos     import CarreraModel, MateriaModel
from utils.validaciones import limpiar_texto
from views.widgets      import (BarraSuperior, TablaEncabezado, TablaScroll,
                                 popup_confirmar, popup_mensaje, campo)

AZUL   = get_color_from_hex("#1565C0")
VERDE  = get_color_from_hex("#2E7D32")
ROJO   = get_color_from_hex("#C62828")
MORADO = get_color_from_hex("#6A1B9A")
BLANCO = get_color_from_hex("#FFFFFF")
NEGRO  = get_color_from_hex("#212121")


class PantallaCarreras(Screen):

    def on_pre_enter(self):
        self._build()

    def _build(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical")
        root.add_widget(BarraSuperior("Carreras", self.manager))

        acciones = BoxLayout(size_hint=(1, None), height=62, spacing=8, padding=(10, 6))
        btn_n = Button(text="+ Nueva", background_color=VERDE, color=BLANCO,
                       size_hint=(None, 1), width=130, font_size=15)
        btn_n.bind(on_press=lambda x: self._form())
        acciones.add_widget(btn_n)
        root.add_widget(acciones)

        carreras       = CarreraModel.todos()
        todas_materias = MateriaModel.todos()
        conteo = {}
        for m in todas_materias:
            cid = m["id_carrera"]
            conteo[cid] = conteo.get(cid, 0) + 1

        cols = ["Clave", "Nombre", "Descripción", "Materias", "Acciones"]
        outer = BoxLayout(orientation="vertical")
        outer.add_widget(TablaEncabezado(cols))

        scroll = ScrollView()
        grid   = GridLayout(cols=1, size_hint=(1, None), spacing=1)
        grid.bind(minimum_height=grid.setter("height"))

        for i, car in enumerate(carreras):
            fila = BoxLayout(size_hint=(1, None), height=62, spacing=4, padding=(4, 4))
            bg = get_color_from_hex("#F0F4FF") if i % 2 == 0 else BLANCO
            with fila.canvas.before:
                Color(*bg)
                rect = Rectangle(size=fila.size, pos=fila.pos)
            fila.bind(
                size=lambda inst, v, r=rect: setattr(r, "size", v),
                pos =lambda inst, v, r=rect: setattr(r, "pos",  v),
            )

            num_mat = conteo.get(car["id_carrera"], 0)
            badge   = f"{num_mat} {'materia' if num_mat == 1 else 'materias'}"

            for txt in [car["clave"], car["nombre"],
                        car.get("descripcion") or "—", badge]:
                lbl = Label(text=str(txt), color=NEGRO, font_size=13,
                            halign="center", valign="middle")
                lbl.bind(size=lbl.setter("text_size"))
                fila.add_widget(lbl)

            btns = BoxLayout(spacing=3, size_hint=(None, 1), width=210)
            b_edit = Button(text="Editar",   font_size=13, background_color=AZUL,   color=BLANCO)
            b_mat  = Button(text="Materias", font_size=13, background_color=MORADO, color=BLANCO)
            b_del  = Button(text="Borrar",   font_size=13, background_color=ROJO,   color=BLANCO)

            b_edit.bind(on_press=lambda x, c=car: self._form(c))
            b_mat.bind( on_press=lambda x, c=car: self._ver_materias(c))
            b_del.bind( on_press=lambda x, c=car: self._borrar(c))

            btns.add_widget(b_edit)
            btns.add_widget(b_mat)
            btns.add_widget(b_del)
            fila.add_widget(btns)
            grid.add_widget(fila)

        if not carreras:
            grid.add_widget(Label(text="Sin carreras registradas",
                                  color=NEGRO, size_hint=(1, None), height=56))

        scroll.add_widget(grid)
        outer.add_widget(scroll)
        root.add_widget(outer)
        self.add_widget(root)

    def _form(self, reg=None):
        contenido = BoxLayout(orientation="vertical", spacing=8, padding=16)
        scroll = ScrollView()
        inner  = BoxLayout(orientation="vertical", size_hint=(1, None), spacing=8)
        inner.bind(minimum_height=inner.setter("height"))

        r1, ti_clave = campo("Clave *",       "Ej: ISC, IIA, LCDE")
        r2, ti_nom   = campo("Nombre *",      "Ing. en Sistemas Computacionales")
        r3, ti_desc  = campo("Descripción",   "Carrera orientada a...", multiline=True)

        for w in [r1, r2, r3]:
            inner.add_widget(w)

        if reg:
            ti_clave.text = reg.get("clave", "")
            ti_nom.text   = reg.get("nombre", "")
            ti_desc.text  = reg.get("descripcion", "")

        scroll.add_widget(inner)
        contenido.add_widget(scroll)

        popup = Popup(
            title="Editar carrera" if reg else "Nueva carrera",
            content=contenido, size_hint=(0.95, 0.72),
        )

        def guardar(x):
            clave  = limpiar_texto(ti_clave.text)
            nombre = limpiar_texto(ti_nom.text)
            if not clave:
                popup_mensaje("Error", "La clave es obligatoria.", ROJO); return
            if not nombre:
                popup_mensaje("Error", "El nombre es obligatorio.", ROJO); return
            datos = {
                "clave":       clave,
                "nombre":      nombre,
                "descripcion": limpiar_texto(ti_desc.text),
            }
            try:
                if reg:
                    CarreraModel.actualizar(reg["id_carrera"], datos)
                    msg = "Carrera actualizada correctamente."
                else:
                    CarreraModel.crear(**datos)
                    msg = "Carrera registrada correctamente."
                popup.dismiss()
                Clock.schedule_once(lambda dt: self._build(), 0)
                popup_mensaje("Listo", msg, VERDE)
            except Exception as e:
                popup_mensaje("Error", str(e), ROJO)

        btn_grd = Button(text="Guardar", background_color=VERDE, color=BLANCO,
                         size_hint=(1, None), height=58, font_size=16)
        btn_grd.bind(on_press=guardar)
        contenido.add_widget(btn_grd)
        popup.open()

    def _borrar(self, reg):
        def confirmar():
            try:
                CarreraModel.eliminar(reg["id_carrera"])
                popup_mensaje("Listo", "Carrera eliminada.", VERDE)
                Clock.schedule_once(lambda dt: self._build(), 0)
            except Exception as e:
                popup_mensaje("No se puede eliminar",
                              f"Esta carrera tiene materias o estudiantes asociados.\nDetalle: {e}",
                              ROJO)

        popup_confirmar("Eliminar carrera",
                        f"¿Eliminar '{reg['nombre']}'?\nEsta acción no se puede deshacer.",
                        confirmar)

    def _ver_materias(self, car):
        mats  = MateriaModel.por_carrera(car["id_carrera"])
        cols  = ["Clave", "Nombre", "Créditos", "Semestre"]
        filas = [[m["clave"], m["nombre"], str(m["creditos"]), str(m["semestre"])]
                 for m in mats]

        contenido = BoxLayout(orientation="vertical", spacing=8, padding=12)
        contenido.add_widget(TablaScroll(cols, filas))

        popup = Popup(title=f"Materias — {car['nombre']}",
                      content=contenido, size_hint=(0.97, 0.84))
        btn_c = Button(text="Cerrar", background_color=AZUL, color=BLANCO,
                       size_hint=(1, None), height=56, font_size=15)
        btn_c.bind(on_press=popup.dismiss)
        contenido.add_widget(btn_c)
        popup.open()
