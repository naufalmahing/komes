from django.contrib import admin
from .models import (
    Order,
    Product,
    Store,
    Tag,
    OrderProduct,
    LatestAddress,
    Address,
)

admin.site.register(Order)
admin.site.register(Product)
admin.site.register(Store)
admin.site.register(Tag)
admin.site.register(OrderProduct)
admin.site.register(LatestAddress)
admin.site.register(Address)