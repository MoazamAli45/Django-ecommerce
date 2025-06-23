from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'store'

urlpatterns = [
    # Original URLs
    path('', views.home, name='home'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart, name='cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='store/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='store/logout.html', next_page='store:home'), name='logout'),
    
    # Superuser seller management URLs (changed from admin/ to management/)
    path('management/create-seller/', views.create_seller, name='create_seller'),
    path('management/manage-sellers/', views.manage_sellers, name='manage_sellers'),
    path('management/approve-seller/<int:seller_id>/', views.approve_seller, name='approve_seller'),
    path('management/disapprove-seller/<int:seller_id>/', views.disapprove_seller, name='disapprove_seller'),
    
    # Seller URLs
    path('seller/dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('seller/add-product/', views.add_product, name='add_product'),
    path('seller/edit-product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('seller/delete-product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('seller/profile/', views.seller_profile, name='seller_profile'),
]