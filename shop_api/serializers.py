from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Product, Review, Order, OrderedProducts, Collection


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name',
                  'last_name']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'created_at', 'updated_at']

    def validate_price(self, data):
        if data < 0:
            raise serializers.ValidationError('Цена не может быть негативной')
        return data


class ReviewSerializer(serializers.ModelSerializer):

    user = UserSerializer(
        read_only=True
    )

    class Meta:
        model = Review
        fields = ['user', 'product', 'text', 'rating', 'created_at', 'updated_at']

    def create(self, validated_data):

        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)

    def validate(self, data):
        user = self.context["request"].user
        product = data.get("product")
        check_duplicate = Review.objects.filter(user=user, product=product)
        if check_duplicate.exists():
            raise serializers.ValidationError('Нельзя оставлять более одного отзыва.')
        return data


class OrderedProductsSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderedProducts
        exclude = ['order']


class OrderSerializer(serializers.ModelSerializer):

    ordered_products = OrderedProductsSerializer(
        many=True
    )

    user = UserSerializer(
        read_only=True
    )

    class Meta:
        model = Order
        fields = ['user', 'status', 'total_price', 'positions', 'created_at', 'updated_at', 'ordered_products']

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user

        order_price = 0
        for position in validated_data['ordered_products']:
            queryset = Product.objects.filter(id=position['product'].id).values('price')
            product_price = queryset[0]['price']
            order_price += product_price * position['quantity']
        validated_data["total_price"] = order_price

        positions = validated_data.pop('ordered_products')
        order = Order.objects.create(**validated_data)
        for position in positions:
            OrderedProducts.objects.create(order=order, **position)
        return order

    def validate_ordered_products(self, data):
        for position in data:
            quantity = position.get('quantity')
            if quantity == 0:
                raise serializers.ValidationError('Количество товаров не может быть равным нулю')
        return data


class CollectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Collection
        fields = ['title', 'text', 'products', 'created_at', 'updated_at']
