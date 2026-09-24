from django.contrib import admin
from .models import Home_Collection, Shop_All, Cart, CartItem, ClientReview, ContactMessage, Order

# Register your models
admin.site.register(Home_Collection)
admin.site.register(Shop_All)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(ClientReview)
admin.site.register(ContactMessage)
admin.site.register(Order)
