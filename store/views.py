from django.db import models 
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q 
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib import messages
from django.db import transaction
from django.views.decorators.http import require_POST
from .models import Home_Collection, Shop_All, Cart, CartItem, ClientReview
from .forms import ProductForm, ReviewForm, AdminProfileForm, AdminPasswordChangeForm  # We'll create this
from django.utils import timezone
import urllib.parse

import json
import logging

logger = logging.getLogger(__name__)

# UPDATED: Better session handling
def get_or_create_cart(request):
    """Get or create a cart for the current user/session"""
    # if request.user.is_authenticated:
    #     cart, created = Cart.objects.get_or_create(
    #         user=request.user,
    #         defaults={'session_key': request.session.session_key or ''}
    #     )
    #     return cart
    
    if not request.session.session_key:
        request.session.save()
    session_key = request.session.session_key
    
    cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart

# Your existing index view
def index(request):
    """Home page with category cards"""
    home_collections = Home_Collection.objects.all().order_by('-created_at')
    reviews = ClientReview.objects.all().order_by('-created_at')[:4]
    cart = get_or_create_cart(request)
    cart_count = cart.get_total_items()
    
    # Get products for each category (4 products per category)
    categories = []
    category_choices = Shop_All.CATEGORY_CHOICES
    
    for category_code, category_name in category_choices:
        products = Shop_All.objects.filter(category=category_code)[:4]
        if products.exists():
            categories.append({
                'code': category_code,
                'name': category_name,
                'products': products,
                'count': products.count()
            })
    
    context = {
        'home_collections': home_collections,
        'reviews': reviews,
        'cart': cart,
        'cart_count': cart_count,
        'categories': categories,
        'now': timezone.now(),
    }
    
    return render(request, 'index.html', context)

# Your existing shop view
def shop(request):
    category_filter = request.GET.get('category', 'all')
    search_query = request.GET.get('search', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    
     # Start with all products
    shop_alls = Shop_All.objects.all().order_by('-created_at')
    
    if category_filter and category_filter != 'all':
        shop_alls = shop_alls.filter(category=category_filter)
              
        # Apply search filter
    if search_query:
        shop_alls = shop_alls.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(category__icontains=search_query)
        )
    
    # Apply price range filter
    if min_price:
        shop_alls = shop_alls.filter(price__gte=min_price)
    if max_price:
        shop_alls = shop_alls.filter(price__lte=max_price)
    
    all_products = Shop_All.objects.all()
    min_product_price = all_products.aggregate(models.Min('price'))['price__min'] or 0
    max_product_price = all_products.aggregate(models.Max('price'))['price__max'] or 100000
    

    
    paginator = Paginator(shop_alls, 12)
    page = request.GET.get('page')
    
    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        products_page = paginator.page(1)
    except EmptyPage:
        products_page = paginator.page(paginator.num_pages)
    
    cart = get_or_create_cart(request)
    cart_count = cart.get_total_items()
    categories = Shop_All.CATEGORY_CHOICES
    
    context = {
        'shop_alls': products_page,
        'categories': categories,
        'active_category': category_filter or 'all',
        'cart_count': cart_count,
        'now': timezone.now(),
        'search_query': search_query,
        'min_price': min_price or min_product_price,
        'max_price': max_price or max_product_price,
        'min_product_price': int(min_product_price),
        'max_product_price': int(max_product_price),
        'has_filters': bool(search_query or min_price or max_price or category_filter != 'all'),
    }
    
    return render(request, 'shop.html', context)


# UPDATED: Add to cart with stock check
def add_to_cart(request):
    logger.info("=== ADD TO CART REQUEST RECEIVED ===")
    
    if request.method == 'POST':
        try:
            # Get product ID and quantity
            data = json.loads(request.body)
            product_id = data.get('product_id')
            quantity = int(data.get('quantity', 1))
            
            logger.info(f"Product ID: {product_id}, Quantity: {quantity}")
            
            if not product_id:
                return JsonResponse({'success': False, 'error': 'Product ID required'})
            
            # Get product and check stock
            product = get_object_or_404(Shop_All, id=product_id)
            
            # Check if enough stock
            if product.stock < quantity:
                return JsonResponse({
                    'success': False, 
                    'error': f'Sorry, only {product.stock} items available in stock.'
                })
            
            # Get or create cart
            cart = get_or_create_cart(request)
            
            # Check if product already in cart
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': 0}  # Start with 0, we'll add below
            )
            
            # Calculate new quantity
            new_quantity = cart_item.quantity + quantity
            
            # Check if total quantity exceeds stock
            if new_quantity > product.stock:
                return JsonResponse({
                    'success': False,
                    'error': f'Cannot add more. Only {product.stock} items available in stock.'
                })
            
            # Update cart item quantity
            cart_item.quantity = new_quantity
            cart_item.save()
            
            # REDUCE STOCK IMMEDIATELY
            product.stock -= quantity
            product.save()
            
            logger.info(f"Stock reduced. New stock: {product.stock}")
            
            cart_count = cart.get_total_items()
            
            return JsonResponse({
                'success': True,
                'cart_count': cart_count,
                'message': f'{product.name} added to cart! ({quantity} item(s))',
                'remaining_stock': product.stock
            })
            
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

# UPDATED: Delete from cart with stock restore
def delete_from_cart(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            
            cart = get_or_create_cart(request)
            cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
            
            # RESTORE STOCK before deleting
            product = cart_item.product
            product.stock += cart_item.quantity
            product.save()
            
            logger.info(f"Stock restored. New stock for {product.name}: {product.stock}")
            
            cart_item.delete()
            
            cart_count = cart.get_total_items()
            
            return JsonResponse({
                'success': True,
                'cart_count': cart_count,
                'message': 'Item removed from cart! Stock restored.'
            })
            
        except CartItem.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Item not found in cart'})
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

# UPDATED: Cart page with better session handling
def cart_page(request):
    # Force session creation
    if not request.session.session_key:
        request.session.save()
    
    cart = get_or_create_cart(request)
    cart_items = cart.items.all()
    cart_count = cart.get_total_items()
    total_price = cart.get_total_price()
    
    whatsapp_message = generate_whatsapp_message(cart_items, total_price, request)
    
    context = {
        'cart_items': cart_items,
        'cart_count': cart_count,
        'total_price': total_price,
        'whatsapp_message': whatsapp_message,
    }
    
    return render(request, 'cart.html', context)

def generate_whatsapp_message(cart_items, total_price, request=None):
    if not cart_items:
        return "Your cart is empty."
    
    # Get base URL for images
    base_url = ""
    if request:
        base_url = request.build_absolute_uri('/').rstrip('/')
    
    # If request is None, use your deployed URL
    if not base_url:
        base_url = "https://wristhaus-website.onrender.com"
    
    # START with image URLs (WhatsApp will show previews at top)
    message = ""
    
    # Add ALL image URLs at the VERY TOP for WhatsApp previews
    for item in cart_items:
        product = item.product
        if product.image:
            # Build the full image URL
            if product.image.url.startswith('http'):
                image_url = product.image.url
            else:
                image_url = base_url + product.image.url
            
            message += f"{image_url}\n"  # Just the URL, no emoji
    
    # Add spacing after images
    message += "\n" * 2
    
    # Now add the order details
    message += "🛍️ *WRISTHAUS - NEW ORDER* 🛍️\n"
    message += "═" * 35 + "\n\n"
    
    for i, item in enumerate(cart_items, 1):
        product = item.product
        subtotal = item.get_total_price()
        
        message += f"*Item {i}: {product.name}*\n"
        message += f"💰 Price: ₦{product.price}\n"
        message += f"📦 Quantity: {item.quantity}\n"
        message += f"💵 Subtotal: ₦{subtotal}\n\n"
    
    message += "═" * 35 + "\n"
    message += f"💰 *TOTAL: ₦{total_price}*\n"
    message += "═" * 35 + "\n\n"
    
    message += "📋 *Order Summary:*\n"
    for item in cart_items:
        message += f"  • {item.product.name} x{item.quantity} = ₦{item.get_total_price()}\n"
    
    message += f"\n📍 *Total: ₦{total_price}*\n\n"
    message += "✅ *Please reply with your delivery address.*\n"
    message += "📞 *We'll confirm your order immediately.*\n"
    message += "🛡️ *Secure payment on delivery.*\n\n"
    message += "_Thank you for shopping at Wristhaus!_ 🙏"
    
    return message

# UPDATED: Checkout with stock validation
def checkout_to_whatsapp(request):
    cart = get_or_create_cart(request)
    cart_items = cart.items.all()
    total_price = cart.get_total_price()
    
    if not cart_items:
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart_page')
    
    # Check if all items are still in stock
    with transaction.atomic():
        for item in cart_items:
            if item.product.stock < item.quantity:
                messages.error(
                    request, 
                    f'Sorry, "{item.product.name}" is out of stock. Only {item.product.stock} available.'
                )
                return redirect('cart_page')
            

    
    message = generate_whatsapp_message(cart_items, total_price, request)
        # Encode message for URL
    encoded_message = urllib.parse.quote(message)
    
    phone_number = "2347030816894"  # CHANGE THIS TO YOUR NUMBER
        # Build WhatsApp URL
    whatsapp_url = f"https://wa.me/{phone_number}?text={encoded_message}"
    

    return redirect(whatsapp_url)

# NEW: Update cart item quantity (for cart page)
def update_cart_quantity(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            action = data.get('action')  # 'increase' or 'decrease'
            
            cart = get_or_create_cart(request)
            cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
            
            if action == 'increase':
                # Check if stock is available
                if cart_item.product.stock < 1:
                    return JsonResponse({
                        'success': False,
                        'error': 'Not enough stock available.'
                    })
                cart_item.quantity += 1
                cart_item.product.stock -= 1
                cart_item.product.save()
                
            elif action == 'decrease':
                if cart_item.quantity > 1:
                    cart_item.quantity -= 1
                    cart_item.product.stock += 1
                    cart_item.product.save()
                else:
                    return JsonResponse({
                        'success': False,
                        'error': 'Minimum quantity is 1'
                    })
            
            cart_item.save()
            
            return JsonResponse({
                'success': True,
                'quantity': cart_item.quantity,
                'subtotal': float(cart_item.get_total_price()),
                'total': float(cart.get_total_price()),
                'cart_count': cart.get_total_items(),
                'remaining_stock': cart_item.product.stock
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})


# NEW: Product detail view
def product_detail(request, product_id):
    """Display single product details"""
    product = get_object_or_404(Shop_All, id=product_id)
    cart = get_or_create_cart(request)
    cart_count = cart.get_total_items()
    
    # Get related products (same category, exclude current)
    related_products = Shop_All.objects.filter(
        category=product.category
    ).exclude(id=product.id).order_by('-created_at')[:4]  # Show 4 related products
    
    context = {
        'product': product,
        'cart_count': cart_count,
        'related_products': related_products,
    }
    
    return render(request, 'product_detail.html', context)


# NEW: Collection page view
def collections(request):
    """Display all products organized by category"""
    search_query = request.GET.get('search', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    
    
        
            # Apply search filter
    if search_query:
        shop_alls = shop_alls.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(category__icontains=search_query)
        )
    

    
   
    cart = get_or_create_cart(request)
    cart_count = cart.get_total_items()

    
    # Get all categories with their products
    categories = []
    for category_code, category_name in Shop_All.CATEGORY_CHOICES:
        products = Shop_All.objects.filter(category=category_code).order_by('-created_at')
        min_product_price = products.aggregate(models.Min('price'))['price__min'] or 0
        max_product_price = products.aggregate(models.Max('price'))['price__max'] or 100000
        if products.exists():  # Only show categories that have products
            categories.append({
                'code': category_code,
                'name': category_name,
                'products': products,
                'count': products.count()
            })
    
    context = {
        'categories': categories,
        'cart_count': cart_count,
        'search_query': search_query,
        'min_price': min_price or min_product_price,
        'max_price': max_price or max_product_price,
}

    
    
    return render(request, 'collections.html', context)

def about(request):
        
    cart = get_or_create_cart(request)
    cart_count = cart.get_total_items()
    
    context = {
       'cart_count': cart_count
    }
    return render(request, 'about_us.html', context)

def contact(request):
    cart = get_or_create_cart(request)
    cart_count = cart.get_total_items()

    context = {
       'cart_count': cart_count
    }
    return render(request, 'contact.html', context)





# ... (keep your existing views)

# ============ ADMIN VIEWS ============

@login_required
def admin_dashboard(request):
    """Main admin dashboard"""
    # Check if user is admin
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access the admin panel.')
        return redirect('index')
    
    # Get statistics
    total_products = Shop_All.objects.count()
    total_orders = Cart.objects.count()
    total_items_sold = CartItem.objects.count()
    low_stock = Shop_All.objects.filter(stock__lt=5).count()
    
    # Recent products
    recent_products = Shop_All.objects.all().order_by('-created_at')[:5]
    
    context = {
        'total_products': total_products,
        'total_orders': total_orders,
        'total_items_sold': total_items_sold,
        'low_stock': low_stock,
        'recent_products': recent_products,
    }
    return render(request, 'admin/dashboard.html', context)

@login_required
def admin_products(request):
    """List all products with pagination"""
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access the admin panel.')
        return redirect('index')
    
    products = Shop_All.objects.all().order_by('-created_at')
    
    # Pagination
    paginator = Paginator(products, 10)
    page = request.GET.get('page')
    
    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        products_page = paginator.page(1)
    except EmptyPage:
        products_page = paginator.page(paginator.num_pages)
    
    return render(request, 'admin/products.html', {
        'products': products_page,
        'total_products': products.count(),
    })
 
@login_required
def admin_product_add(request):
    """Add new product"""
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access the admin panel.')
        return redirect('index')
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Product "{product.name}" added successfully!')
            return redirect('admin_products')
    else:
        form = ProductForm()
    
    return render(request, 'admin/product_form.html', {
        'form': form,
        'title': 'Add New Product',
        'button_text': 'Add Product',
    })

@login_required
def admin_product_edit(request, product_id):
    """Edit existing product"""
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access the admin panel.')
        return redirect('index')
    
    product = get_object_or_404(Shop_All, id=product_id)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'Product "{product.name}" updated successfully!')
            return redirect('admin_products')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'admin/product_form.html', {
        'form': form,
        'product': product,
        'title': f'Edit Product: {product.name}',
        'button_text': 'Update Product',
    })

@login_required
def admin_product_delete(request, product_id):
    """Delete product"""
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access the admin panel.')
        return redirect('index')
    
    product = get_object_or_404(Shop_All, id=product_id)
    
    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'Product "{product_name}" deleted successfully!')
        return redirect('admin_products')
    
    return render(request, 'admin/product_confirm_delete.html', {
        'product': product,
    })

@login_required
def admin_orders(request):
    """View all orders"""
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access the admin panel.')
        return redirect('index')
    
    # Get all carts with items
    carts = Cart.objects.filter(items__isnull=False).distinct().order_by('-created_at')
    
    # Pagination
    paginator = Paginator(carts, 10)
    page = request.GET.get('page')
    
    try:
        carts_page = paginator.page(page)
    except PageNotAnInteger:
        carts_page = paginator.page(1)
    except EmptyPage:
        carts_page = paginator.page(paginator.num_pages)
    
    # Prepare order data
    orders = []
    for cart in carts_page:
        items = cart.items.all()
        total = cart.get_total_price()
        orders.append({
            'cart': cart,
            'items': items,
            'total': total,
            'item_count': items.count(),
        })
    
    return render(request, 'admin/orders.html', {
        'orders': orders,
        'carts': carts_page,
    })

@login_required
def admin_order_detail(request, cart_id):
    """View order details"""
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access the admin panel.')
        return redirect('index')
    
    cart = get_object_or_404(Cart, id=cart_id)
    items = cart.items.all()
    total = cart.get_total_price()
    
    return render(request, 'admin/order_detail.html', {
        'cart': cart,
        'items': items,
        'total': total,
    })

@login_required
def admin_order_delete(request, cart_id):
    """Delete an order"""
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access the admin panel.')
        return redirect('index')
    
    cart = get_object_or_404(Cart, id=cart_id)
    
    if request.method == 'POST':
        cart.delete()
        messages.success(request, 'Order deleted successfully!')
        return redirect('admin_orders')
    
    return render(request, 'admin/order_confirm_delete.html', {
        'cart': cart,
    })

@login_required
def admin_review(request):
    """List all reviews with pagination"""
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access the admin panel.')
        return redirect('index')
    
    reviews = ClientReview.objects.all().order_by('-created_at')
    
    # Pagination
    paginator = Paginator(reviews, 10)
    page = request.GET.get('page')
    
    try:
        reviews_pages = paginator.page(page)
    except PageNotAnInteger:
        reviews_pages = paginator.page(1)
    except EmptyPage:
        reviews_pages = paginator.page(paginator.num_pages)
    
    return render(request, 'admin/reviews.html', {
        'reviews': reviews_pages,
        'total_reviews': reviews.count(),
    })
    


@login_required
def admin_review_add(request):
    """Add new review"""
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access the admin panel.')
        return redirect('index')
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save()
            messages.success(request, f'Review from "{review.name}" added successfully!')
            return redirect('admin_review')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ReviewForm()
    
    return render(request, 'admin/review_form.html', {
        'form': form,
        'title': 'Add New Review',
        'button_text': 'Add Review',
    })
    
    
@login_required
def admin_review_edit(request, review_id):
    """Edit existing review"""
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access the admin panel.')
        return redirect('index')
    
    reviews = get_object_or_404(ClientReview, id=review_id)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES, instance=reviews)
        if form.is_valid():
            form.save()
            messages.success(request, f'Review from "{reviews.name}" updated successfully!')
            return redirect('admin_review')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ReviewForm(instance=reviews)
    
    return render(request, 'admin/review_form.html', {
        'form': form,
        'reviews': reviews,
        'title': f'Edit Review: {reviews.name}',
        'button_text': 'Update Review',
    })


@login_required
def admin_review_delete(request, review_id):
    """Delete review"""
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access the admin panel.')
        return redirect('index')
    
    reviews = get_object_or_404(ClientReview, id=review_id)
    
    if request.method == 'POST':
        review_name = reviews.name
        reviews.delete()
        messages.success(request, f'Review from "{review_name}" deleted successfully!')
        return redirect('admin_review')
    
    return render(request, 'admin/review_confirm_delete.html', {'reviews': reviews})

@login_required
def admin_review_approve(request, review_id):
    """Approve or disapprove review"""
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access the admin panel.')
        return redirect('index')
    
    reviews = get_object_or_404(ClientReview, id=review_id)
    reviews.is_approved = not reviews.is_approved
    reviews.save()
    
    status = "approved" if reviews.is_approved else "disapproved"
    messages.success(request, f'Review from "{reviews.name}" {status}!')
    return redirect('admin_review')


@login_required
def admin_logout(request):
    """Admin logout - clears session and redirects to admin login"""
    if request.user.is_superuser:
        logout(request)
        messages.success(request, 'You have been logged out of the admin panel.')
        return redirect('admin_login')
    else:
        messages.error(request, 'You do not have permission to access the admin panel.')
        return redirect('index')


def admin_login(request):
    """Admin login page - only for superusers"""
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'You do not have admin privileges.')
            return redirect('index')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_superuser:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('admin_dashboard')
            else:
                messages.error(request, 'You do not have admin privileges.')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'admin/login.html')



@login_required
def admin_profile(request):
    """Admin profile management"""
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access the admin panel.')
        return redirect('index')
    
    if request.method == 'POST':
        form = AdminProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully! ✅')
            return redirect('admin_profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AdminProfileForm(instance=request.user)
    
    context = {
        'form': form,
        'user': request.user,
    }
    return render(request, 'admin/profile.html', context)

@login_required
def admin_change_password(request):
    """Admin password change"""
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access the admin panel.')
        return redirect('index')
    
    if request.method == 'POST':
        form = AdminPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Update session to prevent logout
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password has been changed successfully! 🔒')
            return redirect('admin_profile')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = AdminPasswordChangeForm(request.user)
    
    return render(request, 'admin/change_password.html', {'form': form})