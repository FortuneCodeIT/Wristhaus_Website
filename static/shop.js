$(document).ready(function() {
    // Add to Cart
    $('.add-to-cart, .buy-now').click(function(e) {
        e.preventDefault();
        const productId = $(this).data('product-id');
        const isBuyNow = $(this).hasClass('buy-now');
        
        $.ajax({
            url: "{% url 'add_to_cart' %}",
            method: 'POST',
            data: JSON.stringify({
                product_id: productId,
                quantity: 1
            }),
            headers: {
                'X-CSRFToken': '{{ csrf_token }}'
            },
            contentType: 'application/json',
            success: function(response) {
                if (response.success) {
                    updateCartCount(response.cart_count);
                    // alert(response.message);
                    
                    if (isBuyNow) {
                        window.location.href = "{% url 'cart_page' %}";
                    }
                } else {
                    alert('Error: ' + response.error);
                }
            },
            error: function(xhr) {
                alert('An error occurred. Please try again.');
            }
        });
    });
    
});