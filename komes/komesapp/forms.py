from django import forms

from . models import Product

from djmoney.forms.fields import MoneyField

class StoreForm(forms.Form):
    name = forms.CharField(label='Store name', max_length=100)
    description = forms.CharField(label='Store description', widget=forms.Textarea(), required=False)

class ProductForm(forms.Form):
    name = forms.CharField(label='Product name', max_length=100)
    description = forms.CharField(label='Product description', widget=forms.Textarea(), required=False)
    price = MoneyField(max_digits=19, decimal_places=4, default_currency='IDR')
    

class ProductImageForm(forms.ModelForm):
    class Meta:
        model=Product
        fields=[
            'photo'
        ]

class BuyForm(forms.Form):
    """input of payment and shipment method"""
    pass