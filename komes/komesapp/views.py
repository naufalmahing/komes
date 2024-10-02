from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.views import View

from django.views.generic.edit import DeleteView

from django.shortcuts import render

from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy

from django.contrib import messages

from django.contrib.auth.models import User
from .models import (
    Store,
    Product,
    Tag,
    Order,
    OrderProduct,
)

from .forms import StoreForm, ProductForm, ProductImageForm

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
            'has_store': has_store
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

        return render(request, 'komesapp/buy.html', {
            'total_payment': order.get_total_payment(),
            'order': order
        })

    def post(self, request, *args, **kwags):
        pass