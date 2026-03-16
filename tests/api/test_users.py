import requests
import uuid

BASE_URL = "http://localhost:8080/api"

def generate_email():
    return f"test_{uuid.uuid4()}@example.com"


def test_create_user():
    payload = {
        "username": f"user_{uuid.uuid4().hex[:8]}",
        "email": generate_email(),
        "full_name": "Test User",
        "password": "Test1234!",
        "role": "admin"
    }

    response = requests.post(f"{BASE_URL}/users", json=payload)
    print(response.text)

    assert response.status_code == 201
    data = response.json()

    assert data["email"] == payload["email"]


def test_create_user_invalid_email():
    payload = {
        "username": f"user_{uuid.uuid4()}",
        "email": "correo_invalido",
        "full_name": "Test User",
        "password": "Test1234!",
        "role": "admin"
    }

    response = requests.post(f"{BASE_URL}/users", json=payload)
    print(response.text)

    assert response.status_code != 201


def test_get_users():
    response = requests.get(f"{BASE_URL}/users")

    assert response.status_code == 200