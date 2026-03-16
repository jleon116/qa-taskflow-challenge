import requests

BASE_URL = "http://localhost:8080/api"

def test_health_check():
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200