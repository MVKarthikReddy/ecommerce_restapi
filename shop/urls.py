from django.urls import path, include
from rest_framework.routers import DefaultRouter
# from .views import ProductViewSet, CartViewSet, OrderViewSet, CategoryViewSet, lobby
from . import views


# Create a router to handle viewsets
# router = DefaultRouter()
# router.register(r'products', ProductViewSet)
# router.register(r'cart', CartViewSet, basename='cart')
# router.register(r'orders', OrderViewSet, basename='orders')
# router.register(r'categories', CategoryViewSet, basename='orders')





urlpatterns = [
    # path('', include(router.urls)),  # Include all viewsets in the router
    path('', views.lobby),
    # path('cart/add_to_cart/', CartViewSet.as_view({'post': 'add_to_cart'}), name='add_to_cart'),

]
