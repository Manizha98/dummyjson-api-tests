"""
Тесты авторизации: POST /auth/login и GET /auth/me
"""

import requests
import pytest

BASE_URL = "https://dummyjson.com"


class TestLogin:
    """POST /auth/login"""

    def test_successful_login_returns_token_and_user_data(self):
        """
        Успешная авторизация должна вернуть 200 с accessToken и данными пользователя.
        """
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"username": "emilys", "password": "emilyspass"},
            timeout=10,
        )

        assert response.status_code == 200

        body = response.json()
        assert "accessToken" in body, "Ответ не содержит accessToken"
        assert isinstance(body["accessToken"], str) and body["accessToken"], (
            "accessToken должен быть непустой строкой"
        )
        assert body.get("username") == "emilys", (
            "username в ответе не совпадает с отправленным"
        )
        assert "id" in body, "Ответ не содержит id пользователя"

    def test_login_with_wrong_password_returns_400(self):
        """
        Авторизация с неверным паролем должна вернуть 400 и сообщение об ошибке.
        Текущее поведение API: возвращает 400 с {"message": "Invalid credentials"}.
        """
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"username": "emilys", "password": "wrong_password_123"},
            timeout=10,
        )

        assert response.status_code == 400, (
            f"Ожидался статус 400, получен {response.status_code}"
        )

        body = response.json()
        assert "message" in body, "Тело ошибки должно содержать поле 'message'"
        assert body["message"], "Сообщение об ошибке не должно быть пустым"


class TestAuthMe:
    """GET /auth/me"""

    def test_get_current_user_with_valid_token(self, auth_headers):
        """
        Запрос /auth/me с валидным токеном должен вернуть 200 и профиль пользователя.
        """
        response = requests.get(
            f"{BASE_URL}/auth/me",
            headers=auth_headers,
            timeout=10,
        )

        assert response.status_code == 200

        body = response.json()
        assert body.get("username") == "emilys", (
            "Ответ содержит данные не того пользователя"
        )
        assert "email" in body, "Профиль пользователя должен содержать email"
        assert "id" in body, "Профиль пользователя должен содержать id"

    def test_get_current_user_without_token_returns_401(self):
        """
        Запрос /auth/me без токена должен вернуть 401.
        """
        response = requests.get(
            f"{BASE_URL}/auth/me",
            timeout=10,
        )

        assert response.status_code == 401, (
            f"Ожидался статус 401, получен {response.status_code}"
        )
