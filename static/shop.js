// $(document).ready(function() {
//     // Add to Cart
//     $('.add-to-cart, .buy-now').click(function(e) {
//         e.preventDefault();
//         const productId = $(this).data('product-id');
//         const isBuyNow = $(this).hasClass('buy-now');
        
//         $.ajax({
//             url: "{% url 'add_to_cart' %}",
//             method: 'POST',
//             data: JSON.stringify({
//                 product_id: productId,
//                 quantity: 1
//             }),
//             headers: {
//                 'X-CSRFToken': '{{ csrf_token }}'
//             },
//             contentType: 'application/json',
//             success: function(response) {
//                 if (response.success) {
//                     updateCartCount(response.cart_count);
//                     alert(response.message);
                    
//                     if (isBuyNow) {
//                         window.location.href = "{% url 'cart_page' %}";
//                     }
//                 } else {
//                     alert('Error: ' + response.error);
//                 }
//             },
//             error: function(xhr) {
//                 alert('An error occurred. Please try again.');
//             }
//         });
//     });
    
// });

// ===========================================================
// CUSTOM POPUP FUNCTIONS
// ===========================================================

function showPopup(type, title, message, buttonText, buttonAction) {
    // Create overlay
    const overlay = $('<div>', {
        class: 'custom-popup-overlay',
        id: 'customPopupOverlay'
    });
    
    // Determine icon and colors
    let iconHtml = '';
    let btnClass = '';
    
    if (type === 'success') {
        iconHtml = '<i class="fas fa-check-circle"></i>';
        btnClass = 'success-btn';
    } else if (type === 'error') {
        iconHtml = '<i class="fas fa-exclamation-circle"></i>';
        btnClass = 'error-btn';
    } else if (type === 'warning') {
        iconHtml = '<i class="fas fa-exclamation-triangle"></i>';
        btnClass = '';
    } else {
        iconHtml = '<i class="fas fa-info-circle"></i>';
        btnClass = '';
    }
    
    // Create popup
    const popup = $('<div>', {
        class: 'custom-popup',
        id: 'customPopup'
    });
    
    popup.html(`
        <button class="popup-close" id="popupCloseBtn">
            <i class="fas fa-times"></i>
        </button>
        <div class="popup-icon ${type}">
            ${iconHtml}
        </div>
        <h3 class="popup-title">${title}</h3>
        <p class="popup-message">${message}</p>
        <button class="popup-btn ${btnClass}" id="popupActionBtn">
            ${buttonText || 'OK'}
        </button>
    `);
    
    overlay.append(popup);
    $('body').append(overlay);
    
    // Close button handler
    $('#popupCloseBtn').click(function() {
        closePopup();
    });
    
    // Action button handler
    $('#popupActionBtn').click(function() {
        if (buttonAction && typeof buttonAction === 'function') {
            buttonAction();
        }
        closePopup();
    });
    
    // Close on outside click
    overlay.click(function(e) {
        if (e.target === this) {
            closePopup();
        }
    });
    
    // Auto close after 5 seconds for success messages
    if (type === 'success') {
        setTimeout(function() {
            closePopup();
        }, 5000);
    }
}

function closePopup() {
    const overlay = $('#customPopupOverlay');
    if (overlay.length) {
        overlay.fadeOut(300, function() {
            $(this).remove();
        });
    }
}

// ===========================================================
// TOAST NOTIFICATION (Alternative - Less intrusive)
// ===========================================================

function showToast(type, message, duration) {
    duration = duration || 3000;
    
    const toast = $('<div>', {
        class: 'toast-notification',
        id: 'toastNotification'
    });
    
    let icon = '';
    if (type === 'success') {
        icon = '<i class="fas fa-check-circle toast-icon success"></i>';
    } else if (type === 'error') {
        icon = '<i class="fas fa-exclamation-circle toast-icon error"></i>';
    } else {
        icon = '<i class="fas fa-info-circle toast-icon"></i>';
    }
    
    toast.html(`
        ${icon}
        <span class="toast-message">${message}</span>
    `);
    
    $('body').append(toast);
    
    // Auto remove after duration
    setTimeout(function() {
        toast.css('animation', 'slideOutRight 0.5s ease');
        setTimeout(function() {
            toast.remove();
        }, 500);
    }, duration);
}