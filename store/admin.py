from django.contrib import admin
from .models import Product, Cart, CartItem, Seller

@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'user', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('business_name', 'user__username', 'user__email')
    actions = ['approve_sellers', 'disapprove_sellers']

    def approve_sellers(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, f"{queryset.count()} sellers approved.")
    approve_sellers.short_description = "Approve selected sellers"

    def disapprove_sellers(self, request, queryset):
        queryset.update(is_approved=False)
        self.message_user(request, f"{queryset.count()} sellers disapproved.")
    disapprove_sellers.short_description = "Disapprove selected sellers"

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'seller', 'price', 'stock', 'created_at')
    list_filter = ('seller', 'created_at')
    search_fields = ('name', 'description', 'seller__business_name')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    search_fields = ('user__username',)

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity')
    list_filter = ('cart__user',)