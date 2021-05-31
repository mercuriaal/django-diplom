from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Product, Review, Order, Collection


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
        if check_duplicate.count() > 1:
            raise serializers.ValidationError('Нельзя оставлять более одного отзыва.')
        return data


class OrderSerializer(serializers.ModelSerializer):

    user = UserSerializer(
        read_only=True
    )

    class Meta:
        model = Order
        fields = ['user', 'status', 'total_price', 'positions', 'created_at', 'updated_at']

    def create(self, validated_data):
        order_price = 0
        for position in validated_data['positions']:
            queryset = Product.objects.filter(id=position['product']).values('price')
            product_price = queryset[0]['price']
            order_price += product_price * position['quantity']
        validated_data["total_price"] = order_price
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)

    def validate_positions(self, data):
        if not data:
            raise serializers.ValidationError('Заказ не может быть пустым')
        for position in data:
            product_id = position.get('product')
            quantity = position.get('quantity')
            if isinstance(product_id, int) is False or product_id is None:
                raise serializers.ValidationError('В позиции неправильно указан товар')
            if isinstance(quantity, int) is False or quantity is None or quantity == 0:
                raise serializers.ValidationError('В позиции неправильно указано количество товара')
        return data


class CollectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Collection
        fields = ['title', 'text', 'products', 'created_at', 'updated_at']
