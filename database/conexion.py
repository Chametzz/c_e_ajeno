"""
database/conexion.py
Gestión de la conexión a SQLite y creación del esquema.
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "control_escolar.db")
SQL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "control_escolar.sql")


def get_connection() -> sqlite3.Connection:
    """Devuelve una conexión con row_factory y FK activadas."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def inicializar_bd():
    """Crea las tablas e inserta datos de prueba si no existen."""
    if not os.path.exists(DB_PATH):
        if os.path.exists(SQL_PATH):
            with get_connection() as conn:
                with open(SQL_PATH, "r", encoding="utf-8") as f:
                    conn.executescript(f.read())
            print("[BD] Base de datos creada desde control_escolar.sql")
        else:
            print("[BD] ADVERTENCIA: no se encontró control_escolar.sql")
    else:
        print("[BD] Base de datos ya existe, omitiendo inicialización.")
