from rest_framework import serializers
from .models import MenuItem, Category, Cart, Order, OrderItem
from django.contrib.auth.models import User

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['slug', 'title']

class MenuItemSerializer(serializers.Serializer):
    title = serializers.CharField()
    price = serializers.IntegerField()
    featured = serializers.BooleanField()
    category = CategorySerializer()
    class Meta:
        model = MenuItem
        fields = ['title', 'price', 'featured', 'category']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class CartSerializer(serializers.Serializer):
    user = UserSerializer()
    menuitem = serializers.CharField()
    quantity = serializers.IntegerField()
    unit_price = serializers.DecimalField(max_digits=6, decimal_places=2)
    total_price = serializers.SerializerMethodField(method_name='calculate_total_price')
    class Meta:
        model = Cart
        fields = ['user', 'menuitem', 'quantity', 'unit_price', 'total_price']
    def calculate_total_price(self, cart):
        return cart.menuitem.price * cart.quantity

class OrderSerializer(serializers.Serializer):
    user = UserSerializer()
    delivery_crew = serializers.CharField()
    status = serializers.BooleanField()
    total = serializers.DecimalField(max_digits=6, decimal_places=2)
    date = serializers.DateField()
    class Meta:
        model = Order
        fields = ['user', 'delivery_crew', 'status', 'total', 'date']

class OrderItemSerializer(serializers.Serializer):
    order = UserSerializer()
    menuitem = serializers.Serializer()
    quantity = serializers.IntegerField()
    unit_price = serializers.DecimalField(max_digits=6, decimal_places=2)
    price = serializers.Serializer()
    class Meta:
        model = Cart
        fields = ['order', 'menuitem', 'quantity', 'unit_price', 'price']
