from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/', include('users.urls')), # Including users app URLs
    path('api/', include('shop.urls')),  # Including shop app URLs
]
