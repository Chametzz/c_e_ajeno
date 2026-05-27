import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager

from database.conexion import inicializar_bd

from views.login import LoginScreen
from views.menu_admin import MenuAdmin
from views.menu_docente import MenuDocente
from views.menu_estudiante import MenuEstudiante

from views.pantalla_estudiantes import PantallaEstudiantes
from views.pantalla_carreras import PantallaCarreras
from views.pantallas_catalogo import (
    PantallaProfesores,
    PantallaMaterias,
    PantallaAulas,
    PantallaPeriodos,
)
from views.pantalla_grupos import PantallaGrupos
from views.pantalla_calificaciones import PantallaCalificaciones
from views.pantalla_reportes import PantallaReportes


class ControlEscolarApp(App):

    # Variables de sesión accesibles desde cualquier pantalla
    rol_actual = ""
    usuario_actual = ""

    def build(self):
        inicializar_bd()

        sm = ScreenManager()

        pantallas = [
            LoginScreen(name="login"),
            MenuAdmin(name="menu_admin"),
            MenuDocente(name="menu_docente"),
            MenuEstudiante(name="menu_estudiante"),

            PantallaEstudiantes(name="estudiantes"),
            PantallaCarreras(name="carreras"),
            PantallaProfesores(name="profesores"),
            PantallaMaterias(name="materias"),
            PantallaAulas(name="aulas"),
            PantallaPeriodos(name="periodos"),
            PantallaGrupos(name="grupos"),
            PantallaCalificaciones(name="calificaciones"),
            PantallaReportes(name="reportes"),
        ]

        for p in pantallas:
            sm.add_widget(p)

        sm.current = "login"

        return sm


if __name__ == "__main__":
    ControlEscolarApp().run()
