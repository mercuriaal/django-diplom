from django_filters import rest_framework as filters
from .models import Product, Review, Order


class ProductFilter(filters.FilterSet):

    price = filters.RangeFilter()
    name = filters.CharFilter(field_name="name", lookup_expr="icontains")
    description = filters.CharFilter(field_name="description", lookup_expr="icontains")

    class Meta:
        model = Product
        fields = ["price", "name", "description"]


class ReviewFilter(filters.FilterSet):

    user = filters.NumberFilter(field_name="user", lookup_expr="exact")
    product = filters.NumberFilter(field_name="product", lookup_expr="exact")
    creation = filters.DateFilter()

    class Meta:
        model = Review
        fields = ["user", "product", "creation"]


class OrderFilter(filters.FilterSet):

    STATUS_CHOICES = [
        ('NEW', 'Новый'),
        ('IN_PROGRESS', 'В работе'),
        ('DONE', 'Выполнен')
    ]

    status = filters.ChoiceFilter(choices=STATUS_CHOICES)
    price = filters.RangeFilter()
    created = filters.DateFilter()
    updated = filters.DateFilter()
    products = filters.MultipleChoiceFilter()  # разобраться

    class Meta:
        model = Order
        fields = ["status", "price", "created", "updated"]
