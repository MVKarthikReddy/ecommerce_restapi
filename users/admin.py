from django.contrib import admin

from .models import CustomUser

# Registering the models
admin.site.register(CustomUser)