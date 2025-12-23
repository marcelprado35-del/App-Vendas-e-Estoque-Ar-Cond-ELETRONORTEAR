from django import forms
from .models import Product, Customer, Seller, Sale, SaleItem

class SellerForm(forms.ModelForm):
    class Meta:
        model = Seller
        fields = '__all__'

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['customer', 'seller']
        labels = {
            'customer': 'Cliente',
            'seller': 'Vendedor',
        }

class SaleItemForm(forms.ModelForm):
    class Meta:
        model = SaleItem
        fields = ['product', 'quantity', 'lote']
        labels = {
            'product': 'Produto',
            'quantity': 'Quantidade',
            'lote': 'Lote',
        }

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'
