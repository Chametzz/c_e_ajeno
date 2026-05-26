"""
main.py
Punto de entrada de la aplicación Control Escolar (Kivy).
Ejecutar con:  python main.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configurar Kivy antes de importarlo
os.environ.setdefault("KIVY_NO_ENV_CONFIG", "1")

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.utils import get_color_from_hex

from database.conexion import inicializar_bd

# Pantallas
from views.pantalla_inicio import PantallaInicio
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


# Tamaño de ventana (simula pantalla móvil en escritorio)
Window.clearcolor = get_color_from_hex("#F5F5F5")


class ControlEscolarApp(App):
    title = "Control Escolar TAP"

    def build(self):
        inicializar_bd()

        sm = ScreenManager()

        # Pantalla de inicio (debe ser la primera)
        inicio = PantallaInicio(name="inicio")
        sm.add_widget(inicio)

        # Registrar las demás pantallas
        pantallas = [
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

        # Inyectar manager en la pantalla de inicio ahora que está disponible
        inicio.manager  # accedido para forzar la referencia

        sm.current = "inicio"
        return sm


if __name__ == "__main__":
    ControlEscolarApp().run()
