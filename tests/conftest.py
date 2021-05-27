import pytest
from rest_framework.test import APIClient
from model_bakery import baker


@pytest.fixture()
def api_client():
    return APIClient()


@pytest.fixture()
def user_factory():
    def factory(**kwargs):
        return baker.make("User", **kwargs)
    return factory


@pytest.fixture()
def token_factory():
    def factory(**kwargs):
        return baker.make("Token", **kwargs)
    return factory


@pytest.fixture()
def product_factory():
    def factory(**kwargs):
        return baker.make("Product", **kwargs)
    return factory


@pytest.fixture()
def review_factory():
    def factory(**kwargs):
        return baker.make("Review", **kwargs)
    return factory
