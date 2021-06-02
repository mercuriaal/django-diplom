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
    positions = filters.NumberFilter(field_name='positions', method='products_filter')

    class Meta:
        model = Order
        fields = ["status", "created_at", "updated_at"]

    def products_filter(self, queryset, name, value):
        query = queryset.filter(positions__contains=[{"product":int(value)}])
        return query
