# 🎯 QA Challenge — Instrucciones para el Candidato

> **Duración estimada:** 4 – 6 horas de trabajo efectivo  
> **Plazo de entrega:** 7 días calendario  
> **Nivel:** Mid – Senior QA Engineer / QA Automation  

---

## 📋 Resumen

Tienes frente a ti **TaskFlow**, una aplicación de gestión de tareas con API REST y frontend web. Tu misión es evaluarla como si estuvieras por primera vez en un equipo y este producto está a punto de ir a producción.

La aplicación **tiene bugs intencionales** — tu trabajo es encontrarlos, documentarlos, y demostrar tus habilidades de testing tanto manuales como automatizadas.

---

## 🔍 Lo que Evaluamos

| Sí evaluamos | No evaluamos |
|---|---|
| Capacidad para encontrar bugs reales | Velocidad de completación |
| Calidad de documentación de bugs | Que encuentres absolutamente todos |
| Diseño de plan y casos de prueba | Conocimiento del stack específico |
| Automatización de tests (API + UI) | Interfaz de los reportes |
| Pensamiento crítico y analítico | |
| Tests de rendimiento y seguridad básica | |

---

## 🛠️ Setup

### Prerequisitos

| Herramienta | Verificar con |
|---|---|
| Docker | `docker --version` |
| Docker Compose | `docker compose version` |
| Python 3.10+ | `python3 --version` |
| Node.js 18+ (para Playwright/Cypress) | `node --version` |

### Levantar la aplicación

```bash
# 1. Levantar
make start

# 2. Poblar datos de prueba
make seed

# 3. Abrir
# App:     http://localhost:8080
# Swagger: http://localhost:8080/docs

# 4. Para reiniciar desde cero
make restart
```

---

## 🏆 Desafíos

### Desafío 1: Plan de Pruebas y Diseño de Casos (20 puntos)

**Entregable:** `docs/test-plan.md`

Crear un plan de pruebas profesional que incluya:

1. **Alcance:** Qué se prueba y qué no se prueba
2. **Estrategia:** Tipos de prueba a ejecutar (funcional, API, UI, performance, seguridad)
3. **Matriz de riesgos:** Identificar las áreas más riesgosas de la aplicación
4. **Casos de prueba:** Mínimo 30 casos organizados por módulo (Users, Projects, Tasks, Comments, Stats, Export)
5. **Priorización:** Clasificar los casos por prioridad (P1-P4)

Cada caso de prueba debe incluir: ID, título, precondiciones, pasos, datos de prueba, resultado esperado, y prioridad.

---

### Desafío 2: Bug Hunting y Reportes (25 puntos)

**Entregable:** `docs/bug-reports.md`

Explorar la aplicación exhaustivamente (API + UI) y documentar todos los bugs encontrados.

Cada bug report debe seguir este formato:

```
### BUG-XXX: [Título descriptivo]
- **Severidad:** Crítica / Alta / Media / Baja
- **Componente:** API / Frontend / Base de Datos
- **Endpoint/Pantalla:** [Dónde ocurre]
- **Precondiciones:** [Estado necesario]
- **Pasos para reproducir:**
  1. ...
  2. ...
- **Resultado actual:** [Qué pasa]
- **Resultado esperado:** [Qué debería pasar]
- **Evidencia:** [Request/response, screenshot, log]
- **Impacto:** [Cómo afecta al usuario/negocio]
- **Sugerencia de fix:** [Opcional pero valorado]
```

**Tips para el bug hunting:**
- Prueba los happy paths Y los edge cases
- Prueba con datos inválidos, vacíos, extremos
- Revisa la coherencia entre URL paths y body parameters
- Verifica la paginación con diferentes filtros
- Prueba operaciones en recursos que no deberían existir
- Intenta romper la validación de datos
- **Piensa en seguridad** — ¿hay inyección posible?

---

### Desafío 3: Automatización de Tests API (25 puntos)

**Entregable:** Código en `tests/api/`

Automatizar tests para los endpoints de la API usando la herramienta de tu elección:
- **Opción A:** Postman/Newman (exportar collection + environment en `tests/api/`)
- **Opción B:** Python con pytest + requests (preferido)
- **Opción C:** JavaScript con Jest/Mocha + supertest

**Cobertura mínima requerida:**

| Módulo | Casos mínimos |
|--------|--------------|
| Health | Health check responde 200 |
| Users | CRUD completo + validaciones (email inválido, duplicados, campos requeridos) |
| Projects | CRUD + filtros por estado + validación de owner |
| Tasks | CRUD + filtros + paginación + búsqueda + transiciones de estado |
| Comments | Crear + listar + coherencia task_id |
| Stats | Estadísticas globales y por proyecto |
| Bulk | Operaciones masivas con IDs válidos e inválidos |
| Export | Exportar JSON y CSV |

**Requisitos del código:**
- Tests organizados por módulo
- Setup/teardown que limpie datos entre tests
- Assertions claros y descriptivos
- Ejecutable con un solo comando: `make test-api`
- README en `tests/api/` explicando cómo ejecutar

---

### Desafío 4: Automatización de Tests UI / E2E (15 puntos) — Senior

**Entregable:** Código en `tests/ui/`

Automatizar tests E2E usando **Playwright** o **Cypress**:

| Flujo | Descripción |
|-------|-------------|
| Crear tarea | Abrir modal → llenar form → guardar → verificar en lista |
| Filtrar tareas | Aplicar filtro por estado → verificar resultados |
| Ver detalle | Click en tarea → verificar datos en modal detalle |
| Cambiar estado | En detalle, cambiar estado → verificar actualización |
| Eliminar tarea | Click eliminar → verificar que desaparece |
| Buscar | Escribir en buscador → verificar resultados |

**Requisitos:**
- Page Object Model o estructura equivalente
- Screenshots en caso de fallo
- Ejecutable con: `make test-ui`
- Video o trace de ejecución incluido

---

### Desafío 5: Tests de Rendimiento y Seguridad (15 puntos) — Senior

**Entregable:** Código en `tests/performance/` y `tests/security/`

#### Performance (10 puntos)

Usar **K6**, **Artillery**, o **Locust** para:

1. **Load test:** 50 usuarios concurrentes durante 2 minutos
2. **Stress test:** Incrementar usuarios hasta encontrar el punto de quiebre
3. **Spike test:** Pico repentino de 100 usuarios
4. **Endpoints a probar:** GET /api/tasks (con filtros), POST /api/tasks, GET /api/stats

**Entregable:** Script de performance + reporte con métricas (latencia p50/p95/p99, throughput, error rate)

#### Seguridad Básica (5 puntos)

Documentar al menos 3 hallazgos de seguridad:
- ¿Hay inyección SQL posible?
- ¿Los inputs se sanitizan?
- ¿CORS está configurado correctamente?
- ¿Hay rate limiting?
- ¿Los errores exponen información interna?

---

## 📁 Formato de Entrega

```
qa-challenge/
├── docs/
│   ├── test-plan.md          # Plan de pruebas (Desafío 1)
│   └── bug-reports.md        # Bug reports (Desafío 2)
├── tests/
│   ├── api/                  # Tests automatizados API (Desafío 3)
│   │   ├── README.md
│   │   └── ...
│   ├── ui/                   # Tests E2E (Desafío 4)
│   │   ├── README.md
│   │   └── ...
│   ├── performance/          # Tests de rendimiento (Desafío 5)
│   │   ├── README.md
│   │   └── ...
│   └── security/             # Hallazgos de seguridad (Desafío 5)
│       └── README.md
└── ci/
    └── .github/workflows/    # Pipeline CI (Bonus)
        └── tests.yml
```

### Los tests deben ejecutarse con:

```bash
make test-api    # Tests de API
make test-ui     # Tests de UI (E2E)
make test-perf   # Tests de rendimiento
make test-all    # Todos los tests
```

---

## 📊 Criterios de Evaluación

| Desafío | Puntos | Obligatorio |
|---|---|---|
| 1. Plan de Pruebas | 20 | ✅ Sí |
| 2. Bug Hunting | 25 | ✅ Sí |
| 3. Automatización API | 25 | ✅ Sí |
| 4. Tests UI / E2E | 15 | ❌ Senior |
| 5. Performance + Seguridad | 15 | ❌ Senior |
| **Total** | **100** | |

### Bonus (hasta +10 puntos extra)

- Pipeline CI/CD que ejecute todos los tests automáticamente (+5)
- Reporte HTML de resultados con Allure o similar (+3)
- Tests de accesibilidad con axe-core o similar (+2)

### Escala de Resultados

| Rango | Resultado |
|---|---|
| **85 – 110** | 🟢 Excelente — Senior QA / QA Lead |
| **70 – 84** | 🔵 Aprobado — QA sólido con autonomía |
| **55 – 69** | 🟡 Parcial — Fundamentos OK, gaps en automatización |
| **< 55** | 🔴 No aprobado |

---

## 💡 Tips

1. **Empieza explorando** — Abre Swagger (`/docs`), juega con la API, navega el frontend
2. **Documenta mientras pruebas** — No dejes los bug reports para el final
3. **La API tiene bugs que el frontend no muestra** — Prueba la API directamente
4. **Piensa en edge cases** — ¿Qué pasa con strings vacíos? ¿Caracteres especiales? ¿IDs que no existen?
5. **Calidad > Cantidad** — 15 tests bien escritos valen más que 50 tests frágiles
6. **Si encuentras un bug de seguridad, documéntalo con cuidado** — demuestra pensamiento de seguridad

---

## ❓ Preguntas

Puedes contactarnos por correo si tienes dudas. Las preguntas inteligentes demuestran atención al detalle.

> *¡Mucha suerte! Queremos ver tu ojo crítico y tu capacidad analítica.* 🔍
