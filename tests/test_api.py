import pytest
import requests
import time
from typing import Optional


@pytest.fixture(scope="module")
def base_url_train():
    return "http://localhost:8000"


@pytest.fixture(scope="module")
def base_url_predict():
    return "http://localhost:8080"


@pytest.fixture(scope="module")
def auth_token_train(base_url_train):
    """Fixture pour obtenir le token d'authentification"""
    response = requests.post(
        f"{base_url_train}/login", headers={"Authorization": "Bearer user:rakuten_project"}
    )
    assert response.status_code == 200
    return response.json().get("token")


@pytest.fixture(scope="module")
def auth_token_predict(base_url_predict):
    """Fixture pour obtenir le token d'authentification"""
    response = requests.post(
        f"{base_url_predict}/login", headers={"Authorization": "Bearer user:rakuten_project"}
    )
    assert response.status_code == 200
    return response.json().get("token")


@pytest.fixture(scope="module")
def headers(auth_token_train):
    """Fixture pour les headers avec authentification"""
    return {"Authorization": f"Bearer {auth_token_train}", "Content-Type": "application/json"}


@pytest.fixture(scope="module")
def headers_predict(auth_token_predict):
    """Fixture pour les headers avec authentification"""
    return {"Authorization": f"Bearer {auth_token_predict}", "Content-Type": "application/json"}


@pytest.fixture(scope="module")
def bad_headers():
    """Fixture pour les headers avec authentification"""
    return {
        "Authorization": "Bearer vxbjXP62XK9f6VYiY-m2D2k_EEoZQpgx2Q9o47zXN0U",
        "Content-Type": "application/json",
    }


def test_login_success(base_url_train):
    """Test de la connexion avec des identifiants valides"""
    response = requests.post(
        f"{base_url_train}/login", headers={"Authorization": "Bearer user:rakuten_project"}
    )
    assert response.status_code == 200
    assert "token" in response.json()


def test_login_success_predict(base_url_predict):
    """Test de la connexion avec des identifiants valides"""
    response = requests.post(
        f"{base_url_predict}/login", headers={"Authorization": "Bearer user:rakuten_project"}
    )
    assert response.status_code == 200
    assert "token" in response.json()


def test_login_failure(base_url_train):
    """Test de la connexion avec des identifiants invalides"""
    response = requests.post(
        f"{base_url_train}/login", headers={"Authorization": "Bearer wrong:wrong"}
    )
    response_data = response.json()
    # Vérification de la structure de la réponse
    assert response.status_code == 401
    assert "detail" in response_data
    assert response_data["detail"] == "L'authentification a échoué, mauvais identifiants"


def test_login_failure_predict(base_url_predict):
    """Test de la connexion avec des identifiants invalides"""
    response = requests.post(
        f"{base_url_predict}/login", headers={"Authorization": "Bearer wrong:wrong"}
    )
    response_data = response.json()
    # Vérification de la structure de la réponse
    assert response.status_code == 401
    assert "detail" in response_data
    assert response_data["detail"] == "L'authentification a échoué, mauvais identifiants"


def test_train_token_manquante(base_url_train):
    """Test de prédiction token invalide ou manquante"""

    response = requests.post(
        f"{base_url_train}/train",
    )

    response_data = response.json()
    assert response.status_code == 400
    assert "detail" in response_data
    assert response_data["detail"] == "Aucune authentification envoyé"


def test_train_token_manquante_predict(base_url_train):
    """Test de prédiction token invalide ou manquante"""

    response = requests.post(
        f"{base_url_train}/train",
    )

    response_data = response.json()
    assert response.status_code == 400
    assert "detail" in response_data
    assert response_data["detail"] == "Aucune authentification envoyé"


def test_train_token_invalide(base_url_train, bad_headers):
    """Test de prédiction token invalide ou manquante"""

    response = requests.post(
        f"{base_url_train}/train",
        headers=bad_headers,
    )

    response_data = response.json()
    assert response.status_code == 400
    assert "detail" in response_data
    assert response_data["detail"] == "L'entrainement a échoué"


"""
def test_train(base_url_train, headers):
    Test de test success

    response = requests.post(
        f"{base_url_train}/train",
        headers=headers,
    )

    assert response.status_code == 200
"""


def test_prediction_token_manquante(base_url_predict):
    """Test de prédiction data invalide"""

    response = requests.post(f"{base_url_predict}/predict")

    response_data = response.json()
    assert response.status_code == 400
    assert "detail" in response_data
    assert response_data["detail"] == "Aucune authentification envoyé"


def test_prediction_token_invalide(base_url_predict, bad_headers):
    """Test de prédiction data invalide"""

    response = requests.post(f"{base_url_predict}/predict", headers=bad_headers)

    response_data = response.json()
    assert response.status_code == 400
    assert "detail" in response_data
    assert response_data["detail"] == "La prédiction a échoué"


def test_prediction(base_url_predict, headers_predict):
    """Test de prédiction success"""

    response = requests.post(
        f"{base_url_predict}/predict",
        headers=headers_predict,
    )

    assert response.status_code == 200
