# Test Plan — TaskFlow QA Challenge

## 1. Objetivo

El objetivo de este plan de pruebas es validar que la aplicación TaskFlow funcione correctamente en la gestión de usuarios, proyectos, tareas, comentarios, estadísticas y exportación de datos.

Las pruebas buscan asegurar que las funcionalidades principales operen correctamente, que los datos se manejen adecuadamente y que el sistema responda correctamente ante entradas inválidas.

---

# 2. Alcance

## En alcance

Las pruebas cubrirán los siguientes módulos del sistema:

- Users (Gestión de usuarios)
- Projects (Gestión de proyectos)
- Tasks (Gestión de tareas)
- Comments (Comentarios en tareas)
- Stats (Estadísticas del sistema)
- Export (Exportación de datos)

Las pruebas incluirán:

- Pruebas funcionales
- Pruebas de API
- Pruebas de UI
- Pruebas negativas
- Pruebas básicas de seguridad

## Fuera de alcance

- Pruebas de carga extensiva
- Pruebas de seguridad avanzadas (pentesting)
- Integraciones externas

---

# 3. Estrategia de Pruebas

## Pruebas Funcionales
Verificar que cada funcionalidad cumpla con los requisitos definidos.

## Pruebas de API
Validar el comportamiento de los endpoints usando la documentación Swagger disponible en:
http://localhost:8080/docs


## Pruebas de UI
Validar la interacción del usuario con la interfaz web.

## Pruebas Negativas
Enviar datos inválidos para verificar que el sistema maneje correctamente los errores.

## Pruebas de Seguridad Básica
Validar que el sistema maneje correctamente entradas potencialmente maliciosas.

## Pruebas de Performance Básica
Verificar tiempos de respuesta aceptables en endpoints críticos.

---

# 4. Matriz de Riesgos

| Módulo | Riesgo | Impacto |
|------|------|------|
Users | Creación de usuarios duplicados | Alto |
Projects | Eliminación accidental de proyectos | Medio |
Tasks | Flujo incorrecto de estados | Alto |
Comments | Pérdida de comentarios | Medio |
Stats | Métricas incorrectas | Bajo |
Export | Exportación corrupta | Medio |

---

# 5. Casos de Prueba

## Users

| ID | Título | Precondición | Pasos | Datos | Resultado Esperado | Prioridad |
|----|------|------|------|------|------|------|
TC-001 | Crear usuario válido | Sistema activo | POST /api/users | name,email,password | Usuario creado | P1 |
TC-002 | Crear usuario con email inválido | Sistema activo | Crear usuario | email inválido | Error 400 | P1 |
TC-003 | Crear usuario duplicado | Usuario existente | Crear usuario | mismo email | Error | P1 |
TC-004 | Listar usuarios | Usuarios existentes | GET /api/users | - | Lista de usuarios | P2 |
TC-005 | Desactivar usuario | Usuario existente | DELETE /api/users/{id} | id válido | Usuario desactivado | P2 |

---

## Projects

| ID | Título | Precondición | Pasos | Datos | Resultado Esperado | Prioridad |
|----|------|------|------|------|------|------|
TC-006 | Crear proyecto válido | Usuario existente | POST /api/projects | name | Proyecto creado | P1 |
TC-007 | Crear proyecto sin nombre | Sistema activo | Crear proyecto | name vacío | Error | P1 |
TC-008 | Listar proyectos | Proyectos existentes | GET /api/projects | - | Lista proyectos | P2 |
TC-009 | Actualizar proyecto | Proyecto existente | PUT /api/projects/{id} | nuevo nombre | Actualizado | P2 |
TC-010 | Eliminar proyecto | Proyecto existente | DELETE /api/projects/{id} | id | Eliminado | P2 |

---

## Tasks

| ID | Título | Precondición | Pasos | Datos | Resultado Esperado | Prioridad |
|----|------|------|------|------|------|------|
TC-011 | Crear tarea válida | Proyecto existente | POST /api/tasks | title | Tarea creada | P1 |
TC-012 | Crear tarea sin título | Proyecto existente | Crear tarea | title vacío | Error | P1 |
TC-013 | Asignar tarea a usuario | Usuario existente | Crear tarea | user_id | Tarea asignada | P2 |
TC-014 | Cambiar estado tarea | Tarea existente | PUT /api/tasks/{id} | status | Estado actualizado | P1 |
TC-015 | Eliminar tarea | Tarea existente | DELETE /api/tasks/{id} | id | Eliminada | P2 |

---

## Comments

| ID | Título | Precondición | Pasos | Datos | Resultado Esperado | Prioridad |
|----|------|------|------|------|------|------|
TC-016 | Agregar comentario | Tarea existente | POST /comments | text | Comentario creado | P2 |
TC-017 | Listar comentarios | Comentarios existentes | GET /comments | - | Lista comentarios | P3 |
TC-018 | Comentario vacío | Tarea existente | Crear comentario | vacío | Error | P2 |
TC-019 | Comentario largo | Tarea existente | Crear comentario | texto largo | Guardado | P3 |
TC-020 | Comentario con caracteres especiales | Tarea existente | Crear comentario | <script> | Validación | P2 |

---

## Stats

| ID | Título | Precondición | Pasos | Datos | Resultado Esperado | Prioridad |
|----|------|------|------|------|------|------|
TC-021 | Obtener estadísticas | Datos existentes | GET /api/stats | - | Métricas correctas | P2 |
TC-022 | Stats sin tareas | Sin tareas | GET stats | - | Valores en cero | P3 |
TC-023 | Stats con tareas vencidas | Tareas vencidas | GET stats | - | Conteo correcto | P2 |
TC-024 | Stats por prioridad | Tareas con prioridad | GET stats | - | Conteo correcto | P3 |
TC-025 | Stats por estado | Tareas en estados | GET stats | - | Conteo correcto | P2 |

---

## Export

| ID | Título | Precondición | Pasos | Datos | Resultado Esperado | Prioridad |
|----|------|------|------|------|------|------|
TC-026 | Exportar tareas JSON | Tareas existentes | GET /api/export/tasks | json | Archivo generado | P2 |
TC-027 | Exportar tareas CSV | Tareas existentes | GET /api/export/tasks | csv | Archivo generado | P2 |
TC-028 | Export sin tareas | Sin tareas | Export | - | Archivo vacío | P3 |
TC-029 | Export con filtros | Tareas filtradas | Export | status | Archivo correcto | P3 |
TC-030 | Export con gran volumen | Muchas tareas | Export | - | Export exitoso | P4 |