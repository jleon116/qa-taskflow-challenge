### BUG-001: API permite crear usuario con email inválido

- **Severidad:** Alta
- **Componente:** API
- **Endpoint/Pantalla:** POST /api/users
- **Precondiciones:** Aplicación corriendo en http://localhost:8080

**Pasos para reproducir**

1. Ir a http://localhost:8080/docs
2. Ejecutar endpoint POST /api/users
3. Enviar el siguiente request:

{
"username": "juan123",
"email": "correo_invalido",
"full_name": "Juan Perez",
"role": "member"
}

4. Presionar **Execute**

**Resultado actual**

La API crea el usuario y devuelve código **201 Created**.

**Resultado esperado**

La API debería validar el formato del email y devolver un error **400 Bad Request**.

**Evidencia**

Response code: 201

Response body:

{
"id": "802c3b1b-fd0e-4f25-a26c-c6bee59e271b",
"username": "juan123",
"email": "correo_invalido",
"full_name": "Juan Perez",
"role": "member"
}

**Impacto**

Permite almacenar correos inválidos en la base de datos, lo que puede causar problemas en notificaciones y gestión de usuarios.

------------------------------------------------------------------

### BUG-002: API permite crear usuario con email mal formado

- **Severidad:** Alta
- **Componente:** API
- **Endpoint/Pantalla:** POST /api/users
- **Precondiciones:** Aplicación ejecutándose en http://localhost:8080

**Pasos para reproducir**

1. Ir a http://localhost:8080/docs
2. Ejecutar el endpoint POST /api/users
3. Enviar el siguiente request:

{
"username": "usuario999",
"email": "test@.com",
"full_name": "Usuario Test",
"role": "member"
}

4. Presionar **Execute**

**Resultado actual**

La API crea el usuario y devuelve código **201 Created**.

**Resultado esperado**

La API debería validar el formato del email y devolver un error **400 Bad Request**.

**Evidencia**

Response code: 201

Response body:

{
"username": "usuario999",
"email": "test@.com"
}

**Impacto**

Permite almacenar correos inválidos en la base de datos, lo que puede generar problemas en notificaciones y consistencia de datos.

### BUG-003: API permite crear proyectos con owner_id inexistente

- **Severidad:** Alta
- **Componente:** API
- **Endpoint/Pantalla:** POST /api/projects
- **Precondiciones:** Aplicación ejecutándose en http://localhost:8080

**Pasos para reproducir**

1. Ir a http://localhost:8080/docs
2. Buscar el endpoint POST /api/projects
3. Enviar el siguiente request:

{
"name": "Proyecto Test",
"description": "Proyecto de prueba",
"owner_id": "999999"
}

4. Presionar Execute

**Resultado actual**

La API crea el proyecto y devuelve código **201 Created**, aunque el `owner_id` no existe.

**Resultado esperado**

La API debería validar que el `owner_id` exista y devolver un error **404 Not Found** o **400 Bad Request**.

**Evidencia**

Response code: 201

Response body:

{
"name": "Proyecto Test",
"owner_id": "999999"
}

**Impacto**

Permite crear proyectos asociados a usuarios inexistentes, generando inconsistencias en la base de datos.

### BUG-004: API permite almacenar código JavaScript en el título de la tarea (posible XSS)

- **Severidad:** Alta
- **Componente:** API / Seguridad
- **Endpoint:** POST /api/tasks
- **Precondiciones:** Aplicación ejecutándose

**Pasos para reproducir**

1. Ir a http://localhost:8080/docs
2. Ejecutar el endpoint POST /api/tasks
3. Enviar el siguiente request:

{
"title": "<script>alert(1)</script>",
"description": "test",
"project_id": "ecab4908-9664-4858-8ce1-53c83bd0a5e6",
"reporter_id": "ecab4908-9664-4858-8ce1-53c83bd0a5e6",
"priority": "medium"
}

4. Presionar Execute

**Resultado actual**

La API crea la tarea y guarda el código JavaScript en el campo `title`.

**Resultado esperado**

La API debería sanitizar o bloquear contenido HTML/JavaScript en los campos de texto.

**Impacto**

Esto podría permitir ataques **XSS**, ejecutando scripts maliciosos en el navegador de otros usuarios si el valor se renderiza en el frontend.