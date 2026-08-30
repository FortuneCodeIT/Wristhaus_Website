from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    # path('product/<slug:slug>/', views.product_detail, name='product_detail'),  # NEW
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('shop/', views.shop, name='shop'),
    # NEW: Cart URLs
    path('cart/', views.cart_page, name='cart_page'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('delete-from-cart/', views.delete_from_cart, name='delete_from_cart'),
    path('delete-all-from-cart/', views.delete_all_from_cart, name='delete_all_from_cart'),
    path('checkout/', views.checkout_to_whatsapp, name='checkout_to_whatsapp'),
    path('collections/', views.collections, name='collections'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('track-order/', views.track_order, name='track_order'),
    path('update-cart-quantity/', views.update_cart_quantity, name='update_cart_quantity'),
    

        # Admin Authentication URLs - NEW
    path('admin/login/', views.admin_login, name='admin_login'),
    path('admin/logout/', views.admin_logout, name='admin_logout'),
    
    
        # Admin Profile URLs - NEW
    path('dashboard/profile/', views.admin_profile, name='admin_profile'),
    path('dashboard/profile/change-password/', views.admin_change_password, name='admin_change_password'),
    
        # Admin Reviews URLs - NEW
    path('admin/reviews/', views.admin_review, name='admin_review'),
    path('admin/reviews/add/', views.admin_review_add, name='admin_review_add'),
    path('admin/reviews/edit/<int:review_id>/', views.admin_review_edit, name='admin_review_edit'),
    path('admin/reviews/delete/<int:review_id>/', views.admin_review_delete, name='admin_review_delete'),
    path('admin/reviews/approve/<int:review_id>/', views.admin_review_approve, name='admin_review_approve'),
    
     # Admin URLs
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/products/', views.admin_products, name='admin_products'),
    path('admin/products/add/', views.admin_product_add, name='admin_product_add'),
    path('admin/products/edit/<int:product_id>/', views.admin_product_edit, name='admin_product_edit'),
    path('admin/products/delete/<int:product_id>/', views.admin_product_delete, name='admin_product_delete'),
    path('admin/orders/', views.admin_orders, name='admin_orders'),
    path('admin/orders/detail/<int:order_id>/', views.admin_order_detail, name='admin_order_detail'), # ✅ Changed to order_id
    path('admin/orders/delete/<int:order_id>/', views.admin_order_delete, name='admin_order_delete'),
    path('admin/orders/approve/<int:order_id>/', views.admin_order_approve, name='admin_order_approve'),
    path('admin/orders/process/<int:order_id>/', views.admin_order_process, name='admin_order_process'),
    path('admin/orders/cancel/<int:order_id>/', views.admin_order_cancel, name='admin_order_cancel'),

]