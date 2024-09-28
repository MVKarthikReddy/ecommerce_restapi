from django.contrib.auth.models import User
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered')
    )
    
    user = models.ForeignKey(User, related_name='orders', on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(choices=STATUS_CHOICES, max_length=10, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} - {self.status}"
