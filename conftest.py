import pytest
import requests

BASE_URL = "https://dummyjson.com"

VALID_USER = {
    "username": "emilys",
    "password": "emilyspass",
}

VALID_USER_ID = 1  # emilys has userId=1


@pytest.fixture(scope="session")
def auth_token() -> str:
    """Авторизуется один раз на всю сессию и возвращает access-токен."""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json=VALID_USER,
        timeout=10,
    )
    assert response.status_code == 200, "Не удалось получить токен для фикстуры"
    token = response.json().get("accessToken")
    assert token, "accessToken отсутствует в ответе"
    return token


@pytest.fixture(scope="session")
def auth_headers(auth_token: str) -> dict:
    """Заголовки с Bearer-токеном для авторизованных запросов."""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture(scope="session")
def existing_cart_id() -> int:
    """Возвращает id первой корзины из списка (userId=1)."""
    response = requests.get(
        f"{BASE_URL}/carts/user/{VALID_USER_ID}",
        timeout=10,
    )
    assert response.status_code == 200
    carts = response.json().get("carts", [])
    assert carts, "У пользователя нет корзин для тестов"
    return carts[0]["id"]
