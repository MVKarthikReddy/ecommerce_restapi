from django.contrib import admin
from .models import Product, Category, Order, Cart, CartItem, OrderItem

# Register Order model
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'status', 'created_at', 'updated_at')
    search_fields = ('user__username', 'status')
    list_filter = ('status', 'created_at')
    ordering = ('-created_at',)

# Register Cart model
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user')
    search_fields = ('user__username',)

# Register CartItem model
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'product', 'quantity')
    search_fields = ('product__name', 'cart__user__username')

# Register OrderItem model
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity')
    search_fields = ('product__name', 'order__user__username')
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