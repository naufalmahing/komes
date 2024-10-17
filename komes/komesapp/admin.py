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

class AddressInline(admin.TabularInline):
    model = Address

class StoreAdmin(admin.ModelAdmin):
    # inlines = [
    #     AddressInline
    # ]
    list_display=['name', 'address']

admin.site.register(Order)
admin.site.register(Product)
admin.site.register(Store, StoreAdmin)
admin.site.register(Tag)
admin.site.register(OrderProduct)
admin.site.register(LatestAddress)
admin.site.register(Address)