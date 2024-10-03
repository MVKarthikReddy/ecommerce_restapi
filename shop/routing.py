# shops/routing.py

from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/orders/<int:user_id>/', consumers.OrderStatusConsumer.as_asgi()),  # WebSocket URL for orders
]

# shop/routing.py

# from django.urls import path
# from .consumers import OrderStatusConsumer

# websocket_urlpatterns = [
#     path('ws/order-status/', OrderStatusConsumer.as_asgi()),
# ]
