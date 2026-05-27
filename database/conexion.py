import sqlite3
import os

DB_NAME = "control_escolar.db"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(os.path.dirname(BASE_DIR), DB_NAME)


def conectar():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def inicializar_bd():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT UNIQUE,
        password TEXT,
        rol TEXT
    )
    ''')

    usuarios = [
        ("admin", "123", "admin"),
        ("docente", "123", "docente"),
        ("estudiante", "123", "estudiante")
    ]

    for u in usuarios:
        try:
            cursor.execute(
                "INSERT INTO usuarios(usuario, password, rol) VALUES(?,?,?)",
                u
            )
        except:
            pass

    conn.commit()
    conn.close()
