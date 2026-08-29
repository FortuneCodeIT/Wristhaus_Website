from django.db import models
from django.conf import settings
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
    
    
    