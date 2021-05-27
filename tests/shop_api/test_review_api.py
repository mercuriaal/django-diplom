import pytest
from datetime import date
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
def test_retrieve(api_client, user_factory, product_factory, review_factory):
    user = user_factory()
    product = product_factory()
    review = review_factory(user=user, product=product)
    url = reverse("reviews-detail", args=[review.id])
    response = api_client.get(url)
    response_json = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert review.user.username == response_json['user']['username']
    assert review.product.id == response_json['product']


@pytest.mark.django_db
def test_list(api_client, review_factory):
    review = review_factory(_quantity=10)
    url = reverse("reviews-list")
    response = api_client.get(url)
    response_json = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert len(response_json) == 10


@pytest.mark.django_db
def test_unauth_create(api_client, user_factory, product_factory):
    product = product_factory()
    url = reverse("reviews-list")
    payload = {
        "product": product.id,
        "text": "Test review",
        "rating": 5
    }
    response = api_client.post(url, payload)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_auth_create(api_client, user_factory, product_factory, token_factory):
    user = user_factory()
    token = token_factory(user_id=user.id)
    product = product_factory()
    url = reverse("reviews-list")
    payload = {
        "product": product.id,
        "text": "Test review",
        "rating": 5
    }
    client = api_client
    client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    response = client.post(url, payload)
    response_json = response.json()
    assert response.status_code == status.HTTP_201_CREATED
    assert user.id == response_json['user']['id']
    assert product.id == response_json['product']


@pytest.mark.django_db
def test_update_other(api_client, user_factory, token_factory, review_factory):
    user = user_factory()
    token = token_factory(user_id=user.id)
    other_review = review_factory()
    url = reverse("reviews-detail", args=[other_review.id])
    payload = {
        "text": "changed text",
        "rating": 2
    }
    client = api_client
    client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    response = client.patch(url, payload)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_update_own(api_client, user_factory, token_factory, review_factory):
    user = user_factory()
    token = token_factory(user_id=user.id)
    own_review = review_factory(user=user)
    url = reverse("reviews-detail", args=[own_review.id])
    payload = {
        "text": "changed text",
        "rating": 2
    }
    client = api_client
    client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    response = client.patch(url, payload)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_destroy_other(api_client, user_factory, token_factory, review_factory):
    user = user_factory()
    token = token_factory(user_id=user.id)
    other_review = review_factory()
    url = reverse("reviews-detail", args=[other_review.id])
    client = api_client
    client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    response = client.delete(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_destroy_own(api_client, user_factory, token_factory, review_factory):
    user = user_factory()
    token = token_factory(user_id=user.id)
    own_review = review_factory(user=user)
    url = reverse("reviews-detail", args=[own_review.id])
    client = api_client
    client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    response = client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_filter_user_id(api_client, review_factory):
    reviews = review_factory(_quantity=10)
    test_id = reviews[5].user.id
    url = reverse("reviews-list")
    payload = {
        "user": test_id
    }
    response = api_client.get(url, payload)
    response_json = response.json()
    assert len(response_json) == 1
    assert response.data[0]['user']['id'] == test_id


@pytest.mark.django_db
def test_filter_product_id(api_client, review_factory):
    reviews = review_factory(_quantity=10)
    test_id = reviews[5].product.id
    url = reverse("reviews-list")
    payload = {
        "product": test_id
    }
    response = api_client.get(url, payload)
    response_json = response.json()
    assert len(response_json) == 1
    assert response.data[0]['product'] == test_id


@pytest.mark.django_db
def test_filter_date(api_client, review_factory):
    reviews = review_factory()
    test_date = reviews.created_at
    url = reverse("reviews-list")
    payload = {
        "created_at": test_date
    }
    response = api_client.get(url, payload)
    response_json = response.json()
    assert len(response_json) == 1
    assert date.fromisoformat(response.data[0]['created_at']) == test_date
