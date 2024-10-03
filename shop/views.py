from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Order, Product, Cart, CartItem, OrderItem
from .serializers import OrderSerializer, CartSerializer, ProductSerializer
from rest_framework.response import Response
from django.db.models import Sum, F
from django.core.cache import cache
from django.db import transaction
from rest_framework import status
from rest_framework.decorators import action

from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import viewsets
from .models import Category
from .serializers import CategorySerializer
from django.core.cache import cache

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from django.shortcuts import render

def lobby(request):
    return render(request,'shop/lobby.html')


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        """
        Apply custom permissions based on the action.
        Only allow admin users to create, update, or delete categories.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Restrict these actions to admin users only
            permission_classes = [IsAdminUser]
        else:
            # Allow authenticated users to view categories
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]

    def list(self, request, *args, **kwargs):
        # Cache the category list
        cache_key = 'categories_list'
        categories = cache.get(cache_key)

        if not categories:
            categories = Category.objects.all()
            cache.set(cache_key, categories, timeout=3600)  # Cache for 1 hour

        serializer = self.get_serializer(categories, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        # Retrieve a single category
        category = self.get_object()
        serializer = self.get_serializer(category)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        # Admin-only category creation
        response = super().create(request, *args, **kwargs)
        cache.delete('categories_list')  # Invalidate cache after adding a new category
        return response

    def update(self, request, *args, **kwargs):
        # Admin-only category update
        response = super().update(request, *args, **kwargs)
        cache.delete('categories_list')  # Invalidate cache after updating a category
        return response

    def destroy(self, request, *args, **kwargs):
        # Admin-only category deletion
        response = super().destroy(request, *args, **kwargs)
        cache.delete('categories_list')  # Invalidate cache after deleting a category
        return response


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    # permission_classes = [IsAuthenticated]  # to restrict access to authenticated users
    def get_permissions(self):
        """
        Apply custom permissions based on the action.
        Only allow admin users to create, update, or delete.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Restrict create, update, and delete to admin users
            permission_classes = [IsAdminUser]
        else:
            # Allow authenticated users to view products
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]

    def list(self, request, *args, **kwargs):
        # Define the cache key for products list
        cache_key = 'products_list'
        
        # Check if cached data exists
        products = cache.get(cache_key)
        
        if not products:
            # Fetch products from the database if not cached
            products = Product.objects.select_related('category').all()
            
            # Store the result in Redis cache
            cache.set(cache_key, products, timeout=3600)  # Cache for 1 hour
        
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        # Retrieve a single product and avoid caching for this method
        product = self.get_object()
        serializer = self.get_serializer(product)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        # Invalidate cache after creating a new product
        cache.delete('products_list')
        return response

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        # Invalidate cache after updating a product
        cache.delete('products_list')
        return response

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        # Invalidate cache after deleting a product
        cache.delete('products_list')
        return response

class CartViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated] # This line will Ensure the user is authenticated
    serializer_class = CartSerializer

    def get_queryset(self):
        # Retrieve the cart for the authenticated user
        return Cart.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        # Fetch all cart items for the current user's cart
        cart = self.get_queryset().first()

        if cart:
            serializer = self.get_serializer(cart)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'No cart found for the user'}, status=status.HTTP_404_NOT_FOUND)

    def retrieve(self, request, *args, **kwargs):
        # Fetch the cart items of the specific user's cart
        cart = self.get_object()
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        # Custom create method to initialize a cart for the user if it doesn't exist
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='add_to_cart')  # Using @action decorator
    def add_to_cart(self, request, *args, **kwargs):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        try:
            product = Product.objects.get(pk=product_id)
            if product.stock < int(quantity):
                return Response({'error': 'Insufficient stock available.'}, status=status.HTTP_400_BAD_REQUEST)
            CartItem.objects.create(cart=cart, product=product, quantity=quantity)
            return Response({'status': 'Added to cart'}, status=status.HTTP_201_CREATED)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response({'error': 'Invalid quantity value.'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['delete'], url_path='remove_item')
    def remove_cart_item(self, request, pk=None):
        cart = self.get_object()
        cart_item_id = request.data.get('cart_item_id')

        try:
            cart_item = CartItem.objects.get(pk=cart_item_id, cart=cart)
        except CartItem.DoesNotExist:
            return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)

        # Remove the item from the cart
        cart_item.delete()

        return Response({'status': 'Cart item removed successfully'}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'], url_path='place_order')  # Using @action decorator
    def place_order(self, request, *args, **kwargs):
        cart = self.get_object()

        # It will Calculate the total price by summing (product price * quantity) for each CartItem
        total_price = cart.cartitem_set.aggregate(
            total=Sum(F('product__price') * F('quantity'))
        )['total'] or 0

        # Making sure that the cart is not empty
        if total_price <= 0:
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            # This line will create the order
            order = Order.objects.create(user=request.user, total_price=total_price)

            for item in cart.cartitem_set.all():
                # Ensure sufficient stock before proceeding
                if item.product.stock < item.quantity:
                    return Response({'error': f'Insufficient stock for {item.product.name}.'}, status=status.HTTP_400_BAD_REQUEST)

                # This will create the order item
                OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)

                # To update product stock in Product table
                item.product.stock -= item.quantity
                item.product.save()

            # Empty the cart after placing the order
            cart.cartitem_set.all().delete()

        return Response({'status': 'Order placed', 'order_id': order.id}, status=status.HTTP_201_CREATED)

class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated] # This line will Ensure the user is authenticated
    serializer_class = OrderSerializer 

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def update_order_status(self, request, pk, *args, **kwargs):
        order = self.get_object()
        status_value = request.data.get('status', 'PENDING')
        order.status = status_value
        order.save()

        # Notify user about status update
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{order.user.id}",
            {
                'type': 'order_status_update',
                'message': f"Order #{order.id} status updated to {status_value}."
            }
        )

        return Response({'status': 'Order status updated'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel_order(self, request, pk=None):
        order = self.get_object()

        if order.status == 'CANCELED':
            return Response({'error': 'Order is already canceled.'}, status=status.HTTP_400_BAD_REQUEST)

        if order.status == 'COMPLETED':
            return Response({'error': 'Completed orders cannot be canceled.'}, status=status.HTTP_400_BAD_REQUEST)

        # Restore product stock when the order is canceled
        for item in order.orderitem_set.all():
            product = item.product
            product.stock += item.quantity
            product.save()

        # Update the order status to 'CANCELED'
        order.status = 'CANCELED'
        order.save()

        return Response({'status': 'Order canceled successfully'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['delete'], url_path='delete')
    def delete_order(self, request, pk=None):
        order = self.get_object()

        if order.status == 'COMPLETED':
            return Response({'error': 'Completed orders cannot be deleted.'}, status=status.HTTP_400_BAD_REQUEST)

        # Optionally restore stock before deleting
        if order.status != 'CANCELED':
            for item in order.orderitem_set.all():
                product = item.product
                product.stock += item.quantity
                product.save()

        # Delete the order and its items
        order.delete()

        return Response({'status': 'Order deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
