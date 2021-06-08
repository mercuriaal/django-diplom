import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
def test_retrieve(api_client, collection_factory):
    target_collection = collection_factory()
    other_collections = collection_factory(_quantity=10)
    url = reverse('collections-detail', args=[target_collection.id])
    response = api_client.get(url)
    repsonse_json = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(repsonse_json, dict)
    assert repsonse_json['title'] == target_collection.title


@pytest.mark.django_db
def test_list(api_client, collection_factory):
    collections = collection_factory(_quantity=10)
    url = reverse('collections-list')
    response = api_client.get(url)
    response_json = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert len(response_json) == 10


@pytest.mark.parametrize(
    ["admin_user", "http_response"],
    (
        (True, status.HTTP_201_CREATED),
        (False, status.HTTP_403_FORBIDDEN)
    )
)
@pytest.mark.django_db
def test_create_permission(api_client, user_factory, token_factory, product_factory, admin_user, http_response):
    user = user_factory(is_staff=admin_user)
    token = token_factory(user_id=user.id)
    product = product_factory()
    url = reverse('collections-list')
    payload = {
        "title": "test collection",
        "text": "text",
        "products": [product.id]
    }
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    response = api_client.post(url, payload)
    assert response.status_code == http_response


@pytest.mark.parametrize(
    ["admin_user", "http_response"],
    (
        (True, status.HTTP_200_OK),
        (False, status.HTTP_403_FORBIDDEN)
    )
)
@pytest.mark.django_db
def test_update_permission(api_client, user_factory, token_factory, admin_user, http_response, collection_factory):
    user = user_factory(is_staff=admin_user)
    token = token_factory(user_id=user.id)
    collection = collection_factory()
    url = reverse('collections-detail', args=[collection.id])
    payload = {
        "title": "test title update",
        "text": "test text update",
    }
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    response = api_client.patch(url, payload)
    assert response.status_code == http_response


@pytest.mark.parametrize(
    ["admin_user", "http_response"],
    (
        (True, status.HTTP_204_NO_CONTENT),
        (False, status.HTTP_403_FORBIDDEN)
    )
)
@pytest.mark.django_db
def test_delete_permission(api_client, user_factory, token_factory, admin_user, http_response, collection_factory):
    user = user_factory(is_staff=admin_user)
    token = token_factory(user_id=user.id)
    collection = collection_factory()
    url = reverse('collections-detail', args=[collection.id])
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    response = api_client.delete(url)
    assert response.status_code == http_response
