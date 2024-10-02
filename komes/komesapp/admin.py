from django.contrib import admin
from .models import (
    Order,
    Product,
    Store,
    Tag,
    OrderProduct
)

admin.site.register(Order)
admin.site.register(Product)
admin.site.register(Store)
admin.site.register(Tag)
admin.site.register(OrderProduct)