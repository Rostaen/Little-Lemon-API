from django.db import transaction
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User, Group
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from decimal import Decimal
from datetime import date
from .models import MenuItem, Category, Cart, Order, OrderItem
from .serializers import MenuItemSerializer, CategorySerializer, UserSerializer, CartSerializer, OrderSerializer, OrderItemSerializer
from .permissions import IsInGroup

@api_view(['GET','POST'])
@permission_classes([IsAuthenticated, IsInGroup])
def manager(request):
    if request.method == 'GET':
        # Get the Manager group
        manager_group = Group.objects.get(name="Manager")
        # Get all users in the Manager group
        manager = manager_group.user_set.all()
        serialized_manager = UserSerializer(manager, many=True)
        return Response(serialized_manager.data)
    elif request.method == 'POST':
        # Getting username from request
        username = request.data.get('username')
        if username:
            try:
                # Check if user is in the database
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                # Create a new user in the database
                user = User.objects.create(username=username)
                # Get the Manager group
                managers = Group.objects.get(name="Manager")
                # Add the user to the Manager group
                managers.user_set.add(user)
                return Response({"message": f"Added {username} to the Manager Group"}, status.HTTP_201_CREATED)
            return Response({"message": f"User: {username} already exists and wasn't added"}, status.HTTP_302_FOUND)
        return Response({"message": "There was an error with your request"}, status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsInGroup])
def manager_delete_user(request, id):
    if request.method == 'DELETE':
        # Getting username from request
        username = get_object_or_404(User, pk=id)
        if username:
            try:
                # Checking for username in database
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response({"message": f"User: {username} does not exist in the database"}, status.HTTP_404_NOT_FOUND)
            # Deleting the user
            user.delete()
            return Response({"message": f"Username {username} was deleted from the database"}, status.HTTP_200_OK)
        return Response({"message": "User does not exist"}, status.HTTP_404_NOT_FOUND)
    return Response({"message": "For GET/POST please use group view"}, status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def menu_items(request):
    if request.method == 'GET':
        items = MenuItem.objects.select_related('category').all()
        # category_name = request.query_params.get('category')
        # title = request.query_params.get('title')
        # price = request.query_params.get('price')
        # featured = request.query_params.get('featured')

        # Build filtered view here later

        # ------------------------------

        # Build querying here later if needed

        # -----------------------------------

        serialized_item = MenuItemSerializer(items, many=True)
        return Response(serialized_item.data)
    else:
        # Getting user making request
        user = request.user
        # Checking if user is Manager/Admin
        if user.groups.filter(name__in=['Manager']).exists() or request.user.is_superuser:
            if request.method == 'POST':
                # Getting request fields
                title = request.data.get('title')
                price = request.data.get('price')
                featured = request.data.get('featured')
                category_id = request.data.get('category')
                # Checking if fields are present
                if title and price and category_id:
                    # Checking in category exists
                    category = Category.objects.filter(title=category_id).first()
                    if category:
                        # Create menu item
                        MenuItem.objects.create(
                            title=title,
                            price=price,
                            featured=featured,
                            category=category
                        )
                        return Response({"message": f"Menu item {title} was created"}, status.HTTP_201_CREATED)
                    else:
                        return Response({"message": f"Category {category_id} does not exist"}, status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"message": "Title, price, and category are required fields"}, status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"message": "For PUT/PATCH/DELETE please use single menu item URL"}, status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message", "Access Denied"}, status.HTTP_403_FORBIDDEN)

@api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def single_menu_item(request, id):
    item = get_object_or_404(MenuItem, pk=id)
    if request.method == 'GET':
        # Displaying a menu item by ID
        serialized_item = MenuItemSerializer(item)
        return Response(serialized_item.data)
    else:
        # Getting user making request
        user = request.user
        # Checking if user is Manager/Admin
        if user.groups.filter(name__in=['Manager']).exists() or request.user.is_superuser:
            if request.method == 'POST':
                # Getting request fields
                title = request.data.get('title')
                price = request.data.get('price')
                featured = request.data.get('featured')
                category_id = request.data.get('category')
                # Checking if fields are present
                if title and price and category_id:
                    # Checking in category exists
                    category = Category.objects.filter(title=category_id).first()
                    if category:
                        # Create menu item
                        MenuItem.objects.create(
                            title=title,
                            price=price,
                            featured=featured,
                            category=category
                        )
                        return Response({"message": f"Menu item {title} was created"}, status.HTTP_201_CREATED)
                    else:
                        return Response({"message": f"Category {category_id} does not exist"}, status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"message": "Title, price, and category are required fields"}, status.HTTP_400_BAD_REQUEST)
            elif request.method in ['PUT', 'PATCH']:
                # Checking over each item dynamically
                for key, value in request.data.items():
                    if key == 'featured':
                        value = value.capitalize()
                    if key == 'category':
                        value = Category.objects.filter(title=value).first()
                    setattr(item, key, value)
                item.save()
                return Response({"message": f"Menu item {id} updated successfully"}, status.HTTP_202_ACCEPTED)
            elif request.method == 'DELETE':
                item.delete()
                return Response({"message", f"Item {item.title} was successfully deteled"}, status.HTTP_200_OK)
        else:
            return Response({"message": "Permission Denied"}, status.HTTP_403_FORBIDDEN)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsInGroup])
def categories(request):
    if request.method == 'GET':
        # Grabbing all items for Category Model
        categories = Category.objects.all()
        #title = request.query_params.get('title')
        #slug = request.query_params.get('slug')

        # Build filtered view here later

        # ------------------------------

        # Build querying here later if needed

        # -----------------------------------

        # Serializing categories for display
        serialized_category = CategorySerializer(categories, many=True)
        return Response(serialized_category.data)
    elif request.method == 'POST':
        # Getting title from request
        title = request.data.get('title')
        if title:
            # Checking if the Category already exists
            category = Category.objects.filter(title=title).first()
            if category:
                return Response({"message": f"Category {title} already exists"}, status.HTTP_302_FOUND)
            else:
                # Creating the category
                slug = title.lower().replace(" ", "-")
                Category.objects.create(
                    slug=slug,
                    title=title
                )
                return Response({"message": f"Category {title} was created"}, status.HTTP_201_CREATED)
        else:
            return Response({"message": "Title is a required fields"}, status.HTTP_400_BAD_REQUEST)

    return Response({"message": "There was an error with your request"}, status.HTTP_400_BAD_REQUEST)

@api_view(['GET','POST'])
@permission_classes([IsAuthenticated, IsInGroup])
def delivery_crew(request):
    if request.method == 'GET':
        # Get the Manager group
        delivery_crew_group = Group.objects.get(name="Delivery Crew")
        # Get all users in the Manager group
        delivery_crew = delivery_crew_group.user_set.all()
        serialized_delivery_crew = UserSerializer(delivery_crew, many=True)
        return Response(serialized_delivery_crew.data)
    elif request.method == 'POST':
        # Getting username from request
        username = request.data.get('username')
        if username:
            try:
                # Check if user is in the database
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                # Create a new user in the database
                user = User.objects.create(username=username)
                # Get the delivery crew group
                delivery_crew = Group.objects.get(name="Delivery Crew")
                # Add the user to the delivery crew group
                delivery_crew.user_set.add(user)
                return Response({"message": f"Added {username} to the Delivery Crew Group"}, status.HTTP_201_CREATED)
            return Response({"message": f"User: {username} already exists and wasn't added"}, status.HTTP_302_FOUND)
    return Response({"message": "There was an error with your request"}, status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsInGroup])
def delivery_crew_delete_user(request, id):
    if request.method == 'DELETE':
        # Getting username from request
        username = get_object_or_404(User, pk=id)
        if username:
            try:
                # Checking for username in database
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response({"message": f"User: {username} does not exist in the database"}, status.HTTP_404_NOT_FOUND)
            # Deleting the user
            user.delete()
            return Response({"message": f"Username {username} was deleted from the database"}, status.HTTP_200_OK)
        return Response({"message": "User does not exist"}, status.HTTP_404_NOT_FOUND)
    return Response({"message": "For GET/POST please use group view"}, status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def cart_management(request):
    user = request.user
    cart = Cart.objects.filter(user=user)
    if request.method == 'GET':
        serialized_cart = CartSerializer(cart, many=True)
        return Response(serialized_cart.data)
    elif request.method == 'POST':
        menu_item_title = request.data.get('menu item')
        try:
            menu_item = MenuItem.objects.get(title=menu_item_title)
        except MenuItem.DoesNotExist:
            return Response({"message": f"{menu_item} does not exist in our menu"}, status.HTTP_400_BAD_REQUEST)
        quantity = int(request.data.get('quantity', 0))
        unit_price = Decimal(menu_item.price)
        total_price = unit_price * quantity
        Cart.objects.create(
            user=user,
            menuitem=menu_item,
            quantity=quantity,
            unit_price=unit_price,
            price=total_price
        )
        return Response({"message": f"{menu_item_title} was added to the cart"}, status.HTTP_200_OK)
    elif request.method == 'DELETE':
        cart.delete()
        return Response({"message": "Your cart has been emptied"}, status.HTTP_200_OK)
    else:
        return Response({"message": "PUT/PATCH/OPTIONS/HEAD not supported"}, status.HTTP_403_FORBIDDEN)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def order_management(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user)

    if request.method == 'GET':
        if user.groups.filter(name__in=['Manager']).exists() or request.user.is_superuser:
            order = Order.objects.all()
            if order.exists():
                # order_items = OrderItem.objects.all()
                serialized_orders = OrderSerializer(order, many=True)
                # serialized_order_items = OrderItemSerializer(order_items)
                return Response(serialized_orders.data)
            else:
                return Response({"message": f"No orders found"}, status.HTTP_404_NOT_FOUND)
        else:
            user_order = Order.objects.filter(user=user)
            if user_order.exists():
                #customer_order = Order.objects.filter(user=user)
                serialized_user_orders = OrderSerializer(user_order, many=True)
                #serialized_order = OrderSerializer(customer_order)
                user_order_items = OrderItem.objects.filter(order__in=user_order)
                serialized_user_order_items = OrderItemSerializer(user_order_items, many=True)
                return Response({
                    "orders": serialized_user_orders.data,
                    "order_items": serialized_user_order_items.data
                })
            else:
                return Response({"message": f"No order found for {user}"}, status.HTTP_404_NOT_FOUND)
    elif request.method == 'POST':
        try:
            with transaction.atomic():
                order_items = []
                cart_total = 0
                # Transfering cart to order items
                for cart_item in cart_items:
                    order_items.append(OrderItem(
                        order=None,
                        menuitem=cart_item.menuitem,
                        quantity=cart_item.quantity,
                        unit_price=cart_item.unit_price,
                        price=cart_item.price
                    ))
                    cart_total += cart_item.price
                # Creating an order linked to order items
                order = Order.objects.create(
                    user=user,
                    delivery_crew=None,
                    status=False,
                    total=cart_total,
                    date=date.today()
                )
                # Setting the order for the order items
                OrderItem.objects.filter(
                    order=None,
                    menuitem__in=[item.menuitem for item in cart_items]
                ).update(order=order)
                # Deleting cart items
                cart_items.delete()
                return Response({"message": "Your order is being prepared"}, status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": f"Error processing order: {str(e)}"}, status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response({"message": "Error with requested method, try again"}, status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def order_id_management(request, id):
    current_user = request.user
    user = get_object_or_404(User, pk=id)
    if request.method == 'GET':
        # Checking if order and current user match
        if current_user == user:
            # Displaying order for user
            user_order = Order.objects.filter(user = current_user)
            serialize_order = OrderSerializer(user_order, many=True)
            user_items = OrderItem.objects.filter(order__in=user_order)
            serialize_items = OrderItemSerializer(user_items, many=True)
            return Response({
                    "orders": serialize_order.data,
                    "order_items": serialize_items.data
            })
        else:
            return Response({"message": "Only the owner of this order may view the contents"}, status.HTTP_403_FORBIDDEN)
    elif request.method in ['PUT', 'PATCH']:
        user_order = get_object_or_404(Order, pk=id)
        if current_user.groups.filter(name__in=['Manager']).exists() or request.user.is_superuser:
            # Implement updating delivery crew here
            delivery_crew = request.data.get('delivery crew')
            user_order.delivery_crew = delivery_crew
            user_order.save()
            return Response({"message": f"{delivery_crew} has been added to Order ID: {id}"}, status.HTTP_200_OK)
        elif current_user.groups.filter(name__in=['Delivery Crew']).exists():
            # Implement changing status to True = delivered
            user_order.status = 1
            user_order.save()
            return Response({"message": f"{delivery_crew} has marked the order as delivered"}, status.HTTP_200_OK)
        else:
            return Response({"message": "PUT/PATCH Permission Denied"}, status.HTTP_403_FORBIDDEN)
    elif request.method == 'DELETE':
        # Check for Manager/Admin
        if current_user.groups.filter(name__in=['Manager']).exists() or request.user.is_superuser:
            # Implement Delete when Manager/admin validated
            customer_name = request.data.get('username')
            order = Order.objects.filter(user=customer_name)
            if order:
                order_items = OrderItem.objects.filter(user=user)
                order.delete()
                order_items.delete()
                return Response({"message": f"The order for {customer_name} has been completed"}, status.HTTP_200_OK)
            else:
                return Response({"message": f"There is no order for {customer_name}"}, status.HTTP_404_NOT_FOUND)
        else:
            return Response({"message": "DELETE Permission Denied"}, status.HTTP_403_FORBIDDEN)
    else:
        return Response({"message": "Error with request method, try again"}, status.HTTP_400_BAD_REQUEST)
