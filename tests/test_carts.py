"""
Тесты корзины: GET/POST/PUT/PATCH/DELETE /carts
"""

import requests
import pytest

BASE_URL = "https://dummyjson.com"
VALID_USER_ID = 1


class TestGetCartsByUser:
    """GET /carts/user/{userId}"""

    def test_returns_carts_list_for_valid_user(self):
        """
        Запрос корзин существующего пользователя должен вернуть 200
        и массив корзин с корректной структурой.
        """
        response = requests.get(
            f"{BASE_URL}/carts/user/{VALID_USER_ID}",
            timeout=10,
        )

        assert response.status_code == 200

        body = response.json()
        assert "carts" in body, "Ответ должен содержать поле 'carts'"
        assert isinstance(body["carts"], list), "'carts' должен быть массивом"
        assert len(body["carts"]) > 0, "У пользователя должна быть хотя бы одна корзина"

        first_cart = body["carts"][0]
        assert "id" in first_cart, "Корзина должна содержать 'id'"
        assert "products" in first_cart, "Корзина должна содержать 'products'"
        assert first_cart.get("userId") == VALID_USER_ID, (
            "userId в корзине не совпадает с запрошенным"
        )


class TestGetCartById:
    """GET /carts/{cartId}"""

    def test_returns_correct_cart_by_id(self, existing_cart_id):
        """
        Запрос корзины по существующему id должен вернуть 200
        и корзину с совпадающим id.
        """
        response = requests.get(
            f"{BASE_URL}/carts/{existing_cart_id}",
            timeout=10,
        )

        assert response.status_code == 200

        body = response.json()
        assert body.get("id") == existing_cart_id, (
            "id в ответе не совпадает с запрошенным"
        )
        assert "products" in body, "Корзина должна содержать 'products'"
        assert "total" in body, "Корзина должна содержать 'total'"

    def test_nonexistent_cart_id_returns_404(self):
        """
        Запрос несуществующей корзины должен вернуть 404.

        ФАКТИЧЕСКОЕ ПОВЕДЕНИЕ: DummyJSON возвращает 200 с пустым объектом или
        404 в зависимости от реализации. Тест фиксирует ожидаемый стандарт.
        """
        response = requests.get(
            f"{BASE_URL}/carts/99999",
            timeout=10,
        )

        assert response.status_code == 404, (
            f"Ожидался 404 для несуществующего cartId=99999, получен {response.status_code}. "
            "DummyJSON может возвращать иной статус — поведение задокументировано в README."
        )


class TestCreateCart:
    """POST /carts/add"""

    def test_create_cart_with_valid_products(self):
        """
        Создание корзины с валидными данными должно вернуть 201 (или 200)
        и корзину с переданными товарами.

        ПРИМЕЧАНИЕ: DummyJSON возвращает 200, а не 201.
        Тест принимает оба кода как допустимые для этого faux-API.
        """
        payload = {
            "userId": VALID_USER_ID,
            "products": [
                {"id": 1, "quantity": 2},
                {"id": 50, "quantity": 1},
            ],
        }

        response = requests.post(
            f"{BASE_URL}/carts/add",
            json=payload,
            timeout=10,
        )

        assert response.status_code in (200, 201), (
            f"Ожидался 200 или 201, получен {response.status_code}"
        )

        body = response.json()
        assert "id" in body, "Созданная корзина должна содержать 'id'"
        assert body.get("userId") == VALID_USER_ID, (
            "userId в созданной корзине не совпадает с отправленным"
        )

        returned_product_ids = {p["id"] for p in body.get("products", [])}
        assert 1 in returned_product_ids, "Товар с id=1 должен быть в корзине"


class TestUpdateCart:
    """PUT/PATCH /carts/{cartId}"""

    def test_update_cart_quantity(self, existing_cart_id):
        """
        PATCH корзины с новым количеством товара должен вернуть 200
        и отражать обновлённые данные в ответе.
        """
        payload = {
            "products": [
                {"id": 1, "quantity": 5},
            ],
        }

        response = requests.patch(
            f"{BASE_URL}/carts/{existing_cart_id}",
            json=payload,
            timeout=10,
        )

        assert response.status_code == 200

        body = response.json()
        assert body.get("id") == existing_cart_id, (
            "id в ответе не совпадает с обновляемой корзиной"
        )
        assert "products" in body, "Обновлённая корзина должна содержать 'products'"

        updated_product = next(
            (p for p in body["products"] if p["id"] == 1), None
        )
        assert updated_product is not None, "Товар id=1 должен быть в обновлённой корзине"
        assert updated_product.get("quantity") == 5, (
            f"Ожидалось quantity=5, получено {updated_product.get('quantity')}"
        )


class TestDeleteCart:
    """DELETE /carts/{cartId}"""

    def test_delete_existing_cart_returns_200(self, existing_cart_id):
        """
        Удаление существующей корзины должно вернуть 200 и признак isDeleted=True.

        ПРИМЕЧАНИЕ: DummyJSON — симулятор. Реального удаления не происходит,
        но API должен сообщить об успехе.
        """
        response = requests.delete(
            f"{BASE_URL}/carts/{existing_cart_id}",
            timeout=10,
        )

        assert response.status_code == 200

        body = response.json()
        assert body.get("isDeleted") is True, (
            "Ответ должен содержать isDeleted=true"
        )
        assert body.get("id") == existing_cart_id, (
            "id в ответе удалённой корзины должен совпадать с запрошенным"
        )


class TestCartNegative:
    """Негативные проверки для корзины"""

    def test_create_cart_with_zero_quantity_is_rejected_or_handled(self):
        """
        Создание корзины с quantity=0 — граничный случай.
        Ожидается либо 400 (валидация), либо что API хранит 0.
        Тест фиксирует фактическое поведение и проверяет,
        что ответ хотя бы является валидным JSON.

        ФАКТИЧЕСКОЕ ПОВЕДЕНИЕ: DummyJSON принимает quantity=0 и возвращает 200.
        Это нарушение бизнес-логики — в README описано как баг API.
        """
        payload = {
            "userId": VALID_USER_ID,
            "products": [{"id": 1, "quantity": 0}],
        }

        response = requests.post(
            f"{BASE_URL}/carts/add",
            json=payload,
            timeout=10,
        )

        # Фиксируем: ожидаем 400, но DummyJSON возвращает 200
        assert response.status_code in (200, 201, 400), (
            f"Неожиданный статус {response.status_code} для quantity=0"
        )

        if response.status_code == 200:
            pytest.xfail(
                "DummyJSON принимает quantity=0 без ошибки. "
                "Ожидалось: 400 Bad Request. "
                "Реальный API должен отклонять нулевое количество товара."
            )

    def test_update_nonexistent_cart_returns_404(self):
        """
        PATCH несуществующей корзины должен вернуть 404.
        """
        response = requests.patch(
            f"{BASE_URL}/carts/99999",
            json={"products": [{"id": 1, "quantity": 1}]},
            timeout=10,
        )

        assert response.status_code == 404, (
            f"Ожидался 404 для несуществующего cartId=99999, получен {response.status_code}"
        )
