import pytest
from django.urls import reverse
from rest_framework import status

from shop_api.models import Order


@pytest.mark.django_db
def test_retrieve_positive(api_client, order_factory, user_factory, token_factory):
    user = user_factory()
    token = token_factory(user_id=user.id)
    order = order_factory(user=user)
    url = reverse("orders-detail", args=[order.id])
    client = api_client
    client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    response = client.get(url)
    response_json = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert len(response_json) == 1
    assert response_json['user']['id'] == user.id


@pytest.mark.parametrize(
    ["admin_status", "http_response"],
    (
        (True, status.HTTP_200_OK),
        (False, status.HTTP_403_FORBIDDEN)
    )
)
@pytest.mark.django_db
def test_retrieve_permissions(api_client, order_factory, user_factory, admin_status, http_response, token_factory):
    user = user_factory(is_staff=admin_status)
    token = token_factory(user_id=user.id)
    order = order_factory()
    url = reverse("orders-detail", args=[order.id])
    client = api_client
    client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    response = client.get(url)
    assert response.status_code == http_response


@pytest.mark.parametrize(
    ["admin_status", "owned_orders_quantity", "other_orders_quantity", "expected_response_length"],
    (
        (True, 1, 10, 11),
        (True, 5, 10, 15),
        (False, 1, 10, 1),
        (False, 5, 10, 5),
    )
)
@pytest.mark.django_db
def test_list_positive(api_client, order_factory, user_factory, token_factory, admin_status, owned_orders_quantity,
                       other_orders_quantity, expected_response_length):
    user = user_factory(is_staff=admin_status)
    token = token_factory(user_id=user.id)
    owned_orders = order_factory(_quantity=owned_orders_quantity, user=user)
    other_orders = order_factory(_quantity=other_orders_quantity)
    url = reverse("orders-list")
    client = api_client
    client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    response = client.get(url)
    response_json = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert len(response_json) == expected_response_length


@pytest.mark.django_db
def test_list_auth_permission(api_client, order_factory):
    order = order_factory()
    url = reverse("orders-list")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    ["test_product_quantity", "http_response"],
    (
            (10, status.HTTP_201_CREATED),
            (0, status.HTTP_400_BAD_REQUEST)
    )
)
@pytest.mark.django_db
def test_create_validations(api_client, user_factory, token_factory, product_factory,
                            test_product_quantity, http_response):
    user = user_factory()
    product = product_factory()
    token = token_factory(user_id=user.id)
    url = reverse("orders-list")
    payload = {
        "ordered_products": [
            {
                "product": product.id,
                "quantity": test_product_quantity
            }
        ]
    }
    client = api_client
    client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    response = client.post(url, payload, format='json')
    assert response.status_code == http_response


@pytest.mark.django_db
def test_create_auth_permission(api_client, order_factory, product_factory):
    product = product_factory()
    url = reverse("orders-list")
    payload = {
        "ordered_products": [
            {
                "product": product.id,
                "quantity": 5
            }
        ]
    }
    response = api_client.post(url, payload, format='json')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    ["admin_status", "http_response"],
    (
        (True, status.HTTP_200_OK),
        (False, status.HTTP_403_FORBIDDEN)
    )
)
@pytest.mark.django_db
def test_update_status_permissions(api_client, user_factory, token_factory, order_factory,
                                   admin_status, http_response):
    user = user_factory(is_staff=admin_status)
    token = token_factory(user_id=user.id)
    order = order_factory()
    url = reverse("orders-detail", args=[order.id])
    payload = {
        "status": "DONE"
    }
    client = api_client
    client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    response = client.patch(url, payload)
    assert response.status_code == http_response


@pytest.mark.parametrize(
    ["admin_status", "http_response"],
    (
        (True, status.HTTP_204_NO_CONTENT),
        (False, status.HTTP_403_FORBIDDEN)
    )
)
@pytest.mark.django_db
def test_destroy(api_client, order_factory, user_factory, token_factory, admin_status, http_response):
    user = user_factory(is_staff=admin_status)
    token = token_factory(user_id=user.id)
    order = order_factory()
    url = reverse("orders-detail", args=[order.id])
    client = api_client
    client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    response = client.delete(url)
    assert response.status_code == http_response


@pytest.mark.parametrize(
    ["search_example", "expected_quantity"],
    (
        ("NEW", 2),
        ("IN_PROGRESS", 3),
        ("DONE", 4)
    )
)
@pytest.mark.django_db
def test_status_filter(api_client, user_factory, token_factory, order_factory, search_example,
                       expected_quantity):
    user = user_factory()
    token = token_factory(user_id=user.id)
    order_factory(_quantity=2, user=user)
    order_factory(_quantity=3, status="IN_PROGRESS", user=user)
    order_factory(_quantity=4, status="DONE", user=user)
    url = reverse("orders-list")
    payload = {
        "status": search_example
    }
    client = api_client
    client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    response = client.get(url, payload)
    response_json = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert len(response_json) == expected_quantity


@pytest.mark.parametrize(
    ["test_payload", "expected_quantity"],
    (
        ({"price_min": 50}, 3),
        ({"price_min": 101}, 2),
        ({"price_min": 99, "price_max": 1001}, 3),
        ({"price_min": 501, "price_max": 999}, 0),
        ({"price_min": 50, "price_max": 600}, 2),
        ({"price_max": 1001}, 3),
        ({"price_max": 99}, 0)
    )
)
@pytest.mark.django_db
def test_price_filter(api_client, user_factory, token_factory, order_factory, test_payload,
                      expected_quantity):
    user = user_factory()
    token = token_factory(user_id=user.id)
    order_factory(user=user, total_price=100)
    order_factory(user=user, total_price=500)
    order_factory(user=user, total_price=1000)
    url = reverse("orders-list")
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    response = api_client.get(url, test_payload)
    response_json = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert len(response_json) == expected_quantity


@pytest.mark.parametrize(
    ["test_payload", "expected_quantity"],
    (
        ({"creation_before": '2021-07-01'}, 3),
        ({"creation_before": '2021-05-01'}, 2),
        ({"creation_before": '2021-01-01'}, 1),
        ({"creation_before": '2020-12-30'}, 0),
        ({"creation_after": '2021-07-01'}, 0),
        ({"creation_after": '2021-05-01'}, 1),
        ({"creation_after": '2021-01-01'}, 2),
        ({"creation_after": '2020-12-30'}, 3),
        ({"update_before": '2021-07-01'}, 3),
        ({"update_before": '2021-05-01'}, 2),
        ({"update_before": '2021-01-01'}, 1),
        ({"update_after": '2021-07-01'}, 0),
        ({"update_after": '2021-05-01'}, 1),
        ({"update_after": '2021-01-01'}, 2),
        ({"creation_after": '2020-11-30', "creation_before": '2021-07-01'}, 3),
        ({"creation_after": '2021-01-01', "creation_before": '2021-07-01'}, 2),
        ({"creation_after": '2021-04-01', "creation_before": '2021-07-01'}, 1),
        ({"creation_after": '2020-04-01', "creation_before": '2020-07-01'}, 0),
        ({"update_after": '2020-11-30', "update_before": '2021-07-01'}, 3),
        ({"update_after": '2021-01-01', "update_before": '2021-07-01'}, 2),
        ({"update_after": '2021-04-01', "update_before": '2021-07-01'}, 1),
        ({"update_after": '2020-04-01', "update_before": '2020-07-01'}, 0)
    )
)
@pytest.mark.django_db
def test_dates_filter(api_client, user_factory, token_factory, order_factory, test_payload, expected_quantity):
    user = user_factory()
    token = token_factory(user_id=user.id)
    order1 = Order.objects.create(user=user)
    Order.objects.filter(id=order1.id).update(created_at='2021-06-01', updated_at='2021-06-02')
    order2 = order_factory(user=user)
    Order.objects.filter(id=order2.id).update(created_at='2021-01-20', updated_at='2021-02-05')
    order3 = order_factory(user=user)
    Order.objects.filter(id=order3.id).update(created_at='2020-12-31', updated_at='2020-12-31')
    url = reverse("orders-list")
    client = api_client
    client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    response = client.get(url, test_payload)
    response_json = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert len(response_json) == expected_quantity


@pytest.mark.django_db
def test_positions_filter(api_client, user_factory, token_factory, order_factory, product_factory):
    user = user_factory()
    token = token_factory(user_id=user.id)
    product = product_factory()
    other_order = order_factory(user=user, _quantity=10)
    target_order = order_factory(user=user, ordered_products__product=product)

    url = reverse("orders-list")
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    payload = {
        "ordered_products": product.id
    }
    response = api_client.get(url, payload)
    response_json = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert len(response_json) == 1
    assert response_json[0]['ordered_products'][0]['product'] == product.id
