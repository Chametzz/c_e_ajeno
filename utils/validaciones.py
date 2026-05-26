"""
utils/validaciones.py
Funciones de validación y formateo reutilizables.
"""
import re


def validar_correo(correo: str) -> bool:
    return bool(re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", correo))


def validar_fecha(fecha: str) -> bool:
    """Valida formato YYYY-MM-DD."""
    return bool(re.match(r"^\d{4}-\d{2}-\d{2}$", fecha))


def validar_calificacion(valor) -> bool:
    try:
        v = float(valor)
        return 0 <= v <= 100
    except (ValueError, TypeError):
        return False


def formatear_nombre(nombre: str, apellidos: str) -> str:
    return f"{nombre.strip().title()} {apellidos.strip().title()}"


def limpiar_texto(texto: str) -> str:
    return texto.strip()


def calificacion_a_letra(cal: float) -> str:
    if cal >= 90: return "A"
    if cal >= 80: return "B"
    if cal >= 70: return "C"
    if cal >= 60: return "D"
    return "F"
