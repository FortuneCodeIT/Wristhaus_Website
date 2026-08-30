import uuid
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.text import slugify


# Your existing models
class Home_Collection(models.Model):
    CATEGORY_CHOICES = [
        ('watches', 'Watches'),
        ('bracelets', 'Bracelets'),
        ('smart-access', 'Smart Access'),
        ('combo', 'Combo'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to='product_images/')
    stock = models.IntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.name
    

class Shop_All(models.Model):
    CATEGORY_CHOICES = [
        ('watches', 'Watches'),
        ('bracelets', 'Bracelets'),
        ('smart-accessories', 'Smart Accessories'),
        ('combo', 'Combo'),
    ]
    name = models.CharField(max_length=200)
    # slug = models.SlugField(unique=True, blank=True, null=True)  # NEW: Add this
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    stock = models.IntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.name
    
    def get_image_url(self):
        """Get the full image URL for WhatsApp"""
        if not self.image:
            return None

        return (
            f"{settings.SUPABASE_URL}"
            f"/storage/v1/object/public/media"
            f"/{self.image.name}"
        )
    
    # def save(self, *args, **kwargs):
    #     if not self.slug:          
    #         self.slug = slugify(self.name)
    #     super().save(*args, **kwargs)

# NEW: Add these models for cart functionality
class Cart(models.Model):
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def get_total_price(self):
        return sum(item.get_total_price() for item in self.items.all())
    
    def get_total_items(self):
        return sum(item.quantity for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Shop_All, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    
    class Meta:
        # This prevents duplicate cart items for the same product
        unique_together = ('cart', 'product')
    
    def get_total_price(self):
        return self.product.price * self.quantity
    
    def __str__(self):
        return f"{self.product.name} x{self.quantity} (Cart {self.cart.id})"

class ClientReview(models.Model):
    RATING_CHOICES = [
        (1, '⭐'),
        (2, '⭐⭐'),
        (3, '⭐⭐⭐'),
        (4, '⭐⭐⭐⭐'),
        (5, '⭐⭐⭐⭐⭐'),
    ]
        
    name = models.CharField(max_length=100)
    review = models.TextField()
    rating = models.IntegerField(choices=RATING_CHOICES, default=5)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.rating} stars"
    
    

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    order_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
      
    # User who placed the order (if logged in)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Session key for guest users
    session_key = models.CharField(max_length=40, null=True, blank=True)
    
    # Order items stored as JSON
    items = models.JSONField(default=list)
    
    # Order totals
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_items = models.IntegerField(default=0)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    def save(self, *args, **kwargs):
    # Generate unique order number if not set
        if not self.order_number:
            self.order_number = f"WH-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
        
    def get_status_display_custom(self):
        """Get status with emoji"""
        status_map = {
            'pending': '⏳ Pending',
            'processing': '🔄 Processing',
            'completed': '✅ Completed',
            'cancelled': '❌ Cancelled',
        }
        return status_map.get(self.status, self.status)
    
    def get_status_color(self):
        """Get status color for frontend"""
        color_map = {
            'pending': '#ffc107',
            'processing': '#17a2b8',
            'completed': '#28a745',
            'cancelled': '#dc3545',
        }
        return color_map.get(self.status, '#6c757d')
  
    
    def __str__(self):
        return f"Order #{self.id} - {self.get_status_display()}"
    
    def get_status_order(self):
        """Get the order index of current status for timeline"""
        status_order = ['pending', 'processing', 'completed', 'cancelled']
        try:
            return status_order.index(self.status)
        except ValueError:
            return 0
    
    class Meta:
        ordering = ['-created_at']
        
