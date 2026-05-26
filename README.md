# Sistema Integral de Control Escolar
### Tópicos Avanzados de Programación — Unidades 4 y 5

---

## Estructura del proyecto

```
control_escolar/
│
├── main.py                        ← Punto de entrada (ejecutar este)
├── control_escolar.sql            ← Script SQL (crear antes de correr)
├── requirements.txt
│
├── database/
│   ├── conexion.py                ← Conexión SQLite + inicialización
│   └── crud_base.py               ← CRUD genérico reutilizable
│
├── models/
│   └── modelos.py                 ← Lógica de negocio por entidad
│
├── views/
│   ├── widgets.py                 ← Componentes reutilizables
│   ├── pantalla_inicio.py         ← Menú principal
│   ├── pantalla_estudiantes.py    ← CRUD estudiantes + calificaciones
│   ├── pantallas_catalogo.py      ← Profesores, Materias, Aulas, Periodos
│   ├── pantalla_grupos.py         ← Grupos + inscripción + captura califs
│   ├── pantalla_calificaciones.py ← Vista general de calificaciones
│   └── pantalla_reportes.py       ← 5 reportes del sistema
│
└── utils/
    └── validaciones.py            ← Validaciones y formateo
```

---

## Instalación

### 1. Crear entorno virtual (recomendado)
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

> En Linux puede requerirse además:
> ```bash
> sudo apt install python3-dev libgl1-mesa-dev libgles2-mesa-dev
> ```

### 3. Colocar el script SQL
Asegúrate de que `control_escolar.sql` esté en la **raíz del proyecto**
(junto a `main.py`). La app lo detecta y crea la BD automáticamente
la primera vez.

### 4. Ejecutar
```bash
python main.py
```

---

## Tecnologías utilizadas

| Componente       | Tecnología         |
|------------------|--------------------|
| Base de datos    | SQLite 3           |
| Lenguaje         | Python 3.10+       |
| Interfaz móvil   | Kivy 2.3           |
| Conectividad     | Local (sqlite3)    |

---

## Funcionalidades implementadas

### CRUD completo
- ✅ Profesores
- ✅ Estudiantes
- ✅ Materias (asociadas a carrera)
- ✅ Carreras
- ✅ Aulas
- ✅ Periodos semestrales
- ✅ Grupos (con asignación de profesor, materia, aula, periodo)
- ✅ Inscripción de estudiantes en grupos
- ✅ Captura y edición de calificaciones (parcial y final)

### Reportes
1. Todas las calificaciones del sistema
2. Estudiantes por grupo (seleccionable)
3. Materias por carrera (seleccionable)
4. Grupos por profesor (con horario)
5. Promedio general por materia

### Seguridad / Validación
- Validación de correo electrónico (regex)
- Validación de fechas (formato ISO-8601)
- Validación de calificaciones (0–100)
- Restricciones de integridad referencial (FK en SQLite)
- Manejo de excepciones en todas las operaciones de BD

---

## Diagrama de entidades (resumen)

```
CARRERA ──< MATERIA ──< GRUPO >── PROFESOR
                         │
                         └──< GRUPO_ESTUDIANTE >── ESTUDIANTE
                                      │
                                 CALIFICACION
AULA ──────────────────> GRUPO
PERIODO_SEMESTRAL ──────> GRUPO
```
