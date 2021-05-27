import pytest
from django.urls import reverse
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_403_FORBIDDEN, HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_retrieve(api_client, product_factory):
    product = product_factory()
    url = reverse("products-detail", args=[product.id])
    response = api_client.get(url)
    response_json = response.json()
    assert response.status_code == HTTP_200_OK
    assert product.name == response_json['name']


@pytest.mark.django_db
def test_list(api_client, product_factory):
    products = product_factory(_quantity=10)
    url = reverse("products-list")
    response = api_client.get(url)
    response_json = response.json()
    assert response.status_code == HTTP_200_OK
    assert len(products) == len(response_json)


@pytest.mark.parametrize(
    ["min_value", "max_value", "expected_quantity"],
    (
        (0, 1000, 3),
        (99, 101, 1),
        (250, 600, 2),
        (0, 99, 0)
    )
)
@pytest.mark.django_db
def test_price_filter(api_client, product_factory, min_value, max_value, expected_quantity):
    min_price_product = product_factory(price=100)
    middle_price_product = product_factory(price=300)
    max_price_product = product_factory(price=500)
    url = reverse("products-list")
    payload = {
        "price_min": min_value,
        "price_max": max_value
    }
    response = api_client.get(url, payload)
    response_json = response.json()
    assert response.status_code == HTTP_200_OK
    assert len(response_json) == expected_quantity


@pytest.mark.parametrize(
    ["search_field", "search_example", "expected_quantity"],
    (
        ("name", "test", 1),
        ("name", "product", 1),
        ("name", "Test_product", 1),
        ("name", "Something_else", 0),
        ("description", "test", 1),
        ("description", "some random description which im going to test", 1),
        ("description", "im going", 1),
        ("description", "this one should not work", 0),
    )
)
@pytest.mark.django_db
def test_text_filter(api_client, product_factory, search_example, expected_quantity, search_field):
    product = product_factory(name="test_product", description="some random description which im going to test")
    url = reverse("products-list")
    payload = {
        search_field: search_example
    }
    response = api_client.get(url, payload)
    response_json = response.json()
    assert response.status_code == HTTP_200_OK
    assert len(response_json) == expected_quantity


@pytest.mark.parametrize(
    ["is_admin", "http_response"],
    (
        (True, HTTP_201_CREATED),
        (False, HTTP_403_FORBIDDEN)
    )
)
@pytest.mark.django_db
def test_create(api_client, user_factory, token_factory, is_admin, http_response):
    user = user_factory(is_staff=is_admin)
    token = token_factory(user_id=user.id)
    url = reverse("products-list")
    payload = {
        "name": "Test_product",
        "price": 100
    }
    client = api_client
    client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    response = client.post(url, payload)
    assert response.status_code == http_response


@pytest.mark.parametrize(
    ["is_admin", "http_response"],
    (
        (True, HTTP_200_OK),
        (False, HTTP_403_FORBIDDEN)
    )
)
@pytest.mark.django_db
def test_update(api_client, product_factory, user_factory, token_factory, is_admin, http_response):
    user = user_factory(is_staff=is_admin)
    token = token_factory(user_id=user.id)
    product = product_factory()
    url = reverse("products-detail", args=[product.id])
    payload = {
        "price": 100
    }
    client = api_client
    client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    response = client.patch(url, payload)
    assert response.status_code == http_response


@pytest.mark.parametrize(
    ["is_admin", "http_response"],
    (
        (True, HTTP_204_NO_CONTENT),
        (False, HTTP_403_FORBIDDEN)
    )
)
@pytest.mark.django_db
def test_destroy(api_client, product_factory, user_factory, token_factory, is_admin, http_response):
    user = user_factory(is_staff=is_admin)
    token = token_factory(user_id=user.id)
    product = product_factory()
    url = reverse("products-detail", args=[product.id])
    client = api_client
    client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    response = client.delete(url)
    assert response.status_code == http_response


