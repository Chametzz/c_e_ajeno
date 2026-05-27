"""
models/modelos.py
Lógica de negocio y validaciones por entidad.
"""
from database.crud_base import (
    insertar, obtener_todos, obtener_por_id,
    actualizar, eliminar, buscar, ejecutar_vista
)
from database.conexion import get_connection


# ─────────────────────────────────────────
#  CARRERA
# ─────────────────────────────────────────
class CarreraModel:
    TABLA = "carrera"
    PK    = "id_carrera"

    @staticmethod
    def crear(clave, nombre, descripcion=""):
        return insertar(CarreraModel.TABLA, {"clave": clave, "nombre": nombre, "descripcion": descripcion})

    @staticmethod
    def todos():
        return obtener_todos(CarreraModel.TABLA)

    @staticmethod
    def por_id(id_carrera):
        return obtener_por_id(CarreraModel.TABLA, CarreraModel.PK, id_carrera)

    @staticmethod
    def actualizar(id_carrera, datos):
        return actualizar(CarreraModel.TABLA, datos, CarreraModel.PK, id_carrera)

    @staticmethod
    def eliminar(id_carrera):
        return eliminar(CarreraModel.TABLA, CarreraModel.PK, id_carrera)


# ─────────────────────────────────────────
#  MATERIA
# ─────────────────────────────────────────
class MateriaModel:
    TABLA = "materia"
    PK    = "id_materia"

    @staticmethod
    def crear(clave, nombre, creditos, semestre, id_carrera):
        return insertar(MateriaModel.TABLA, {
            "clave": clave, "nombre": nombre,
            "creditos": creditos, "semestre": semestre,
            "id_carrera": id_carrera
        })

    @staticmethod
    def todos():
        with get_connection() as conn:
            rows = conn.execute("""
                SELECT m.*, c.nombre AS carrera
                FROM materia m
                JOIN carrera c ON c.id_carrera = m.id_carrera
            """).fetchall()
            return [dict(r) for r in rows]

    @staticmethod
    def por_id(id_materia):
        return obtener_por_id(MateriaModel.TABLA, MateriaModel.PK, id_materia)

    @staticmethod
    def por_carrera(id_carrera):
        with get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM materia WHERE id_carrera = ?", (id_carrera,)
            ).fetchall()
            return [dict(r) for r in rows]

    @staticmethod
    def actualizar(id_materia, datos):
        return actualizar(MateriaModel.TABLA, datos, MateriaModel.PK, id_materia)

    @staticmethod
    def eliminar(id_materia):
        return eliminar(MateriaModel.TABLA, MateriaModel.PK, id_materia)


# ─────────────────────────────────────────
#  PROFESOR
# ─────────────────────────────────────────
class ProfesorModel:
    TABLA = "profesor"
    PK    = "id_profesor"

    @staticmethod
    def crear(num_empleado, nombre, apellidos, correo, especialidad=""):
        return insertar(ProfesorModel.TABLA, {
            "num_empleado": num_empleado, "nombre": nombre,
            "apellidos": apellidos, "correo": correo,
            "especialidad": especialidad
        })

    @staticmethod
    def todos():
        return obtener_todos(ProfesorModel.TABLA)

    @staticmethod
    def por_id(id_profesor):
        return obtener_por_id(ProfesorModel.TABLA, ProfesorModel.PK, id_profesor)

    @staticmethod
    def buscar_nombre(texto):
        return buscar(ProfesorModel.TABLA, "nombre", texto)

    @staticmethod
    def actualizar(id_profesor, datos):
        return actualizar(ProfesorModel.TABLA, datos, ProfesorModel.PK, id_profesor)

    @staticmethod
    def eliminar(id_profesor):
        return eliminar(ProfesorModel.TABLA, ProfesorModel.PK, id_profesor)

    @staticmethod
    def horario(id_profesor):
        with get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM v_horario_profesor
                WHERE num_empleado = (
                    SELECT num_empleado FROM profesor WHERE id_profesor = ?
                )
            """, (id_profesor,)).fetchall()
            return [dict(r) for r in rows]


# ─────────────────────────────────────────
#  ESTUDIANTE
# ─────────────────────────────────────────
class EstudianteModel:
    TABLA = "estudiante"
    PK    = "id_estudiante"

    @staticmethod
    def crear(num_control, nombre, apellidos, correo, semestre, id_carrera):
        return insertar(EstudianteModel.TABLA, {
            "num_control": num_control, "nombre": nombre,
            "apellidos": apellidos, "correo": correo,
            "semestre": semestre, "id_carrera": id_carrera
        })

    @staticmethod
    def todos():
        with get_connection() as conn:
            rows = conn.execute("""
                SELECT e.*, c.nombre AS carrera
                FROM estudiante e
                JOIN carrera c ON c.id_carrera = e.id_carrera
            """).fetchall()
            return [dict(r) for r in rows]

    @staticmethod
    def por_id(id_estudiante):
        return obtener_por_id(EstudianteModel.TABLA, EstudianteModel.PK, id_estudiante)

    @staticmethod
    def buscar_nombre(texto):
        with get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM estudiante WHERE nombre LIKE ? OR apellidos LIKE ? OR num_control LIKE ?",
                (f"%{texto}%", f"%{texto}%", f"%{texto}%")
            ).fetchall()
            return [dict(r) for r in rows]

    @staticmethod
    def actualizar(id_estudiante, datos):
        return actualizar(EstudianteModel.TABLA, datos, EstudianteModel.PK, id_estudiante)

    @staticmethod
    def eliminar(id_estudiante):
        return eliminar(EstudianteModel.TABLA, EstudianteModel.PK, id_estudiante)

    @staticmethod
    def calificaciones(id_estudiante):
        with get_connection() as conn:
            rows = conn.execute("""
                SELECT c.*, m.nombre AS materia, g.horario, ps.nombre AS periodo
                FROM calificacion c
                JOIN grupo_estudiante ge ON ge.id_grupo_est = c.id_grupo_est
                JOIN grupo g ON g.id_grupo = ge.id_grupo
                JOIN materia m ON m.id_materia = g.id_materia
                JOIN periodo_semestral ps ON ps.id_periodo = g.id_periodo
                WHERE ge.id_estudiante = ?
            """, (id_estudiante,)).fetchall()
            return [dict(r) for r in rows]

    @staticmethod
    def grupos(id_estudiante):
        with get_connection() as conn:
            rows = conn.execute("""
                SELECT g.horario, m.nombre AS materia,
                       p.nombre || ' ' || p.apellidos AS profesor,
                       a.clave AS aula, ps.nombre AS periodo
                FROM grupo_estudiante ge
                JOIN grupo g ON g.id_grupo = ge.id_grupo
                JOIN materia m ON m.id_materia = g.id_materia
                JOIN profesor p ON p.id_profesor = g.id_profesor
                JOIN aula a ON a.id_aula = g.id_aula
                JOIN periodo_semestral ps ON ps.id_periodo = g.id_periodo
                WHERE ge.id_estudiante = ?
            """, (id_estudiante,)).fetchall()
            return [dict(r) for r in rows]


# ─────────────────────────────────────────
#  AULA
# ─────────────────────────────────────────
class AulaModel:
    TABLA = "aula"
    PK    = "id_aula"

    @staticmethod
    def crear(clave, edificio, capacidad, tipo):
        return insertar(AulaModel.TABLA, {
            "clave": clave, "edificio": edificio,
            "capacidad": capacidad, "tipo": tipo
        })

    @staticmethod
    def todos():
        return obtener_todos(AulaModel.TABLA)

    @staticmethod
    def por_id(id_aula):
        return obtener_por_id(AulaModel.TABLA, AulaModel.PK, id_aula)

    @staticmethod
    def actualizar(id_aula, datos):
        return actualizar(AulaModel.TABLA, datos, AulaModel.PK, id_aula)

    @staticmethod
    def eliminar(id_aula):
        return eliminar(AulaModel.TABLA, AulaModel.PK, id_aula)


# ─────────────────────────────────────────
#  PERIODO SEMESTRAL
# ─────────────────────────────────────────
class PeriodoModel:
    TABLA = "periodo_semestral"
    PK    = "id_periodo"

    @staticmethod
    def crear(nombre, fecha_inicio, fecha_fin, estado="activo"):
        return insertar(PeriodoModel.TABLA, {
            "nombre": nombre, "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin, "estado": estado
        })

    @staticmethod
    def todos():
        return obtener_todos(PeriodoModel.TABLA)

    @staticmethod
    def activo():
        with get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM periodo_semestral WHERE estado = 'activo' LIMIT 1"
            ).fetchone()
            return dict(row) if row else None

    @staticmethod
    def por_id(id_periodo):
        return obtener_por_id(PeriodoModel.TABLA, PeriodoModel.PK, id_periodo)

    @staticmethod
    def actualizar(id_periodo, datos):
        return actualizar(PeriodoModel.TABLA, datos, PeriodoModel.PK, id_periodo)

    @staticmethod
    def eliminar(id_periodo):
        return eliminar(PeriodoModel.TABLA, PeriodoModel.PK, id_periodo)


# ─────────────────────────────────────────
#  GRUPO
# ─────────────────────────────────────────
class GrupoModel:
    TABLA = "grupo"
    PK    = "id_grupo"

    @staticmethod
    def crear(horario, id_materia, id_profesor, id_aula, id_periodo):
        return insertar(GrupoModel.TABLA, {
            "horario": horario, "id_materia": id_materia,
            "id_profesor": id_profesor, "id_aula": id_aula,
            "id_periodo": id_periodo
        })

    @staticmethod
    def todos():
        return ejecutar_vista("v_grupos")

    @staticmethod
    def por_id(id_grupo):
        return obtener_por_id(GrupoModel.TABLA, GrupoModel.PK, id_grupo)

    @staticmethod
    def estudiantes(id_grupo):
        with get_connection() as conn:
            rows = conn.execute("""
                SELECT e.id_estudiante,
                       e.num_control,
                       e.nombre || ' ' || e.apellidos AS estudiante,
                       ge.id_grupo_est
                FROM grupo_estudiante ge
                JOIN estudiante e ON e.id_estudiante = ge.id_estudiante
                WHERE ge.id_grupo = ?
            """, (id_grupo,)).fetchall()
            return [dict(r) for r in rows]

    @staticmethod
    def inscribir_estudiante(id_grupo, id_estudiante):
        id_ge = insertar("grupo_estudiante", {
            "id_grupo": id_grupo, "id_estudiante": id_estudiante
        })
        # Crear registro de calificación vacío
        insertar("calificacion", {"id_grupo_est": id_ge})
        return id_ge

    @staticmethod
    def actualizar(id_grupo, datos):
        return actualizar(GrupoModel.TABLA, datos, GrupoModel.PK, id_grupo)

    @staticmethod
    def eliminar(id_grupo):
        return eliminar(GrupoModel.TABLA, GrupoModel.PK, id_grupo)


# ─────────────────────────────────────────
#  CALIFICACIÓN
# ─────────────────────────────────────────
class CalificacionModel:

    @staticmethod
    def todas():
        return ejecutar_vista("v_calificaciones")

    @staticmethod
    def todas_con_id():
        """Igual que todas() pero incluye id_calificacion para poder editar."""
        with get_connection() as conn:
            rows = conn.execute("""
                SELECT c.id_calificacion,
                       e.num_control,
                       e.nombre || ' ' || e.apellidos AS estudiante,
                       m.nombre                        AS materia,
                       ps.nombre                       AS periodo,
                       c.calificacion_parcial,
                       c.calificacion_final,
                       c.observaciones
                FROM calificacion        c
                JOIN grupo_estudiante    ge  ON ge.id_grupo_est = c.id_grupo_est
                JOIN estudiante          e   ON e.id_estudiante = ge.id_estudiante
                JOIN grupo               g   ON g.id_grupo      = ge.id_grupo
                JOIN materia             m   ON m.id_materia     = g.id_materia
                JOIN periodo_semestral   ps  ON ps.id_periodo    = g.id_periodo
                ORDER BY ps.nombre, e.apellidos, e.nombre
            """).fetchall()
            return [dict(r) for r in rows]

    @staticmethod
    def por_grupo(id_grupo):
        with get_connection() as conn:
            rows = conn.execute("""
                SELECT c.id_calificacion, c.id_grupo_est,
                       e.num_control, e.nombre || ' ' || e.apellidos AS estudiante,
                       c.calificacion_parcial, c.calificacion_final, c.observaciones
                FROM calificacion c
                JOIN grupo_estudiante ge ON ge.id_grupo_est = c.id_grupo_est
                JOIN estudiante e ON e.id_estudiante = ge.id_estudiante
                WHERE ge.id_grupo = ?
            """, (id_grupo,)).fetchall()
            return [dict(r) for r in rows]

    @staticmethod
    def actualizar(id_calificacion, parcial=None, final=None, obs=None):
        datos = {}
        if parcial is not None: datos["calificacion_parcial"] = parcial
        if final   is not None: datos["calificacion_final"]   = final
        if obs     is not None: datos["observaciones"]= obs if obs != "" else None
        if datos:
            return actualizar("calificacion", datos, "id_calificacion", id_calificacion)
        return 0
