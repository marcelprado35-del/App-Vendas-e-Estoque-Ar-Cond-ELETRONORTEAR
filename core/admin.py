from django.contrib import admin
from .models import Product, Customer, Seller, Sale, SaleItem


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "stock_quantity")

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone")

@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "commission")

class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "sale_date", "total_amount")
    inlines = [SaleItemInline]
