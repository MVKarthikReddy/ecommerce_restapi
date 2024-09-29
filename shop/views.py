from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Order, Product, Cart, CartItem, OrderItem
from .serializers import OrderSerializer, CartSerializer, ProductSerializer
from rest_framework.response import Response
from django.db.models import Sum, F
from django.db import transaction
from rest_framework import status
from rest_framework.decorators import action


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]  # Assuming you want to restrict access to authenticated users

class CartViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
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

    @action(detail=True, methods=['post'], url_path='place_order')  # Using @action decorator
    def place_order(self, request, *args, **kwargs):
        cart = self.get_object()
        print('hellp')
        # Calculate total price by summing (product price * quantity) for each CartItem
        total_price = cart.cartitem_set.aggregate(
            total=Sum(F('product__price') * F('quantity'))
        )['total'] or 0

        if total_price <= 0:
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            # Create the order
            order = Order.objects.create(user=request.user, total_price=total_price)

            for item in cart.cartitem_set.all():
                # Ensure sufficient stock before proceeding
                if item.product.stock < item.quantity:
                    return Response({'error': f'Insufficient stock for {item.product.name}.'}, status=status.HTTP_400_BAD_REQUEST)

                # Create the order item
                OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)

                # Update product stock
                item.product.stock -= item.quantity
                item.product.save()

            # Empty the cart after placing the order
            cart.cartitem_set.all().delete()

        return Response({'status': 'Order placed', 'order_id': order.id}, status=status.HTTP_201_CREATED)

class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def update_order_status(self, request, pk, *args, **kwargs):
        order = self.get_object()
        status_value = request.data.get('status', 'PENDING')
        order.status = status_value
        order.save()
        
        # Notify user about status update (implementation depends on your WebSocket setup)
        # Example: notify_user(order.user, order)

        return Response({'status': 'Order status updated'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel_order(self, request, pk=None):
        order = self.get_object()

        if order.status == 'CANCELLED':
            return Response({'error': 'Order is already cancelled'}, status=status.HTTP_400_BAD_REQUEST)

        if order.status != 'PENDING':
            return Response({'error': 'Only pending orders can be cancelled'}, status=status.HTTP_400_BAD_REQUEST)

        # Update the order status to CANCELLED
        order.status = 'CANCELLED'
        order.save()

        # Restore stock for each product in the order
        for item in order.items.all():
            item.product.stock += item.quantity
            item.product.save()

        return Response({'status': 'Order cancelled, stock restored'}, status=status.HTTP_200_OK)
