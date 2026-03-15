#!/usr/bin/env python3
"""
Seed Script — Populates the database with realistic test data.
Run: python seed.py [--api-url http://localhost:8080]
"""

import argparse
import json
import sys
import time
import requests

DEFAULT_URL = "http://localhost:8080/api"

USERS = [
    {"username": "jgomez", "email": "jorge.gomez@company.com", "full_name": "Jorge Gómez", "role": "admin"},
    {"username": "mrodriguez", "email": "maria.rodriguez@company.com", "full_name": "María Rodríguez", "role": "member"},
    {"username": "candres", "email": "carlos.andres@company.com", "full_name": "Carlos Andrés López", "role": "member"},
    {"username": "lmartinez", "email": "laura.martinez@company.com", "full_name": "Laura Martínez", "role": "member"},
    {"username": "dviewer", "email": "diana.viewer@company.com", "full_name": "Diana Peña", "role": "viewer"},
]

PROJECTS = [
    {"name": "Portal Web Corporativo", "description": "Rediseño del portal web principal de la empresa"},
    {"name": "App Móvil v2", "description": "Segunda versión de la aplicación móvil para clientes"},
    {"name": "Migración Cloud", "description": "Migración de infraestructura on-premise a AWS"},
]

TASKS = [
    # Portal Web
    {"title": "Diseñar wireframes de la página de inicio", "description": "Crear wireframes de baja fidelidad para la nueva página de inicio del portal", "priority": "high", "status": "done", "tags": ["diseño", "frontend"], "due_date": "2025-12-15"},
    {"title": "Implementar sistema de autenticación OAuth", "description": "Integrar login con Google y Microsoft usando OAuth 2.0", "priority": "critical", "status": "in_progress", "tags": ["backend", "seguridad"], "due_date": "2026-03-10"},
    {"title": "Optimizar queries de la página de reportes", "description": "Las queries del dashboard de reportes toman más de 5 segundos. Optimizar con índices y caching.", "priority": "high", "status": "in_review", "tags": ["backend", "performance"], "due_date": "2026-03-05"},
    {"title": "Corregir responsive del menú de navegación", "description": "El menú hamburguesa no funciona en iOS Safari", "priority": "medium", "status": "todo", "tags": ["frontend", "bug"], "due_date": "2026-03-20"},
    {"title": "Escribir tests e2e para flujo de registro", "description": "Cubrir el flujo completo de registro de usuario con Playwright", "priority": "medium", "status": "todo", "tags": ["testing", "frontend"], "due_date": "2026-04-01"},
    {"title": "Configurar CDN para assets estáticos", "description": None, "priority": "low", "status": "todo", "tags": ["infra"], "due_date": None},
    {"title": "Actualizar dependencias de seguridad", "description": "npm audit muestra 3 vulnerabilidades high. Actualizar packages.", "priority": "critical", "status": "todo", "tags": ["seguridad", "mantenimiento"], "due_date": "2026-02-28"},

    # App Móvil
    {"title": "Implementar push notifications", "description": "Integrar Firebase Cloud Messaging para notificaciones push en Android e iOS", "priority": "high", "status": "in_progress", "tags": ["mobile", "backend"], "due_date": "2026-03-15"},
    {"title": "Diseñar pantalla de onboarding", "description": "3 pantallas de bienvenida con animaciones Lottie", "priority": "medium", "status": "done", "tags": ["diseño", "mobile"], "due_date": "2025-11-30"},
    {"title": "Fix crash en Android 14 al abrir cámara", "description": "La app crash con NullPointerException al intentar abrir la cámara en dispositivos Samsung con Android 14", "priority": "critical", "status": "in_progress", "tags": ["bug", "mobile", "android"], "due_date": "2026-03-01"},
    {"title": "Implementar modo offline", "description": "Cachear datos críticos con Room DB para funcionamiento sin conexión", "priority": "high", "status": "todo", "tags": ["mobile", "backend"], "due_date": "2026-04-15"},
    {"title": "Tests de rendimiento en dispositivos low-end", "description": "Verificar performance en Moto G4 y similares. Target: 60fps en scroll, <2s cold start.", "priority": "medium", "status": "todo", "tags": ["testing", "performance"], "due_date": "2026-04-30"},

    # Migración Cloud
    {"title": "Documentar arquitectura actual on-premise", "description": "Diagrama de todos los servicios, bases de datos, y dependencias actuales", "priority": "high", "status": "done", "tags": ["documentación", "infra"], "due_date": "2025-10-15"},
    {"title": "Configurar VPC y subnets en AWS", "description": "VPC con subnets públicas y privadas en 2 AZs. NAT Gateway para salida de subnets privadas.", "priority": "critical", "status": "done", "tags": ["infra", "aws"], "due_date": "2025-12-01"},
    {"title": "Migrar base de datos PostgreSQL a RDS", "description": "Migrar la BD principal (500GB) usando DMS con mínimo downtime", "priority": "critical", "status": "in_review", "tags": ["infra", "aws", "database"], "due_date": "2026-03-20"},
    {"title": "Configurar monitoring con CloudWatch", "description": "Dashboards para CPU, memoria, disco, latencia de API, y error rates", "priority": "high", "status": "todo", "tags": ["infra", "monitoring"], "due_date": "2026-04-10"},
    {"title": "Plan de disaster recovery", "description": "Documentar RPO/RTO y procedimientos de recovery para cada servicio crítico", "priority": "medium", "status": "todo", "tags": ["documentación", "infra"], "due_date": "2026-05-01"},
    {"title": "Configurar alertas de costos", "description": "Budget alerts en AWS cuando el gasto exceda $5000/mes", "priority": "low", "status": "cancelled", "tags": ["infra", "aws"], "due_date": None},
]


def seed(api_url):
    print(f"\n🌱 Seeding data to {api_url}...\n")

    # Wait for API
    for i in range(10):
        try:
            r = requests.get(f"{api_url}/health", timeout=3)
            if r.status_code == 200:
                break
        except:
            pass
        print(f"  Waiting for API... ({i+1}/10)")
        time.sleep(2)
    else:
        print("❌ API not available")
        sys.exit(1)

    # Create users
    user_ids = []
    print("👤 Creating users...")
    for u in USERS:
        r = requests.post(f"{api_url}/users", json=u)
        if r.status_code == 201:
            user_ids.append(r.json()["id"])
            print(f"   ✓ {u['full_name']}")
        else:
            print(f"   ✗ {u['username']}: {r.text}")
            user_ids.append(None)

    # Create projects
    project_ids = []
    print("\n📁 Creating projects...")
    for i, p in enumerate(PROJECTS):
        p["owner_id"] = user_ids[0]  # admin owns all
        r = requests.post(f"{api_url}/projects", json=p)
        if r.status_code == 201:
            project_ids.append(r.json()["id"])
            print(f"   ✓ {p['name']}")
        else:
            print(f"   ✗ {p['name']}: {r.text}")
            project_ids.append(None)

    # Create tasks
    print("\n📝 Creating tasks...")
    task_project_map = [0]*7 + [1]*5 + [2]*6  # distribute tasks across projects
    for i, t in enumerate(TASKS):
        proj_idx = task_project_map[i] if i < len(task_project_map) else 0
        task_data = {
            "title": t["title"],
            "description": t.get("description"),
            "project_id": project_ids[proj_idx],
            "assignee_id": user_ids[(i % 4) + 1],  # rotate assignees (skip admin)
            "reporter_id": user_ids[0],
            "priority": t["priority"],
            "due_date": t.get("due_date"),
            "tags": t.get("tags", []),
        }
        r = requests.post(f"{api_url}/tasks", json=task_data)
        if r.status_code == 201:
            task_id = r.json()["id"]
            # Update status if not 'todo'
            if t["status"] != "todo":
                requests.put(f"{api_url}/tasks/{task_id}", json={"status": t["status"]})
            print(f"   ✓ {t['title'][:60]}...")
        else:
            print(f"   ✗ {t['title'][:40]}: {r.text}")

    print(f"\n✅ Seed complete! Created {len(USERS)} users, {len(PROJECTS)} projects, {len(TASKS)} tasks.\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed TaskFlow with test data")
    parser.add_argument("--api-url", default=DEFAULT_URL, help="API base URL")
    args = parser.parse_args()
    seed(args.api_url)
