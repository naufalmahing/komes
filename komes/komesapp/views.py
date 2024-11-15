from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.views import View

from django.views.generic.edit import DeleteView

from django.shortcuts import render

from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse, reverse_lazy

from django.contrib import messages

from django.contrib.auth.models import User
from .models import (
    Store,
    Product,
    Tag,
    Order,
    OrderProduct,
    Address,
    LatestAddress,
)

from django.template import loader

from .forms import StoreForm, CreateStoreForm, ProductForm, ProductImageForm, ShipmentForm, AddressForm
from django.forms.models import model_to_dict

import datetime
import midtransclient

import requests
import json

from django.conf import settings
SERVER_KEY = settings.MIDTRANS_SERVER_KEY
CLIENT_KEY = settings.MIDTRANS_CLIENT_KEY
BITESHIP_TOKEN = settings.BITESHIP_TOKEN

class MyView(LoginRequiredMixin, View):
    login_url = '/accounts/login'
    redirect_field_name = "redirect_to"

    def get(self, request):
        
        products = Product.objects.all()
        
        return render(request, 'komesapp/index.html', {
            'products': products
        })

class StoresView(LoginRequiredMixin, View):
    login_url = '/accounts/login'
    redirect_field_name = "redirect_to"

    def get(self, request):
        
        stores = Store.objects.all()
        
        return render(request, 'komesapp/stores.html', {
            'stores': stores
        })
    

class OrderView(LoginRequiredMixin, View):
    login_url = '/accounts/login'
    redirect_field_name = "redirect_to"

    def get(self, request):
        order = Order.objects.filter(user__id=request.user.id).last()
        orderproducts = OrderProduct.objects.filter(order__id=order.id)
        
        return render(request, 'komesapp/order.html', {
            'orderproducts': orderproducts,
            'order': orderproducts.first().order
        })
    
    def post(self, request, *args, **kwargs):
        product = Product.objects.get(id=kwargs['product_id'])

        order = Order.objects.filter(user__id=request.user.id, active=True).last()
        if not order:
            order = Order(user=User.objects.get(id=request.user.id))
            order.save()
        
        # check if there's an object with the same order and product from orderproduct 
        orderproduct = OrderProduct.objects.filter(product__id=product.id, order__id=order.id).first()
        if not orderproduct:
            orderproduct = OrderProduct(product=product, order=order, count=0)    
        
        orderproduct.count += 1
        orderproduct.save()

        messages.success(request, 'Product added to order')
        if 'redirect_to' in request.POST:
            redirect_to = request.POST['redirect_to']
            return HttpResponseRedirect(redirect_to)

        return HttpResponseRedirect(reverse(
            'storedetail', 
            kwargs={
                'store_id': product.store.id
            })
        )
    
class DeleteProductFromOrderView(LoginRequiredMixin, View):
    login_url = '/accounts/login'
    redirect_field_name = "redirect_to"

    def post(self, request, *args, **kwargs):
        order = Order.objects.filter(user__id=request.user.id, active=True).last()
        product = Product.objects.get(id=kwargs['product_id'])
        order.orderproduct_set.filter(order__id=order.id, product__id=product.id).last().delete()
       
        messages.success(request, 'Product deleted from order')
        return HttpResponseRedirect(
           reverse('order')
       )

"""clear order of products that populates it"""
class ClearOrderView(LoginRequiredMixin, View):
    login_url = '/accounts/login'
    redirect_field_name = "redirect_to"

    def get(self, request):
        return render(request, 'komesapp/clear_order_confirmation.html')
    
    def post(self, request):
        order = Order.objects.filter(user__id=request.user.id, active=True).last()
        print(order.orderproduct_set)
        order.orderproduct_set.all().delete()
        return HttpResponseRedirect(reverse('order'))
    
# class DeleteProductView(LoginRequiredMixin, View):
#     login_url = '/accounts/login'
#     redirect_field_name = "redirect_to"

#     def post(self, request, *args, **kwargs): 
#         Product.objects.get(id=kwargs['product_id']).delete()
#         return HttpResponseRedirect(
#             reverse(
#                 'storedetail',
#                 kwargs={
#                     'store_id': kwargs['store_id']
#                 }
#             )
#         )
    
class SettingsView(LoginRequiredMixin, View):
    login_url = '/accounts/login'
    redirect_field_name = "redirect_to"

    def get(self, request):
        
        has_store = True if Store.objects.filter(owner__id=request.user.id) else False
        
        user = User.objects.get(id=request.user.id)
        return render(request, 'komesapp/settings.html', {
            'has_store': has_store,
            'address': user.latestaddress.address if hasattr(user, 'latestaddress') else None
        })
    
class CreateStoreView(LoginRequiredMixin, View):
    login_url = '/accounts/login'
    redirect_field_name = "redirect_to"
    
    def get(self, request):
        form = CreateStoreForm() 
        return render(request, 'komesapp/createstore.html', {
            'form': form
        })
    
    def post(self, request):
        form = CreateStoreForm(request.POST)
        if form.is_valid():
            
            name = form.cleaned_data.get('address_name')
            city = form.cleaned_data.get('city')
            subdistrict = form.cleaned_data.get('subdistrict')
            ward = form.cleaned_data.get('ward')
            address = form.cleaned_data.get('address')
            zipcode = form.cleaned_data.get('zipcode')
            user = User.objects.get(id=request.user.id)
            
            address = Address(name=name, city=city, subdistrict=subdistrict, ward=ward, address=address, zipcode=zipcode, user=user)
            address.save()
            
            store = Store(
                name=form.cleaned_data.get('store_name'), description=form.cleaned_data.get('description'),
                owner=request.user,
                address=address
            )
            store.save()

        return HttpResponseRedirect(reverse('storedetail', kwargs={
            'store_id': store.id
        }))
    
class StoreDetailView(LoginRequiredMixin, View):
    login_url = '/accounts/login'
    redirect_field_name = "redirect_to"

    """get detail view from a store where its user's or not"""
    def get(self, request, *args, **kwargs):
        user = User.objects.get(id=request.user.id)
        store = user.store
        
        if not store:
            store = Store.objects.get(id=kwargs['store_id'])
            if store:
                return HttpResponse('Access not permitted')
            else:
                return HttpResponse('Store not found')

        # store = Store.objects.filter(owner__id=request).first()
        return render(request, 'komesapp/storedetail.html', {
            'store': store
        })
    
class UpdateStoreView(LoginRequiredMixin, View):
    login_url = '/accounts/login'
    redirect_field_name = "redirect_to"

    def get(self, request, *args, **kwargs):
        # get user permission
        user = User.objects.get(id=request.user.id)
        store = user.store if user.store else None
        store = Store.objects.get(id=kwargs['store_id'])

        if not store:
            store = Store.objects.get(id=kwargs['store_id'])
            if store:
                return HttpResponse('Access not permitted')
            else:
                return HttpResponse('Store not found')
            
        # TODO: idk if i should use this
        # if store:
        #     if not user.has_perm('komesapp.change_store'):
        #         return 'no permission'


        form = StoreForm({
            'name': store.name,
            'description': store.description
        })
        return render(request, 'komesapp/updatestore.html', {
            'form': form,
            'store': store
        }) 

    def post(self, request, *args, **kwargs):
        print(request.POST)
        form = StoreForm(request.POST)
        user = User.objects.get(id=request.user.id)
        store = user.store 

        if not store:
            store = Store.objects.get(id=kwargs['store_id'])
            if store:
                return HttpResponse('Access not permitted')
            else:
                return HttpResponse('Store not found')
            
        if form.is_valid():
            store.name = form.cleaned_data.get('name')
            store.description = form.cleaned_data.get('description')
            store.save()
            return HttpResponseRedirect(reverse('storedetail', kwargs={
                'store_id':store.id
            }))
        
class UpdateStoreAddressView(LoginRequiredMixin, View):
    login_url = '/accounts/login'
    redirect_field_name = "redirect_to"

    def get(self, request, *args, **kwargs):
        user = User.objects.get(id=request.user.id)
        store = user.store 
        
        if not store:
            store = Store.objects.get(id=kwargs['store_id'])
            if store:
                return HttpResponse('Access not permitted')
            else:
                return HttpResponse('Store not found')
            
        form = AddressForm(model_to_dict(store.address))
        return render(request, 'komesapp/update_store_address.html', {
            'address_form': form,
            'store': store,
        })
    
    def post(self, request, *args, **kwargs):
        form = AddressForm(request.POST)
        
        user = User.objects.get(id=request.user.id)
        store = user.store 
        
        if not store:
            store = Store.objects.get(id=kwargs['store_id'])
            if store:
                return HttpResponse('Access not permitted')
            else:
                return HttpResponse('Store not found')
            
        if form.is_valid():
            store.address.name = form.cleaned_data.get('name')
            store.address.city = form.cleaned_data.get('city')
            store.address.subdistrict = form.cleaned_data.get('subdistrict')
            store.address.ward = form.cleaned_data.get('ward')
            store.address.address = form.cleaned_data.get('address')
            store.address.zipcode = form.cleaned_data.get('zipcode')
            store.address.save()

            return HttpResponseRedirect(reverse('updatestore', kwargs={
                'store_id': kwargs['store_id']
            }))
        
        # messages.error(request, form.errors)
        return HttpResponseRedirect(reverse('storeupdateaddress', kwargs={
                'store_id': kwargs['store_id']
            }))
class AddProductView(LoginRequiredMixin, View):
    login_url = '/accounts/login'
    redirect_field_name = "redirect_to"

    def get(self, request):
        form = ProductForm()
        return render(request, 'komesapp/add_store_product.html', {
            'form': form,
        })
    
    def post(self, request):
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data.get('name')
            description = form.cleaned_data.get('description')
            photo = form.cleaned_data.get('photo')
            store = Store.objects.filter(owner__id=request.user.id).last()
            
            Product(store=store, name=name, description=description, photo=photo).save()
            return HttpResponseRedirect(reverse('updatestore', kwargs={
                'store_id': store.id
            }))
        
        print(form.errors)
        return render(request, 'komesapp/add_store_product.html', {
            'msg': form.errors,
            'form': form
        })
        

class DeleteProductView(LoginRequiredMixin, View):
    login_url = '/accounts/login'
    redirect_field_name = "redirect_to"

    def get(self, request, *args, **kwargs):
        return render(request, 'komesapp/delete_store_product_confirmation.html', {
            'product_id': kwargs['product_id']
        })

    def post(self, request, *args, **kwargs):
        Product.objects.get(id=kwargs['product_id']).delete()
        return HttpResponseRedirect(reverse('updatestore', kwargs={
                'store_id': Store.objects.filter(owner__id=request.user.id).last().id
            }))

"""test view"""
def upload_preview_image(request):
    return render(request, 'komesapp/uploadpreview.html', {'photo': Product.objects.last().photo})

class UpdateProductView(LoginRequiredMixin, View):
    login_url = '/accounts/login'
    redirect_field_name = "redirect_to"
    
    def get(self, request, *args, **kwargs):
        product = Product.objects.get(id=kwargs['product_id'])
        form = ProductForm(
            data={
                'name': product.name,
                'description': product.description,
                'photo': product.photo.url,
                'price_0': product.price.amount, 
                'price_1': 'IDR'
            }
        )

        return render(request, 'komesapp/update_store_product.html', {
            'form': form,
            'photo': product.photo,
            'product_id': product.id
        })
    
    def post(self, request, *args, **kwargs):
        form = ProductForm(request.POST, request.FILES)
        print(request.POST)
        print(request.FILES)
        if form.is_valid():
            product = Product.objects.get(id=kwargs['product_id'])
            product.name = form.cleaned_data.get('name')
            product.description = form.cleaned_data.get('description')
            product.price = form.cleaned_data.get('price')
            product.save()
            return HttpResponseRedirect(reverse('updatestore', kwargs={
                'store_id': Store.objects.filter(owner__id=request.user.id).last().id
            }))
        
class UpdateProductImageView(LoginRequiredMixin, View):
    login_url = '/accounts/login'
    redirect_field_name = "redirect_to"

    def get(self, request, *args, **kwargs):
        form = ProductImageForm()
        product = Product.objects.get(id=kwargs['product_id'])
        return render(request, 'komesapp/update_store_product_image.html', {
            'form': form,
            'product_id': kwargs['product_id'],
            'photo_url': product.photo.url
        })

    def post(self, request, *args, **kwargs):
        product = Product.objects.get(id=kwargs['product_id'])
        form = ProductImageForm(request.POST, request.FILES)
        if form.is_valid():
            product.photo = form.cleaned_data.get('photo')
            product.save()
            return HttpResponseRedirect(reverse('updatestoreproduct', kwargs={
                'product_id': kwargs['product_id']
            }))
        return 'update image form is not valid'

class DeleteStoreView(LoginRequiredMixin, DeleteView):
    login_url = '/accounts/login'
    redirect_field_name = "redirect_to"

    model = Store
    success_url = reverse_lazy('index')
    template_name = 'komesapp/delete_store_confirmation.html'

class BuyView(LoginRequiredMixin, View):
    login_url = '/accounts/login'
    redirect_field_name = "redirect_to"

    def get(self, request, *args, **kwargs):
        """
        use django-money, create a sum function to total the payment needed
        
        first learn how to use bni api or gopay api and other api for payment. learn service api that can be used for shipment like jne"""

        # get total of payment
        order = Order.objects.get(id=kwargs['order_id'])
        
        # form
        # form = BuyForm()

        
        print(order.get_total_payment().amount)
        print(order.courier_fee)
        print(order.courier_fee.amount)


        """payment with midtransclient"""
        
        snap = midtransclient.Snap(
            is_production=False,
            server_key=SERVER_KEY,
            client_key=CLIENT_KEY
        )
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        transaction_token = snap.create_transaction_token({
            "transaction_details": {
                "order_id": "order-id-python-"+timestamp,
                "gross_amount": int(order.get_total_payment().amount)
            }, "credit_card":{
                "secure" : True
            }
        })

        

        return render(request, 'komesapp/buy.html', {
            'total_payment': order.get_total_payment(),
            'order': order,
            'snap_token': transaction_token,
            'client_key': CLIENT_KEY
        })

    def post(self, request, *args, **kwargs):
        order = Order.objects.get(id=kwargs['order_id'])
        order.courier_fee = request.POST['courier-fee']
        order.save()

        # create a biteship order object
        url = "https://api.biteship.com/v1/orders"

        user = User.objects.get(id=request.user.id)
        # get store owner, order -> product -> store -> owner
        store_owner = order.products.first().store.owner

        # list all items
        items = [
            {
                'name': product.name,
                'value': int(product.price.amount), 
                'quantity': 1,
                'weight': 100 # just dummy
            } 
        for product in order.products.all()]
        
        print(store_owner.first_name)
        print(store_owner.store.address)
        print(store_owner.store.address.zipcode)
        print(user.first_name)
        print(user.latestaddress.address)
        print(user.latestaddress.address.zipcode)
        print(request.POST['courier-name'])
        print(request.POST['courier-fee'])
        print(request.POST['courier-type'])
        print(request.POST['delivery-type'])

        print(items)
        # payload = json.dumps({
        # "origin_contact_name": store_owner.first_name + ' ' + store_owner.last_name,
        # "origin_contact_phone": "088888888888",
        # "origin_address": store_owner.store.address.address,
        # "origin_note": "",
        # "origin_postal_code": store_owner.store.address.zipcode,
        # "destination_contact_name": user.first_name + ' ' + user.last_name,
        # "destination_contact_phone": "088888888888",
        # "destination_address": user.latestaddress.address.address,
        # "destination_postal_code": user.latestaddress.address.zipcode,
        # "destination_note": "",
        # "courier_company": request.POST['courier-name'],
        # "courier_type": request.POST['courier-type'],
        # "delivery_type": request.POST['delivery-type'],
        # "order_note": "Please be careful",
        # "metadata": {},
        # "items": items
        # })

        # payload = json.dumps({
        # "shipper_contact_name": "Amir",
        # "shipper_contact_phone": "088888888888",
        # "shipper_contact_email": "biteship@test.com",
        # "shipper_organization": "Biteship Org Test",
        # "origin_contact_name": "Amir",
        # "origin_contact_phone": "088888888888",
        # "origin_address": "Plaza Senayan, Jalan Asia Afrik...",
        # "origin_note": "Deket pintu masuk STC",
        # "origin_postal_code": 12440,
        # "destination_contact_name": "John Doe",
        # "destination_contact_phone": "088888888888",
        # "destination_contact_email": "jon@test.com",
        # "destination_address": "Lebak Bulus MRT...",
        # "destination_postal_code": 12950,
        # "destination_note": "Near the gas station",
        # "courier_company": "jne",
        # "courier_type": "reg",
        # "courier_insurance": 500000,
        # "delivery_type": "now",
        # "order_note": "Please be careful",
        # "metadata": {},
        # "items": [
        #     {
        #     "name": "Black L",
        #     "description": "White Shirt",
        #     "category": "fashion",
        #     "value": 165000,
        #     "quantity": 1,
        #     "height": 10,
        #     "length": 10,
        #     "weight": 200,
        #     "width": 10
        #     }
        # ]
        # })

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer biteship_test.eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoidGVzIGFwaSIsInVzZXJJZCI6IjY2ZjhkNzMwZDZjNjQ3MDAxMjA1MGQxMSIsImlhdCI6MTcyNzU4NDIzMH0.eQlCI2RFeMiUoHzwO5_DZ7aajUuxDbIIk_tdkDrg8mA'
        }

        # response = requests.request("POST", url, headers=headers, data=payload)

        # print(response.text)

        return HttpResponseRedirect(reverse('buy', kwargs={
            'order_id': kwargs['order_id']
        }))


class LatestAddressView(LoginRequiredMixin, View):
    login_url = '/accounts/login'
    redirect_field_name = "redirect_to"

    def post(self, request, *args, **kwargs):
        address_id = kwargs['address_id']

        user = User.objects.get(id=request.user.id)
        latest_address  = user.latestaddress
        latest_address.address = user.address_set.get(id=address_id)
        latest_address.save()

        # get latest order from user
        order = user.order_set.last()
        print(order)

        redirect_to = request.POST['redirect_to']
        # if 'order' in redirect_to:
            # return HttpResponse('checkout')
        return HttpResponseRedirect(redirect_to)

        # return render(request, 'komesapp/order.html')

"""modal page to choose address when checkout"""
class ChangeAddressModalView(LoginRequiredMixin, View):
    login_url = '/accounts/login'
    redirect_field_name = "redirect_to"

    def get(self, request):
        # get user
        user = User.objects.get(id=request.user.id)

        print(user.order_set.last())
        print(type(user.order_set.last()))
        print(user.order_set.last().products)
        # print(user.order_set.all())
        return HttpResponse(loader.render_to_string('komesapp/address_change_modal.html', context={
            'addresses': user.address_set.all(),
            'address': user.latestaddress.address,
            'order': user.order_set.last()
        }, request=request))
    
        """v.1
        fix with render???"""
    

    def post(self, request):
        user = User.objects.get(id=request.user.id)

        new_latestaddress = user.address_set.get(request.JSON['address_id'])
        if new_latestaddress:
            user.latestaddress.address = new_latestaddress
            user.save()

            return HttpResponseRedirect(reverse('')) # this the one that needs dynamic return url
        return HttpResponse('Address isn\'t in your address list')
        
class OrderChangeAddressModalView(LoginRequiredMixin, View):
    login_url = '/accounts/login'
    redirect_field_name = "redirect_to"

    def get(self, request):
        # get user
        user = User.objects.get(id=request.user.id)
        # user.user_permissions.add(permissio)
        addresses = user.address_set.all()
        
        # print(user.order_set.last())
        # print(type(user.order_set.last()))
        # print(user.order_set.last().products)
        # print(user.order_set.all())
        return HttpResponse(loader.render_to_string('komesapp/address_change_modal_from_order.html', context={
            # 'addresses': user.address_set.all(),
            'addresses': addresses,
            'address': user.latestaddress.address,
            'order': user.order_set.last(),
            'store': user.store
        }, request=request))
    
        """v.1
        fix with render???"""
    

    def post(self, request):
        # user = User.objects.get(id=request.user.id)
        # user.latestaddress_set.address = Address.objects.get(request.JSON['address_id'])
        # user.save()

        # return HttpResponseRedirect(reverse('checkout', kwargs={
        #     'order_id': user.order_set.last().id
        # })) # this the one that needs dynamic return url

        user = User.objects.get(id=request.user.id)
        
        # check if address is in the user addresses

        new_latestaddress = user.address_set.filter(id=request.JSON['address_id']).first()
        if new_latestaddress:
            user.latestaddress_set.address = new_latestaddress
            user.save()

            return render(request, 'komesapp/order.html', {
                'address': user.latestaddress.address,
                'order': user.order_set.last()
            })
        return HttpResponse('Address isn\'t in your address list')
    
    
class SettingsChangeAddressModalView(LoginRequiredMixin, View):
    login_url = '/accounts/login'
    redirect_field_name = "redirect_to"

    def get(self, request):
        # get user
        user = User.objects.get(id=request.user.id)

        # print(user.order_set.last())
        # print(type(user.order_set.last()))
        # print(user.order_set.last().products)
        # print(user.order_set.all())
        return HttpResponse(loader.render_to_string('komesapp/address_change_modal_from_settings.html', context={
            'addresses': user.address_set.all(),
            'address': user.latestaddress.address,
            'order': user.order_set.last()
        }, request=request))
    
        """v.1
        fix with render???"""
    

    def post(self, request):

        # user = User.objects.get(id=request.user.id)
        # user.latestaddress_set.address = Address.objects.get(request.JSON['address_id'])
        # user.save()

        # return HttpResponseRedirect(reverse('checkout', kwargs={
        #     'order_id': user.order_set.last().id
        # })) # this the one that needs dynamic return url

        user = User.objects.get(id=request.user.id)
        
        # check if address is in the user addresses

        new_latestaddress = user.address_set.filter(id=request.JSON['address_id']).first()
        if new_latestaddress:
            user.latestaddress_set.address = new_latestaddress
            user.save()

            return HttpResponseRedirect(reverse('settings')) # this the one that needs dynamic return url
        return HttpResponse('Address isn\'t in your address list')


"""test view for rendering template with loader render"""
def test_form(request):
    # eturn HttpResponse(loader.render_to_string('komesapp/'))
    pass

"""update address from modal"""


"""create address from modal"""

"""choose address from setting page"""
class ChangeAddressView(LoginRequiredMixin, View):
    login_url = '/accounts/login'
    redirect_field_name = "redirect_to"

    def get(self, request):
        # get user
        user = User.objects.get(id=request.user.id)
        print(user.latestaddress)
        return render(request, 'komesapp/address.html', {
            'addresses': user.address_set.all(),
            'latest_address': user.latestaddress.address
        })

    def post(self, request):
        """update latest address with checkbox"""
        pass
        # user = User.objects.get(id=request.user.id)
        # user.latestaddress_set.address = Address.objects.get(request.JSON['address_id'])
        # user.save()

        # return HttpResponseRedirect(reverse('')) # this the one that needs dynamic return url

"""api test"""
def api_test(request):
    data = request.JSON['foo']
    return data

"""create address modal page"""
class CreateAddressModalView(LoginRequiredMixin, View):
    login_url = '/accounts/login'
    redirect_field_name = "redirect_to"

    def get(self, request):
        form = AddressForm()
        
        # return render(request, 'komesapp/create_address.html', context={
        #     'address_form': form
        # })
    
        return HttpResponse(loader.render_to_string('komesapp/address_input_modal.html', context={
            'address_form': form,
        }, request=request))

    
    def post(self, request):
        # get form
        form = AddressForm(request.POST)

        if form.is_valid():
            name = form.cleaned_data.get('name')
            city = form.cleaned_data.get('city')
            subdistrict = form.cleaned_data.get('subdistrict')
            ward = form.cleaned_data.get('ward')
            address = form.cleaned_data.get('address')
            zipcode = form.cleaned_data.get('zipcode')
            user = User.objects.get(id=request.user.id)
            
            address = Address(name=name, city=city, subdistrict=subdistrict, ward=ward, address=address, zipcode=zipcode, user=user)
            address.save()
            
            user.latestaddress.address = address
            user.latestaddress.save()

            print(request.POST['redirect_to'])
            redirect_to = request.POST['redirect_to']
            # kwargs = {}
            # if 'checkout' in redirect_to:
            #     kwargs = {
            #         'order_id': user.order_set.last().id
            #     }
            #     return HttpResponseRedirect(reverse('checkout'), kwargs=kwargs)
            
            return HttpResponseRedirect(redirect_to)
        

class OrderCreateAddressModalView(LoginRequiredMixin, View):
    login_url = '/accounts/login'
    redirect_field_name = "redirect_to"

    def get(self, request):
        form = AddressForm()
        
        # return render(request, 'komesapp/create_address.html', context={
        #     'address_form': form
        # })
    
        user = User.objects.get(id=request.user.id)

        return HttpResponse(loader.render_to_string('komesapp/address_input_modal_from_order.html', context={
            'address_form': form,
            'order': user.order_set.last(),
            'address': user.latestaddress.address,
            'store': user.store
        }, request=request))

    
    def post(self, request):
        # get form
        form = AddressForm(request.POST)

        if form.is_valid():
            name = form.cleaned_data.get('name')
            city = form.cleaned_data.get('city')
            subdistrict = form.cleaned_data.get('subdistrict')
            ward = form.cleaned_data.get('ward')
            address = form.cleaned_data.get('address')
            zipcode = form.cleaned_data.get('zipcode')
            user = User.objects.get(id=request.user.id)
            
            address = Address(name=name, city=city, subdistrict=subdistrict, ward=ward, address=address, zipcode=zipcode, user=user)
            address.save()
            
            user.latestaddress.address = address
            user.latestaddress.save()

            print(request.POST['redirect_to'])
            redirect_to = request.POST['redirect_to']
            # kwargs = {}
            # if 'checkout' in redirect_to:
            #     kwargs = {
            #         'order_id': user.order_set.last().id
            #     }
            #     return HttpResponseRedirect(reverse('checkout'), kwargs=kwargs)
            
            return HttpResponseRedirect(reverse('orderaddress'))
        

class SettingsCreateAddressModalView(LoginRequiredMixin, View):
    login_url = '/accounts/login'
    redirect_field_name = "redirect_to"

    def get(self, request):
        form = AddressForm()
        
        # return render(request, 'komesapp/create_address.html', context={
        #     'address_form': form
        # })
        user = User.objects.get(id=request.user.id)
        return HttpResponse(loader.render_to_string('komesapp/address_input_modal_from_settings.html', context={
            'address_form': form,
            'address': user.latestaddress.address
        }, request=request))

    
    def post(self, request):
        # get form
        form = AddressForm(request.POST)

        if form.is_valid():
            name = form.cleaned_data.get('name')
            city = form.cleaned_data.get('city')
            subdistrict = form.cleaned_data.get('subdistrict')
            ward = form.cleaned_data.get('ward')
            address = form.cleaned_data.get('address')
            zipcode = form.cleaned_data.get('zipcode')
            user = User.objects.get(id=request.user.id)
            
            address = Address(name=name, city=city, subdistrict=subdistrict, ward=ward, address=address, zipcode=zipcode, user=user)
            address.save()
            
            user.latestaddress.address = address
            user.latestaddress.save()

            print(request.POST['redirect_to'])
            redirect_to = request.POST['redirect_to']
            # kwargs = {}
            # if 'checkout' in redirect_to:
            #     kwargs = {
            #         'order_id': user.order_set.last().id
            #     }
            #     return HttpResponseRedirect(reverse('checkout'), kwargs=kwargs)
            
            return HttpResponseRedirect(reverse('settingsaddress'))

class OrderDeleteAddressView(LoginRequiredMixin, View):
    login_url = '/accounts/login'
    redirect_field_name = "redirect_to"

    def get(self, request, *args, **kwargs):
        user = User.objects.get(id=request.user.id)
        return HttpResponse(loader.render_to_string('komesapp/delete_address_confirmation_from_order.html', context={
                'addresses': user.address_set.all(),
                'address': Address.objects.get(id=kwargs['address_id']),
                'order': user.order_set.last(),
                'store': user.order_set.last().products.first().store,
                'previous_url': request.META['HTTP_REFERER']
            }, request=request))

    def post(self, request, *args, **kwargs):
        user = User.objects.get(id=request.user.id)
        address = user.address_set.filter(id=kwargs['address_id']).first()

        if user.latestaddress.address.id == address.id:
            ids = [address.id for address in user.address_set.all()]
            ids.remove(user.latestaddress.address.id)
            user.latestaddress.address = user.address_set.filter(id=ids[0]).first()
            user.latestaddress.save()
        messages.success(request, 'Delete address: ' + address.name)
        address.delete()

        return HttpResponseRedirect(request.POST['redirect_to'])


class SettingsDeleteAddressView(LoginRequiredMixin, View):
    login_url = '/accounts/login'
    redirect_field_name = "redirect_to"

    def get(self, request, *args, **kwargs):
        user = User.objects.get(id=request.user.id)
        return HttpResponse(loader.render_to_string('komesapp/delete_address_confirmation_from_settings.html', context={
                'addresses': user.address_set.all(),
                'address': Address.objects.get(id=kwargs['address_id']),
                'previous_url': request.META['HTTP_REFERER']
            }, request=request))

    def post(self, request, *args, **kwargs):
        user = User.objects.get(id=request.user.id)
        address = user.address_set.filter(id=kwargs['address_id']).first()

        if user.latestaddress.address.id == address.id:
            ids = [address.id for address in user.address_set.all()]
            ids.remove(user.latestaddress.address.id)
            user.latestaddress.address = user.address_set.filter(id=ids[0]).first()
            user.latestaddress.save()
        messages.success(request, 'Delete address: ' + address.name)
        address.delete()

        return HttpResponseRedirect(request.POST['redirect_to'])

class OrderUpdateAddressView(LoginRequiredMixin, View):
    login_url = '/accounts/login'
    redirect_field_name = "redirect_to"

    def get(self, request, *args, **kwargs):
        user = User.objects.get(id=request.user.id)
        address = user.address_set.filter(id=kwargs['address_id']).first()
        # address to dictionary
        address_dict = model_to_dict(address)
        form = AddressForm(address_dict)

        return render(request, 'komesapp/address_update_modal_from_order.html', {
            'address': address,
            'address_form': form,
            'addresses': user.address_set.all(),
            'order': user.order_set.last(),
            'store': user.order_set.last().products.first().store
        })
    
    def post(self, request, *args, **kwargs):
        user = User.objects.get(id=request.user.id)
        address = user.address_set.filter(id=kwargs['address_id']).first()

        form = AddressForm(request.POST)
        if form.is_valid():
            address.name = form.cleaned_data.get('name')
            address.city = form.cleaned_data.get('city')
            address.subdistrict = form.cleaned_data.get('subdistrict')
            address.ward = form.cleaned_data.get('ward')
            address.address = form.cleaned_data.get('address')
            address.zipcode = form.cleaned_data.get('zipcode')
            address.save()

            return HttpResponseRedirect(reverse('orderaddress'))
        

class SettingsUpdateAddressView(LoginRequiredMixin, View):
    login_url = '/accounts/login'
    redirect_field_name = "redirect_to"

    def get(self, request, *args, **kwargs):
        user = User.objects.get(id=request.user.id)
        address = user.address_set.filter(id=kwargs['address_id']).first()
        # address to dictionary
        address_dict = model_to_dict(address)
        form = AddressForm(address_dict)

        return render(request, 'komesapp/address_update_modal_from_settings.html', {
            'address': address,
            'address_form': form,
        })
    
    def post(self, request, *args, **kwargs):
        user = User.objects.get(id=request.user.id)
        address = user.address_set.filter(id=kwargs['address_id']).first()

        form = AddressForm(request.POST)
        if form.is_valid():
            address.name = form.cleaned_data.get('name')
            address.city = form.cleaned_data.get('city')
            address.subdistrict = form.cleaned_data.get('subdistrict')
            address.ward = form.cleaned_data.get('ward')
            address.address = form.cleaned_data.get('address')
            address.zipcode = form.cleaned_data.get('zipcode')
            address.save()

            return HttpResponseRedirect(reverse('settingsaddress'))
        
class CheckoutView(LoginRequiredMixin, View):
    login_url = '/accounts/login'
    redirect_field_name = "redirect_to"

    # def get_rate(self):
    #     url = 'https://my-json-server.typicode.com/naufalmahing/fakejsonserver/couriers_api'

    #     payload = json.dumps({
    #     "origin_latitude": -6.3031123,
    #     "origin_longitude": 106.7794934999,
    #     "destination_latitude": -6.2441792,
    #     "destination_longitude": 106.783529,
    #     "couriers": "grab,jne,tiki",
    #     "items": [
    #         {
    #         "name": "Shoes",
    #         "description": "Black colored size 45",
    #         "value": 199000,
    #         "length": 30,
    #         "width": 15,
    #         "height": 20,
    #         "weight": 200,
    #         "quantity": 2
    #         }
    #     ]
    #     })
    #     headers = {
    #     'Content-Type': 'application/json',
    #     'Authorization': BITESHIP_TOKEN
    #     }

    #     # response = requests.request("POST", url, headers=headers, data=payload)

    #     response = requests.request('GET', url)

    #     return response.json()

    def get(self, request, *args, **kwargs):
        """get origin and address input
        then get courier input
        """
        
        # url = "https://api.biteship.com/v1/rates/couriers"
        url = 'https://my-json-server.typicode.com/naufalmahing/fakejsonserver/couriers_api'


        headers = {
            'Content-Type': 'application/json',
            'Authorization': BITESHIP_TOKEN
        }

        # get position from address provided
        user = User.objects.get(id=request.user.id)
        order = user.order_set.last()
        address = user.latestaddress.address
        store_address = user.order_set.last().products.first().store.address


        maps_api_url = 'https://api.biteship.com/v1/maps/areas'
        
        maps_api_res = requests.get(
            maps_api_url,headers=headers, params={
                'country': 'ID',
                'input': address.subdistrict,
                'type': 'single'
            }
        )

        areas = maps_api_res.json()['areas']

        area = [el['id'] for el in areas if 
        el['administrative_division_level_2_name'].lower() in address.city.lower() and 
        el['administrative_division_level_3_name'].lower() in address.subdistrict.lower() and
        el['postal_code'] == int(address.zipcode)]
        print(area)

        
        maps_api_res = requests.get(
            maps_api_url,headers=headers, params={
                'country': 'ID',
                'input': store_address.subdistrict,
                'type': 'single'
            }
        )
        areas = maps_api_res.json()['areas']

        # print(store_address.city)
        # print(areas[0]['administrative_division_level_2_name'])
        # print(store_address.subdistrict)
        # print(areas[0]['administrative_division_level_3_name'])
        # print(store_address.zipcode)
        # print(areas[0]['postal_code'])

        store_area = [el['id'] for el in areas if 
        el['administrative_division_level_2_name'].lower() in store_address.city.lower() and 
        el['administrative_division_level_3_name'].lower() in store_address.subdistrict.lower() and
        el['postal_code'] == int(store_address.zipcode)]
        print(store_area)
        
        if not store_area or not area: 
            if not store_area:
                messages.error(request, 'Store address is not valid in Indonesia, wait for the store to correct it')
            if not area:
                messages.error(request, 'User address is not valid in Indonesia, check if it is a correct address')

            return HttpResponseRedirect(reverse('order'))
        
        
        items = [
            {
            "name": product.name,
            "description": "",
            "value": int(product.price.amount),
            "length": 30,
            "width": 15,
            "height": 20,
            "weight": 200,
            "quantity": 1
            }
        for product in order.products.all()]
        print(items)

        # payload = json.dumps({
        #     "origin_area_id": store_area[0],
        #     "destination_area_id": area[0],
        #     "couriers": "paxel,jne,sicepat",
        #     "items": items
        # })

        payload = json.dumps({
        "origin_latitude": -6.3031123,
        "origin_longitude": 106.7794934999,
        "destination_latitude": -6.2441792,
        "destination_longitude": 106.783529,
        "couriers": "grab,jne,tiki",
        "items": [
            {
            "name": "Shoes",
            "description": "Black colored size 45",
            "value": 199000,
            "length": 30,
            "width": 15,
            "height": 20,
            "weight": 200,
            "quantity": 2
            }
        ]
        })

        # response = requests.request("POST", url, headers=headers, data=payload)

        response = requests.request('GET', url)

        # print(response)
        res = response.json()
        
        # res = self.get_rate()

        # print(res)

        # print('this is key: pricing')
        # print(res['pricing'])
        # d = [
        #     {
        #         'courier_name': element['courier_name'],
        #         'courier_service_name': element['courier_service_name'], 
        #         'duration': element['duration'], 
        #         'price': element['price']
        #     } for element in res['pricing']
        # ]

        rates = [d for d in res['pricing']]
        
        # print('this is d')
        # print(d)
        
        # access pricings from response
        # print(res['pricing'])
        
        shipment_form = ShipmentForm()

        order = Order.objects.get(id=kwargs['order_id'])
        address = User.objects.get(id=request.user.id).latestaddress.address
        
        return render(request, 'komesapp/checkout.html', {
            'order': order,
            'shipment_form': shipment_form,
            'address': address,
            'shipments': rates,
            'store': User.objects.get(id=request.user.id).store
        })
    
    def post(self, request, *args, **kwargs):
        # send message if no address
        if request.POST['address'] == '':
            messages.error(request, 'Use an address')
            return HttpResponseRedirect(reverse('checkout', kwargs={
                'order_id': kwargs['order_id']
            }))
        elif not Address.objects.filter(name=request.POST['address']):
            messages.error(request, 'Can not find address')
            return HttpResponseRedirect(reverse('checkout', kwargs={
                'order_id': kwargs['order_id']
            }))
        elif request.POST['courier-name'] == '':
            messages.error(request, 'Choose a courier')
            return HttpResponseRedirect(reverse('checkout', kwargs={
                'order_id': kwargs['order_id']
            }))
        
        return HttpResponseRedirect(reverse('buy'), kwargs={
            'order_id': kwargs['order_id']
        })
    
class SuccessPaymentView(LoginRequiredMixin, View):
    login_url = '/accounts/login'
    redirect_field_name = "redirect_to"

    def get(self, request):
        messages.success(request, 'Payment success')

        user = User.objects.get(id=request.user.id)
        last_order = user.order_set.last()
        last_order.active = False
        last_order.save()

        user.order_set.create()
        
        return HttpResponseRedirect(reverse('index'))

class ErrorPaymentView(LoginRequiredMixin, View):
    login_url = '/accounts/login'
    redirect_field_name = "redirect_to"

    def get(self, request):
        messages.error(request, 'Payment error')
        return HttpResponseRedirect(reverse('buy', kwargs={
            'order_id': User.objects.get(id=request.user.id).order_set.last().id
        }))

class UnfinishedPaymentView(LoginRequiredMixin, View):
    login_url = '/accounts/login'
    redirect_field_name = "redirect_to"

    def get(self, request):
        messages.warning(request, 'Payment unfinished')
        return HttpResponseRedirect(reverse('buy', kwargs={
            'order_id': User.objects.get(id=request.user.id).order_set.last().id
        }))