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

from .forms import StoreForm, ProductForm, ProductImageForm, ShipmentForm, AddressForm

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
        
        return render(request, 'komesapp/order.html', {
            'order': order
        })
    
    def post(self, request, *args, **kwargs):
        product = Product.objects.get(id=kwargs['product_id'])

        order = Order.objects.filter(user__id=request.user.id, active=True).last()
        if not order:
            order = Order(user=User.objects.get(id=request.user.id))
            order.save()
        
        OrderProduct(product=product, order=order).save()
        messages.success(request, 'Product added to order')
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
        
        return render(request, 'komesapp/settings.html', {
            'has_store': has_store,
            'address': User.objects.get(id=request.user.id).latestaddress.address
        })
    
class CreateStoreView(LoginRequiredMixin, View):
    login_url = '/accounts/login'
    redirect_field_name = "redirect_to"
    
    def get(self, request):
        form = StoreForm() 
        return render(request, 'komesapp/createstore.html', {
            'form': form
        })
    
    def post(self, request):
        form = StoreForm(request.POST)
        if form.is_valid():
            store = Store(
                name=form.cleaned_data.get('name'), description=form.cleaned_data.get('description'),
                owner=request.user
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
        store = Store.objects.get(id=kwargs['store_id'])
        # store = Store.objects.filter(owner__id=request).first()
        return render(request, 'komesapp/storedetail.html', {
            'store': store
        })
    
class UpdateStoreView(LoginRequiredMixin, View):
    login_url = '/accounts/login'
    redirect_field_name = "redirect_to"

    def get(self, request, *args, **kwargs):
        store = Store.objects.get(id=kwargs['store_id'])
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
        store = Store.objects.get(id=kwargs['store_id'])
        if form.is_valid():
            store.name = form.cleaned_data.get('name')
            store.description = form.cleaned_data.get('description')
            store.save()
            return HttpResponseRedirect(reverse('storedetail', kwargs={
                'store_id':store.id
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
                "gross_amount": 200000
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

    def post(self, request, *args, **kwags):
        pass

class LatestAddressView(LoginRequiredMixin, View):
    login_url = '/accounts/login'
    redirect_field_name = "redirect_to"

    def post(self, request, *args, **kwargs):
        address_id = kwargs['address_id']

        user = User.objects.get(id=request.user.id)
        latest_address  = user.latestaddress
        latest_address.address = Address.objects.get(id=address_id)
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
        user.latestaddress_set.address = Address.objects.get(request.JSON['address_id'])
        user.save()

        return HttpResponseRedirect(reverse('')) # this the one that needs dynamic return url
        
class OrderChangeAddressModalView(LoginRequiredMixin, View):
    login_url = '/accounts/login'
    redirect_field_name = "redirect_to"

    def get(self, request):
        # get user
        user = User.objects.get(id=request.user.id)

        # print(user.order_set.last())
        # print(type(user.order_set.last()))
        # print(user.order_set.last().products)
        # print(user.order_set.all())
        return HttpResponse(loader.render_to_string('komesapp/address_change_modal_from_order.html', context={
            'addresses': user.address_set.all(),
            'address': user.latestaddress.address,
            'order': user.order_set.last()
        }, request=request))
    
        """v.1
        fix with render???"""
    

    def post(self, request):
        user = User.objects.get(id=request.user.id)
        user.latestaddress_set.address = Address.objects.get(request.JSON['address_id'])
        user.save()

        # return HttpResponseRedirect(reverse('checkout', kwargs={
        #     'order_id': user.order_set.last().id
        # })) # this the one that needs dynamic return url

        return render(request, 'komesapp/order.html', {
            'address': user.latestaddress.address,
            'order': user.order_set.last()
        })
    
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
        user = User.objects.get(id=request.user.id)
        user.latestaddress_set.address = Address.objects.get(request.JSON['address_id'])
        user.save()

        return HttpResponseRedirect(reverse('settings')) # this the one that needs dynamic return url

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
            
            return HttpResponseRedirect(reverse('orderaddress'))
        

class SettingsCreateAddressModalView(LoginRequiredMixin, View):
    login_url = '/accounts/login'
    redirect_field_name = "redirect_to"

    def get(self, request):
        form = AddressForm()
        
        # return render(request, 'komesapp/create_address.html', context={
        #     'address_form': form
        # })
    
        return HttpResponse(loader.render_to_string('komesapp/address_input_modal_from_settings.html', context={
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
            
            return HttpResponseRedirect(reverse('settingsaddress'))

class DeleteAddressView(LoginRequiredMixin, View):
    login_url = '/accounts/login'
    redirect_field_name = "redirect_to"

    def get(self, request, *args, **kwargs):
        user = User.objects.get(id=request.user.id)
        return HttpResponse(loader.render_to_string('komesapp/delete_address_confirmation.html', context={
                'addresses': user.address_set.all(),
                'address': user.latestaddress.address,
                'order': user.order_set.last()
            }, request=request))

    def post(self, request, *args, **kwargs):
        address = Address.objects.get(id=kwargs['address_id'])
        user = User.objects.get(id=request.user.id)
        if user.latestaddress.address.id == address.id:
            ids = [address.id for address in user.address_set.all()]
            ids.remove(user.latestaddress.address.id)
            user.latestaddress.address = user.address_set.get(id=ids[0])
            user.latestaddress.save()
        address.delete()
        return HttpResponse(status=200)


class UpdateAddressView(LoginRequiredMixin, View):
    login_url = '/accounts/login'
    redirect_field_name = "redirect_to"

    def get(self, request, *args, **kwargs):
        user = User.objects.get(id=request.user.id)
        address = user.address_set.filter(id=kwargs['address_id'])
        # address to dictionary
        address_dict = address.value().first()
        form = AddressForm(instance=address) # this form doesn't use ModelForm

        return render(request, 'komesapp/address_input.html', {
            'address_form': form
        })
    
    def post(self, request, *args, **kwargs):
        user = User.objects.get(id=request.user.id)
        address = user.address_set.filter(id=kwargs['address_id'])

        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('address')) # idk if this is the right page to return, might need dynamic return page
        
class CheckoutView(LoginRequiredMixin, View):
    login_url = '/accounts/login'
    redirect_field_name = "redirect_to"

    def get(self, request, *args, **kwargs):
        """get origin and address input
        then get courier input
        """
        
        # url = "https://api.biteship.com/v1/rates/couriers"
        url = 'https://my-json-server.typicode.com/naufalmahing/fakejsonserver/couriers_api'

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
        headers = {
        'Content-Type': 'application/json',
        'Authorization': BITESHIP_TOKEN
        }

        # response = requests.request("POST", url, headers=headers, data=payload)

        response = requests.request('GET', url)

        res = response.json()
        
        # access pricings from response
        # print(res['pricing'])
        
        shipment_form = ShipmentForm()

        order = Order.objects.get(id=kwargs['order_id'])
        address = User.objects.get(id=request.user.id).latestaddress.address
        
        return render(request, 'komesapp/checkout.html', {
            'order': order,
            'shipment_form': shipment_form,
            'address': address
        })
    
    def post(self, request, *args, **kwargs):
        # logic
        return HttpResponseRedirect(reverse('buy'), kwargs={
            'order_id': kwargs['order_id']
        })