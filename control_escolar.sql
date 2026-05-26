-- ============================================================
--  Sistema Integral de Control Escolar
--  Base de datos: SQLite
--  Asignatura: Tópicos Avanzados de Programación
-- ============================================================

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

-- ------------------------------------------------------------
-- 1. CARRERA
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS carrera (
    id_carrera  INTEGER PRIMARY KEY AUTOINCREMENT,
    clave       TEXT    NOT NULL UNIQUE,
    nombre      TEXT    NOT NULL,
    descripcion TEXT
);

-- ------------------------------------------------------------
-- 2. MATERIA
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS materia (
    id_materia  INTEGER PRIMARY KEY AUTOINCREMENT,
    clave       TEXT    NOT NULL UNIQUE,
    nombre      TEXT    NOT NULL,
    creditos    INTEGER NOT NULL CHECK (creditos > 0),
    semestre    INTEGER NOT NULL CHECK (semestre BETWEEN 1 AND 12),
    id_carrera  INTEGER NOT NULL,
    FOREIGN KEY (id_carrera) REFERENCES carrera (id_carrera)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

-- ------------------------------------------------------------
-- 3. PROFESOR
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS profesor (
    id_profesor  INTEGER PRIMARY KEY AUTOINCREMENT,
    num_empleado TEXT    NOT NULL UNIQUE,
    nombre       TEXT    NOT NULL,
    apellidos    TEXT    NOT NULL,
    correo       TEXT    NOT NULL UNIQUE,
    especialidad TEXT
);

-- ------------------------------------------------------------
-- 4. ESTUDIANTE
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS estudiante (
    id_estudiante INTEGER PRIMARY KEY AUTOINCREMENT,
    num_control   TEXT    NOT NULL UNIQUE,
    nombre        TEXT    NOT NULL,
    apellidos     TEXT    NOT NULL,
    correo        TEXT    NOT NULL UNIQUE,
    semestre      INTEGER NOT NULL CHECK (semestre BETWEEN 1 AND 12),
    id_carrera    INTEGER NOT NULL,
    FOREIGN KEY (id_carrera) REFERENCES carrera (id_carrera)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

-- ------------------------------------------------------------
-- 5. AULA
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS aula (
    id_aula    INTEGER PRIMARY KEY AUTOINCREMENT,
    clave      TEXT    NOT NULL UNIQUE,
    edificio   TEXT    NOT NULL,
    capacidad  INTEGER NOT NULL CHECK (capacidad > 0),
    tipo       TEXT    NOT NULL  -- e.g. 'laboratorio', 'salon', 'taller'
);

-- ------------------------------------------------------------
-- 6. PERIODO SEMESTRAL
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS periodo_semestral (
    id_periodo   INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre       TEXT    NOT NULL,
    fecha_inicio TEXT    NOT NULL,  -- ISO-8601: 'YYYY-MM-DD'
    fecha_fin    TEXT    NOT NULL,
    estado       TEXT    NOT NULL DEFAULT 'activo'
                         CHECK (estado IN ('activo', 'cerrado', 'pendiente')),
    CHECK (fecha_fin > fecha_inicio)
);

-- ------------------------------------------------------------
-- 7. GRUPO
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS grupo (
    id_grupo    INTEGER PRIMARY KEY AUTOINCREMENT,
    horario     TEXT    NOT NULL,  -- e.g. 'Lun-Mie 07:00-09:00'
    id_materia  INTEGER NOT NULL,
    id_profesor INTEGER NOT NULL,
    id_aula     INTEGER NOT NULL,
    id_periodo  INTEGER NOT NULL,
    FOREIGN KEY (id_materia)  REFERENCES materia          (id_materia)  ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (id_profesor) REFERENCES profesor         (id_profesor) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (id_aula)     REFERENCES aula             (id_aula)     ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (id_periodo)  REFERENCES periodo_semestral(id_periodo)  ON UPDATE CASCADE ON DELETE RESTRICT
);

-- ------------------------------------------------------------
-- 8. GRUPO_ESTUDIANTE  (relación M:N entre grupo y estudiante)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS grupo_estudiante (
    id_grupo_est  INTEGER PRIMARY KEY AUTOINCREMENT,
    id_grupo      INTEGER NOT NULL,
    id_estudiante INTEGER NOT NULL,
    fecha_inscripcion TEXT DEFAULT (DATE('now')),
    UNIQUE (id_grupo, id_estudiante),
    FOREIGN KEY (id_grupo)      REFERENCES grupo     (id_grupo)      ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (id_estudiante) REFERENCES estudiante(id_estudiante) ON UPDATE CASCADE ON DELETE CASCADE
);

-- ------------------------------------------------------------
-- 9. CALIFICACION
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS calificacion (
    id_calificacion     INTEGER PRIMARY KEY AUTOINCREMENT,
    id_grupo_est        INTEGER NOT NULL UNIQUE,  -- 1 calificación por inscripción
    calificacion_parcial REAL   CHECK (calificacion_parcial BETWEEN 0 AND 100),
    calificacion_final   REAL   CHECK (calificacion_final   BETWEEN 0 AND 100),
    observaciones        TEXT,
    FOREIGN KEY (id_grupo_est) REFERENCES grupo_estudiante(id_grupo_est)
        ON UPDATE CASCADE ON DELETE CASCADE
);

-- ============================================================
--  ÍNDICES  (mejoran rendimiento en consultas frecuentes)
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_materia_carrera      ON materia          (id_carrera);
CREATE INDEX IF NOT EXISTS idx_estudiante_carrera   ON estudiante       (id_carrera);
CREATE INDEX IF NOT EXISTS idx_grupo_materia        ON grupo            (id_materia);
CREATE INDEX IF NOT EXISTS idx_grupo_profesor       ON grupo            (id_profesor);
CREATE INDEX IF NOT EXISTS idx_grupo_periodo        ON grupo            (id_periodo);
CREATE INDEX IF NOT EXISTS idx_grupo_est_grupo      ON grupo_estudiante (id_grupo);
CREATE INDEX IF NOT EXISTS idx_grupo_est_estudiante ON grupo_estudiante (id_estudiante);

-- ============================================================
--  VISTAS  (facilitan reportes básicos)
-- ============================================================

-- Calificaciones completas con nombres
CREATE VIEW IF NOT EXISTS v_calificaciones AS
SELECT
    e.num_control,
    e.nombre || ' ' || e.apellidos AS estudiante,
    m.nombre                        AS materia,
    m.clave                         AS clave_materia,
    p.nombre || ' ' || p.apellidos AS profesor,
    g.horario,
    ps.nombre                       AS periodo,
    c.calificacion_parcial,
    c.calificacion_final,
    c.observaciones
FROM calificacion        c
JOIN grupo_estudiante    ge  ON ge.id_grupo_est = c.id_grupo_est
JOIN estudiante          e   ON e.id_estudiante = ge.id_estudiante
JOIN grupo               g   ON g.id_grupo      = ge.id_grupo
JOIN materia             m   ON m.id_materia     = g.id_materia
JOIN profesor            p   ON p.id_profesor    = g.id_profesor
JOIN periodo_semestral   ps  ON ps.id_periodo    = g.id_periodo;

-- Grupos con todos sus datos
CREATE VIEW IF NOT EXISTS v_grupos AS
SELECT
    g.id_grupo,
    m.nombre                        AS materia,
    m.clave                         AS clave_materia,
    p.nombre || ' ' || p.apellidos AS profesor,
    a.clave                         AS aula,
    a.edificio,
    g.horario,
    ps.nombre                       AS periodo,
    ps.estado                       AS estado_periodo,
    COUNT(ge.id_estudiante)         AS num_estudiantes
FROM grupo               g
JOIN materia             m  ON m.id_materia  = g.id_materia
JOIN profesor            p  ON p.id_profesor = g.id_profesor
JOIN aula                a  ON a.id_aula     = g.id_aula
JOIN periodo_semestral   ps ON ps.id_periodo = g.id_periodo
LEFT JOIN grupo_estudiante ge ON ge.id_grupo = g.id_grupo
GROUP BY g.id_grupo;

-- Horario de un profesor (útil para la app móvil)
CREATE VIEW IF NOT EXISTS v_horario_profesor AS
SELECT
    p.num_empleado,
    p.nombre || ' ' || p.apellidos AS profesor,
    m.nombre                        AS materia,
    a.clave                         AS aula,
    a.edificio,
    g.horario,
    ps.nombre                       AS periodo
FROM grupo             g
JOIN materia           m  ON m.id_materia  = g.id_materia
JOIN profesor          p  ON p.id_profesor = g.id_profesor
JOIN aula              a  ON a.id_aula     = g.id_aula
JOIN periodo_semestral ps ON ps.id_periodo = g.id_periodo;

-- ============================================================
--  DATOS DE PRUEBA
-- ============================================================

-- Carreras
INSERT INTO carrera (clave, nombre, descripcion) VALUES
    ('ISC', 'Ing. en Sistemas Computacionales', 'Carrera enfocada en desarrollo de software y redes'),
    ('IIA', 'Ing. en Inteligencia Artificial',  'Carrera orientada a IA y ciencia de datos'),
    ('IGE', 'Ing. en Gestión Empresarial',      'Carrera con enfoque en administración y TIC');

-- Materias
INSERT INTO materia (clave, nombre, creditos, semestre, id_carrera) VALUES
    ('SC-401', 'Tópicos Avanzados de Programación', 5, 4, 1),
    ('SC-402', 'Base de Datos Avanzadas',            5, 4, 1),
    ('SC-501', 'Desarrollo Web',                     4, 5, 1),
    ('IA-301', 'Aprendizaje Automático',             5, 3, 2),
    ('IA-401', 'Visión Computacional',               4, 4, 2);

-- Profesores
INSERT INTO profesor (num_empleado, nombre, apellidos, correo, especialidad) VALUES
    ('EMP-001', 'Carlos',   'Mendoza López',   'cmendoza@iteso.edu.mx',  'Desarrollo de Software'),
    ('EMP-002', 'Patricia', 'Ruiz Hernández',  'pruiz@iteso.edu.mx',     'Base de Datos'),
    ('EMP-003', 'Roberto',  'Vargas Castillo',  'rvargas@iteso.edu.mx',  'Inteligencia Artificial');

-- Estudiantes
INSERT INTO estudiante (num_control, nombre, apellidos, correo, semestre, id_carrera) VALUES
    ('21SC001', 'Ana',    'García Torres',    'ana.garcia@estudiante.mx',    4, 1),
    ('21SC002', 'Luis',   'Martínez Pérez',   'luis.martinez@estudiante.mx', 4, 1),
    ('21SC003', 'Sofía',  'López Ramírez',    'sofia.lopez@estudiante.mx',   4, 1),
    ('21IA001', 'Diego',  'Sánchez Morales',  'diego.sanchez@estudiante.mx', 4, 2),
    ('21IA002', 'Valeria','Flores Jiménez',   'valeria.flores@estudiante.mx',4, 2);

-- Aulas
INSERT INTO aula (clave, edificio, capacidad, tipo) VALUES
    ('A-101', 'Edificio A', 35, 'salon'),
    ('B-205', 'Edificio B', 20, 'laboratorio'),
    ('C-301', 'Edificio C', 40, 'salon');

-- Periodo semestral
INSERT INTO periodo_semestral (nombre, fecha_inicio, fecha_fin, estado) VALUES
    ('Agosto-Diciembre 2025', '2025-08-11', '2025-12-19', 'activo');

-- Grupos
INSERT INTO grupo (horario, id_materia, id_profesor, id_aula, id_periodo) VALUES
    ('Lun-Mie 07:00-09:00', 1, 1, 2, 1),  -- TAP  - Carlos   - Lab B-205
    ('Mar-Jue 09:00-11:00', 2, 2, 1, 1),  -- BDA  - Patricia - A-101
    ('Lun-Mie 11:00-13:00', 4, 3, 1, 1);  -- ML   - Roberto  - A-101

-- Inscripciones (grupo_estudiante)
INSERT INTO grupo_estudiante (id_grupo, id_estudiante) VALUES
    (1, 1), (1, 2), (1, 3),   -- Ana, Luis, Sofía en TAP
    (2, 1), (2, 2),            -- Ana, Luis en BDA
    (3, 4), (3, 5);            -- Diego, Valeria en ML

-- Calificaciones parciales
INSERT INTO calificacion (id_grupo_est, calificacion_parcial, calificacion_final, observaciones) VALUES
    (1, 88.0, 91.0, NULL),
    (2, 75.0, 80.0, 'Mejoró en el examen final'),
    (3, 95.0, 97.0, 'Desempeño sobresaliente'),
    (4, 82.0, 85.0, NULL),
    (5, 70.0, 74.0, 'Necesita reforzar SQL'),
    (6, 90.0, 92.0, NULL),
    (7, 88.0, 89.0, NULL);
