from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser, SAFE_METHODS
from django_filters.rest_framework import DjangoFilterBackend

from .filters import ProductFilter, ReviewFilter, OrderFilter
from .models import Product, Review, Order, Collection
from .serializers import ProductSerializer, ReviewSerializer, OrderSerializer, CollectionSerializer
from .permissions import IsOwnerOrAdmin


class ProductViewSet(ModelViewSet):

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminUser()]
        return []


class ReviewViewSet(ModelViewSet):

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ReviewFilter

    def get_permissions(self):
        if self.action in ["create"]:
            return [IsAuthenticated()]
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsOwnerOrAdmin()]
        return []


class OrderViewSet(ModelViewSet):

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = OrderFilter

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsOwnerOrAdmin()]
        if self.action in ["create"]:
            return [IsAuthenticated()]
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAdminUser()]
        return []


class CollectionViewSet(ModelViewSet):

    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer

    def get_permissions(self):
        if self.action not in SAFE_METHODS:
            return [IsAdminUser()]
        else:
            return True
