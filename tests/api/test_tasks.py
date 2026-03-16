import requests
import uuid

BASE_URL = "http://localhost:8080/api"


def generate_task_title():
    return f"task_{uuid.uuid4().hex[:6]}"


def create_user_if_needed():

    users_response = requests.get(f"{BASE_URL}/users")
    users = users_response.json()

    if isinstance(users, list) and len(users) > 0:
        return users[0]["id"]

    if "items" in users and len(users["items"]) > 0:
        return users["items"][0]["id"]

    if "data" in users and len(users["data"]) > 0:
        return users["data"][0]["id"]

    # 🔹 crear usuario automáticamente
    payload = {
        "username": f"user_{uuid.uuid4().hex[:6]}",
        "email": f"user_{uuid.uuid4().hex[:6]}@test.com",
        "full_name": "Auto Test User",
        "password": "Test1234!",
        "role": "admin"
    }

    create = requests.post(f"{BASE_URL}/users", json=payload)
    user = create.json()

    return user["id"]


def get_project_id():

    response = requests.get(f"{BASE_URL}/projects")
    data = response.json()

    if isinstance(data, list) and len(data) > 0:
        return data[0]["id"]

    if "items" in data and len(data["items"]) > 0:
        return data["items"][0]["id"]

    if "data" in data and len(data["data"]) > 0:
        return data["data"][0]["id"]

    # 🔹 si no hay proyectos, crear uno automáticamente
    owner_id = create_user_if_needed()

    payload = {
        "name": f"auto_project_{uuid.uuid4().hex[:6]}",
        "description": "Auto created project",
        "owner_id": owner_id
    }

    create = requests.post(f"{BASE_URL}/projects", json=payload)
    project = create.json()

    return project["id"]


def test_create_task():

    project_id = get_project_id()

    users = requests.get(f"{BASE_URL}/users").json()

    reporter_id = None

    if isinstance(users, list) and len(users) > 0:
        reporter_id = users[0]["id"]

    elif isinstance(users, dict):
        if "items" in users and len(users["items"]) > 0:
            reporter_id = users["items"][0]["id"]
        elif "data" in users and len(users["data"]) > 0:
            reporter_id = users["data"][0]["id"]

    # 🔹 SI NO HAY USUARIOS, CREAR UNO AUTOMÁTICAMENTE
    if reporter_id is None:

        payload_user = {
            "username": f"user_{uuid.uuid4().hex[:6]}",
            "email": f"user_{uuid.uuid4().hex[:6]}@test.com",
            "full_name": "Auto Test User",
            "password": "Test1234!",
            "role": "admin"
        }

        create_user = requests.post(f"{BASE_URL}/users", json=payload_user)
        reporter_id = create_user.json()["id"]

    payload = {
        "title": generate_task_title(),
        "description": "Task created by test",
        "project_id": project_id,
        "reporter_id": reporter_id,
        "priority": "medium"
    }

    response = requests.post(f"{BASE_URL}/tasks", json=payload)

    assert response.status_code in [200, 201]


def test_get_tasks():

    response = requests.get(f"{BASE_URL}/tasks")

    assert response.status_code == 200


def test_tasks_pagination():

    response = requests.get(f"{BASE_URL}/tasks?page=1&limit=5")

    assert response.status_code == 200


def test_tasks_filter():

    response = requests.get(f"{BASE_URL}/tasks?status=open")

    assert response.status_code == 200