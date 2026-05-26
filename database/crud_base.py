"""
database/crud_base.py
Operaciones CRUD genéricas sobre cualquier tabla.
"""
from database.conexion import get_connection


def insertar(tabla: str, datos: dict) -> int:
    cols = ", ".join(datos.keys())
    placeholders = ", ".join(["?"] * len(datos))
    sql = f"INSERT INTO {tabla} ({cols}) VALUES ({placeholders})"
    with get_connection() as conn:
        cur = conn.execute(sql, list(datos.values()))
        return cur.lastrowid


def obtener_todos(tabla: str) -> list:
    with get_connection() as conn:
        rows = conn.execute(f"SELECT * FROM {tabla}").fetchall()
        return [dict(r) for r in rows]


def obtener_por_id(tabla: str, pk: str, valor) -> dict | None:
    with get_connection() as conn:
        row = conn.execute(f"SELECT * FROM {tabla} WHERE {pk} = ?", (valor,)).fetchone()
        return dict(row) if row else None


def actualizar(tabla: str, datos: dict, pk: str, valor) -> int:
    sets = ", ".join([f"{k} = ?" for k in datos.keys()])
    sql = f"UPDATE {tabla} SET {sets} WHERE {pk} = ?"
    with get_connection() as conn:
        cur = conn.execute(sql, [*datos.values(), valor])
        return cur.rowcount


def eliminar(tabla: str, pk: str, valor) -> int:
    with get_connection() as conn:
        cur = conn.execute(f"DELETE FROM {tabla} WHERE {pk} = ?", (valor,))
        return cur.rowcount


def buscar(tabla: str, campo: str, valor) -> list:
    with get_connection() as conn:
        rows = conn.execute(
            f"SELECT * FROM {tabla} WHERE {campo} LIKE ?", (f"%{valor}%",)
        ).fetchall()
        return [dict(r) for r in rows]


def ejecutar_vista(vista: str) -> list:
    with get_connection() as conn:
        rows = conn.execute(f"SELECT * FROM {vista}").fetchall()
        return [dict(r) for r in rows]
