import os
import platform

from django import get_version as django_version
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, UpdateView, DeleteView

from .forms import SaleForm, ProductForm, CustomerForm, SellerForm
from .models import Product, Customer, Seller, Sale, SaleItem


def index(request):
    """Render the landing screen with loader and environment details."""

    host_name = request.get_host().lower()

    agent_brand = "AppWizzy" if host_name == "appwizzy.com" else "Flatlogic"

    now = timezone.now()

    products = Product.objects.all()

    context = {
        "products": products,
        "project_name": "New Style",
        "agent_brand": agent_brand,
        "django_version": django_version(),
        "python_version": platform.python_version(),
        "current_time": now,
        "host_name": host_name,
        "project_description": os.getenv("PROJECT_DESCRIPTION", ""),
        "project_image_url": os.getenv("PROJECT_IMAGE_URL", ""),
    }

    return render(request, "core/index.html", context)


def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'core/customer_list.html', {'customers': customers})


class CustomerCreateView(CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'core/customer_form.html'
    success_url = reverse_lazy('customer_list')


class CustomerUpdateView(UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'core/customer_form.html'
    success_url = reverse_lazy('customer_list')


class CustomerDeleteView(DeleteView):
    model = Customer
    template_name = 'core/customer_confirm_delete.html'
    success_url = reverse_lazy('customer_list')


class SellerCreateView(CreateView):
    model = Seller
    form_class = SellerForm
    template_name = 'core/seller_form.html'
    success_url = reverse_lazy('seller-list')


class SellerUpdateView(UpdateView):
    model = Seller
    form_class = SellerForm
    template_name = 'core/seller_form.html'
    success_url = reverse_lazy('seller-list')


class SellerDeleteView(DeleteView):
    model = Seller
    template_name = 'core/seller_confirm_delete.html'
    success_url = reverse_lazy('seller-list')


def seller_list(request):
    """Render the seller list page."""

    sellers = Seller.objects.all()

    context = {"sellers": sellers}

    return render(request, "core/seller_list.html", context)


import logging

def sale_list(request):
    """Render the sale list page."""

    logging.info("Sale list view called")

    sales = Sale.objects.select_related('customer', 'seller').all()
    logging.info(f"Sales: {sales}")

    context = {"sales": sales}

    return render(request, "core/sale_list.html", context)


from django.forms import inlineformset_factory
from django.db import transaction
from .forms import SaleForm, ProductForm, CustomerForm, SellerForm, SaleItemForm
def sale_create(request):
    SaleItemFormSet = inlineformset_factory(
        Sale, SaleItem, form=SaleItemForm, extra=1, can_delete=True
    )
    if request.method == 'POST':
        form = SaleForm(request.POST)
        formset = SaleItemFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                sale = form.save(commit=False)
                # Initialize calculated fields
                sale.total_amount = 0
                sale.commission_amount = 0
                sale.save()  # Save sale to get an ID for the formset

                formset.instance = sale
                sale_items = formset.save(commit=False)

                total_amount = 0
                commission_amount = 0

                for item in sale_items:
                    # Freeze price at the time of sale
                    item.price = item.product.price
                    
                    # Determine commission rate: Use seller's rate if > 0, otherwise fallback to product's rate
                    if sale.seller and sale.seller.commission > 0:
                        item.commission_rate = sale.seller.commission
                    else:
                        item.commission_rate = item.product.commission_rate
                    item.save()

                    # Calculate totals
                    item_total = item.price * item.quantity
                    total_amount += item_total
                    commission_amount += item_total * (item.commission_rate / 100)
                
                # Update the sale instance with calculated totals
                sale.total_amount = total_amount
                sale.commission_amount = commission_amount
                sale.save()

            return redirect('sale_list')
    else:
        form = SaleForm()
        formset = SaleItemFormSet()
    
    return render(request, 'core/sale_create.html', {'form': form, 'formset': formset})

def sale_update(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    SaleItemFormSet = inlineformset_factory(
        Sale, SaleItem, form=SaleItemForm, extra=1, can_delete=True
    )

    if request.method == 'POST':
        form = SaleForm(request.POST, instance=sale)
        formset = SaleItemFormSet(request.POST, instance=sale)

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                sale = form.save()

                # Handle deleted items first
                for form in formset.deleted_forms:
                    if form.instance.pk:
                        form.instance.delete()

                # Handle new and changed items
                sale_items = formset.save(commit=False)
                for item in sale_items:
                    if not item.pk:  # If it's a new item
                        item.price = item.product.price
                    # Commission rate will be set in the recalculation step
                    item.save()
                formset.save_m2m()

                # Recalculate total amount and commission from all valid items
                total_amount = 0
                commission_amount = 0
                for item in sale.items.all():
                    # Determine and save the correct commission rate for every item
                    if sale.seller and sale.seller.commission > 0:
                        item.commission_rate = sale.seller.commission
                    else:
                        item.commission_rate = item.product.commission_rate
                    item.save()

                    item_total = item.price * item.quantity
                    total_amount += item_total
                    commission_amount += item_total * (item.commission_rate / 100)
                
                sale.total_amount = total_amount
                sale.commission_amount = commission_amount
                sale.save()

            return redirect('sale_list')
    else:
        form = SaleForm(instance=sale)
        formset = SaleItemFormSet(instance=sale)

    return render(request, 'core/sale_form.html', {'form': form, 'formset': formset, 'sale': sale})




def product_list(request):
    products = Product.objects.all()
    return render(request, 'core/product_list.html', {'products': products})


class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'core/product_form.html'
    success_url = reverse_lazy('product_list')


class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'core/product_form.html'
    success_url = reverse_lazy('product_list')


class ProductDeleteView(DeleteView):
    model = Product
    template_name = 'core/product_confirm_delete.html'
    success_url = reverse_lazy('product_list')



class SaleDeleteView(DeleteView):
    model = Sale
    template_name = 'core/sale_confirm_delete.html'
    success_url = reverse_lazy('sale_list')