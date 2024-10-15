from collections.abc import Callable
from typing import Any, Mapping, Sequence
from django import forms
from django.forms.renderers import BaseRenderer
from django.forms.utils import ErrorList

from . models import Product

from djmoney.forms.fields import MoneyField

import requests

class StoreForm(forms.Form):
    name = forms.CharField(label='Store name', max_length=100)
    description = forms.CharField(label='Store description', widget=forms.Textarea(), required=False)

class ProductForm(forms.Form):
    name = forms.CharField(label='Product name', max_length=100)
    description = forms.CharField(label='Product description', widget=forms.Textarea(), required=False)
    price = MoneyField(max_digits=19, decimal_places=2, default_currency='IDR')
    

class ProductImageForm(forms.ModelForm):
    class Meta:
        model=Product
        fields=[
            'photo'
        ]

class AddressForm(forms.Form):
    name = forms.CharField(label='Name', max_length=250)
    city = forms.CharField(label='City', max_length=100)
    subdistrict = forms.CharField(label='Subdistrict', max_length=150)
    ward = forms.CharField(label='Ward', max_length=200)
    address = forms.CharField(widget=forms.Textarea())
    zipcode = forms.CharField(label='Zip Code', max_length=20)

class CreateStoreForm(forms.Form):
    store_name = forms.CharField(label='Store name', max_length=100)
    description = forms.CharField(label='Store description', widget=forms.Textarea(), required=False)

    address_name = forms.CharField(label='Address Name', max_length=250)
    city = forms.CharField(label='City', max_length=100)
    subdistrict = forms.CharField(label='Subdistrict', max_length=150)
    ward = forms.CharField(label='Ward', max_length=200)
    address = forms.CharField(widget=forms.Textarea())
    zipcode = forms.CharField(label='Zip Code', max_length=20)

class ChooseAddessForm(forms.Form):
    pass

class CustomChoice(forms.ChoiceField):
    
    def __init__(self, *, choices=(), **kwargs):
        super().__init__(**kwargs)
        self.choices = [
            ("FR", "Freshman"),
            ("SO", "Siiiiiiiiii"),
            ("JR", "Junior"),
            ("SR", "Senior"),
            ("GR", "Graduate"),
        ]

    def get_courier_data(self):
        url = 'https://my-json-server.typicode.com/naufalmahing/fakejsonserver/couriers_api'
        response = requests.request('GET', url)

        res = response.json()
        res['pricing']

class ShipmentForm(forms.Form):
    idk = [
        ("FR", "Freshman"),
        ("SO", "Sophomore"),
        ("JR", "Junior"),
        ("SR", "Senior"),
        ("GR", "Graduate"),
    ]
    courier = CustomChoice(label='Courier')
    """call api to get available couriers and display to form"""

class BuyForm(forms.Form):
    """input of payment and shipment method"""
    pass