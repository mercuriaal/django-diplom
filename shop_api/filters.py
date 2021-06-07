from django_filters import rest_framework as filters
from .models import Review, Order


class ProductFilter(filters.FilterSet):

    price = filters.RangeFilter()
    name = filters.CharFilter(field_name="name", lookup_expr="icontains")
    description = filters.CharFilter(field_name="description", lookup_expr="icontains")


class ReviewFilter(filters.FilterSet):

    class Meta:
        model = Review
        fields = ["user", "product", "created_at"]


class OrderFilter(filters.FilterSet):

    price = filters.RangeFilter(field_name='total_price')
    ordered_products = filters.NumberFilter(field_name='ordered_products', method='products_filter')
    creation = filters.DateFromToRangeFilter(field_name='created_at')
    update = filters.DateFromToRangeFilter(field_name='updated_at')

    class Meta:
        model = Order
        fields = ["status", "created_at", "updated_at"]

    def products_filter(self, queryset, name, value):
        query = queryset.filter(ordered_products__product=value)
        return query
