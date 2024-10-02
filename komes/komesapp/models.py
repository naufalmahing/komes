from django.db import models
from django.contrib.auth.models import User

from djmoney.models.fields import MoneyField

class Store(models.Model):
    name=models.CharField(max_length=150)
    description=models.TextField(null=True)
    owner=models.OneToOneField(
        User,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return str(self.id) + '-' + self.name

class Product(models.Model):
    name=models.CharField(max_length=150)
    description=models.TextField()
    photo=models.ImageField()
    store=models.ForeignKey(Store, on_delete=models.CASCADE)
    price=MoneyField(max_digits=19, decimal_places=4, default_currency='IDR', default=0)
    # counter
    # available
    
    def __str__(self):
        return str(self.id) + '-' + self.name

class Tag(models.Model):
    name=models.CharField(max_length=100)
    products=models.ManyToManyField(Product, blank=True)

    def __str__(self):
        return str(self.id) + '-' + self.name
    
class Order(models.Model):
    products=models.ManyToManyField(Product, through='OrderProduct')
    user=models.ForeignKey(User, on_delete=models.CASCADE,null=False)
    active=models.BooleanField(default=True)

    def __str__(self):
        return str(self.id)
    
    def get_total_payment(self):
        total = sum([product.price for product in self.products.all()])
        return total

class OrderProduct(models.Model):
    product=models.ForeignKey(Product, on_delete=models.CASCADE)
    order=models.ForeignKey(Order, on_delete=models.CASCADE)
    