from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Product, Cart, CartItem, Seller
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.http import JsonResponse
from .forms import SellerCreationForm, ProductForm, SellerUpdateForm
from django.contrib.auth.models import User

def home(request):
    products = Product.objects.filter(seller__is_approved=True) | Product.objects.filter(seller__isnull=True)
    return render(request, 'store/home.html', {'products': products})

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'store/product_detail.html', {'product': product})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    success = False
    message = ""
    
    if not item_created:
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
            cart_item.save()
            success = True
            message = f"Added {product.name} to cart."
            messages.success(request, message)
        else:
            message = "Cannot add more items. Stock limit reached."
            messages.error(request, message)
    else:
        if product.stock > 0:
            cart_item.save()
            success = True
            message = f"Added {product.name} to cart."
            messages.success(request, message)
        else:
            message = "Product out of stock."
            messages.error(request, message)
    
    # Handle AJAX request
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        cart_count = cart.items.count()  # type: ignore # Get updated cart item count
        return JsonResponse({
            'success': success,
            'message': message,
            'cart_count': cart_count
        })
    
    # Fallback for non-AJAX (redirect to referer or home)
    referer = request.META.get('HTTP_REFERER', 'store:home')
    return redirect(referer)
@login_required
def cart(request):
    cart = get_object_or_404(Cart, user=request.user)
    return render(request, 'store/cart.html', {'cart': cart})

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect('store:cart')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('store:home')
    else:
        form = UserCreationForm()
    return render(request, 'store/signup.html', {'form': form})

def custom_logout(request):
    logout(request)
    return redirect('store:home')

# Helper function to check if user is superuser
def is_superuser(user):
    return user.is_superuser

def is_seller(user):
    return hasattr(user, 'seller')

# Superuser views for seller management
@user_passes_test(is_superuser)
def create_seller(request):
    if request.method == 'POST':
        form = SellerCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Seller account created successfully!')
            return redirect('store:manage_sellers')
    else:
        form = SellerCreationForm()
    return render(request, 'store/create_seller.html', {'form': form})

@user_passes_test(is_superuser)
def manage_sellers(request):
    sellers = Seller.objects.all().order_by('-created_at')
    return render(request, 'store/manage_sellers.html', {'sellers': sellers})

@user_passes_test(is_superuser)
def approve_seller(request, seller_id):
    seller = get_object_or_404(Seller, id=seller_id)
    seller.is_approved = True
    seller.save()
    messages.success(request, f'Seller {seller.business_name} has been approved!')
    return redirect('store:manage_sellers')

@user_passes_test(is_superuser)
def disapprove_seller(request, seller_id):
    seller = get_object_or_404(Seller, id=seller_id)
    seller.is_approved = False
    seller.save()
    messages.warning(request, f'Seller {seller.business_name} has been disapproved!')
    return redirect('store:manage_sellers')

# Seller views
@login_required
@user_passes_test(is_seller)
def seller_dashboard(request):
    seller = request.user.seller
    products = seller.products.all()
    return render(request, 'store/seller_dashboard.html', {
        'seller': seller,
        'products': products
    })

@login_required
@user_passes_test(is_seller)
def add_product(request):
    if not request.user.seller.is_approved:
        messages.error(request, 'Your seller account is not approved yet.')
        return redirect('store:seller_dashboard')
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user.seller
            product.save()
            messages.success(request, 'Product added successfully!')
            return redirect('store:seller_dashboard')
    else:
        form = ProductForm()
    return render(request, 'store/add_product.html', {'form': form})

@login_required
@user_passes_test(is_seller)
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, seller=request.user.seller)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('store:seller_dashboard')
    else:
        form = ProductForm(instance=product)
    return render(request, 'store/edit_product.html', {'form': form, 'product': product})

@login_required
@user_passes_test(is_seller)
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, seller=request.user.seller)
    
    if request.method == 'GET':
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect('store:seller_dashboard')
    
    return render(request, 'store/seller_dashboard.html', {'product': product})

@login_required
@user_passes_test(is_seller)
def seller_profile(request):
    seller = request.user.seller
    
    if request.method == 'POST':
        form = SellerUpdateForm(request.POST, instance=seller)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('store:seller_profile')
    else:
        form = SellerUpdateForm(instance=seller)
    
    return render(request, 'store/seller_profile.html', {'form': form, 'seller': seller})