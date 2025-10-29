import pytest
from fastapi.testclient import TestClient


def test_health_endpoint(client: TestClient):
    """Test de l'endpoint de santé"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_legend(client: TestClient):
    """Test de l'endpoint de légende"""
    response = client.get("/api/v1/legend/")
    assert response.status_code == 200
    
    data = response.json()
    assert 'a' in data
    assert data['a']['label'] == 'Administratif/gestion'
    assert data['a']['color'] == '#49B675'


def test_create_employee(client: TestClient):
    """Test de création d'employé"""
    employee_data = {
        "slug": "test-employee",
        "fullname": "Test Employee",
        "active": True
    }
    
    response = client.post("/api/v1/employees/", json=employee_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["slug"] == "test-employee"
    assert data["fullname"] == "Test Employee"
    assert data["active"] == True
    assert "id" in data


def test_get_employees(client: TestClient):
    """Test de récupération des employés"""
    # Créer un employé d'abord
    employee_data = {
        "slug": "test-get",
        "fullname": "Test Get",
        "active": True
    }
    client.post("/api/v1/employees/", json=employee_data)
    
    # Récupérer la liste
    response = client.get("/api/v1/employees/")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["slug"] == "test-get"


def test_auth_login_valid_pin(client: TestClient):
    """Test de connexion avec PIN valide"""
    login_data = {"pin": "1234"}  # PIN par défaut dans les tests
    
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_auth_login_invalid_pin(client: TestClient):
    """Test de connexion avec PIN invalide"""
    login_data = {"pin": "wrong"}
    
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 401
    assert "Invalid PIN" in response.json()["detail"]


def test_create_employee_duplicate_slug(client: TestClient):
    """Test de création d'employé avec slug dupliqué"""
    employee_data = {
        "slug": "duplicate",
        "fullname": "First Employee",
        "active": True
    }
    
    # Première création
    response1 = client.post("/api/v1/employees/", json=employee_data)
    assert response1.status_code == 200
    
    # Tentative de duplication
    employee_data["fullname"] = "Second Employee"
    response2 = client.post("/api/v1/employees/", json=employee_data)
    assert response2.status_code == 400
    assert "already exists" in response2.json()["detail"]