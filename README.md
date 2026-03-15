# 📋 TaskFlow — Task Management Application

## Descripción

TaskFlow es una aplicación web de gestión de tareas para equipos. Permite crear proyectos, asignar tareas, hacer seguimiento de estados, y exportar reportes.

### Funcionalidades

- **Usuarios:** Crear, listar, desactivar usuarios con roles (admin, member, viewer)
- **Proyectos:** CRUD de proyectos con estados (active, archived, deleted)
- **Tareas:** CRUD completo con prioridades, asignación, fechas límite, tags, y flujo de estados
- **Comentarios:** Hilos de comentarios por tarea
- **Estadísticas:** Dashboard con métricas (total, por estado, por prioridad, vencidas)
- **Exportación:** Exportar tareas en formato JSON o CSV
- **Operaciones masivas:** Actualización en lote de múltiples tareas

### Stack Tecnológico

| Componente | Tecnología |
|---|---|
| Backend | Python 3.12 + FastAPI |
| Frontend | HTML + CSS + Vanilla JS |
| Base de datos | SQLite |
| Contenedor | Docker + Docker Compose |

## Quick Start

```bash
# Levantar la aplicación
make start

# Poblar con datos de prueba
make seed

# Abrir en el navegador
open http://localhost:8080

# Detener
make stop
```

## API Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/users` | Crear usuario |
| GET | `/api/users` | Listar usuarios |
| GET | `/api/users/{id}` | Obtener usuario |
| DELETE | `/api/users/{id}` | Desactivar usuario |
| POST | `/api/projects` | Crear proyecto |
| GET | `/api/projects` | Listar proyectos |
| GET | `/api/projects/{id}` | Obtener proyecto |
| PUT | `/api/projects/{id}` | Actualizar proyecto |
| DELETE | `/api/projects/{id}` | Eliminar proyecto |
| POST | `/api/tasks` | Crear tarea |
| GET | `/api/tasks` | Listar tareas (con filtros y paginación) |
| GET | `/api/tasks/{id}` | Obtener tarea |
| PUT | `/api/tasks/{id}` | Actualizar tarea |
| DELETE | `/api/tasks/{id}` | Eliminar tarea |
| POST | `/api/tasks/{id}/comments` | Agregar comentario |
| GET | `/api/tasks/{id}/comments` | Listar comentarios |
| GET | `/api/stats` | Estadísticas |
| POST | `/api/tasks/bulk-update` | Actualización masiva |
| GET | `/api/export/tasks` | Exportar tareas |

Documentación interactiva Swagger: `http://localhost:8080/docs`

---

## 🎯 Tu Misión

Lee el archivo **`docs/CHALLENGE.md`** para conocer los desafíos, entregables, y criterios de evaluación.

---

*Este repositorio es parte de un proceso de evaluación técnica.*
