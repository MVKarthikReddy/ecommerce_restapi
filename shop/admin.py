from django.contrib import admin
from .models import Product, Category, Order

admin.site.register(Order)

# Customizing Category Admin
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

# Customizing Product Admin
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'category')
    list_filter = ('category',)
    search_fields = ('name',)
    actions = ['reset_stock']

    # Custom action to reset stock
    def reset_stock(self, request, queryset):
        queryset.update(stock=100)  # Example: reset stock to 100 for selected products
        self.message_user(request, "Stock reset successfully")
    reset_stock.short_description = "Reset stock to 100"