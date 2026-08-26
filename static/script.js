    //  this is for preloader
       document.addEventListener('DOMContentLoaded', () => {

            const preloader = document.getElementById('preloader');
            if (preloader) {
                preloader.style.display = 'none';
            }
        });

         setTimeout(function() {
            const preloader = document.getElementById('preloader');
                if (preloader) {
                    preloader.style.display = 'none';
                }
         },50000);

// Luna & Co — shared behaviors
document.addEventListener('DOMContentLoaded', () => {

const mobileNav = document.getElementById('mobile-nav');
const desktopNav = document.getElementById('desktop-nav');
const openNav = document.getElementById('openNav');

openNav.addEventListener('click', () => {
    openNav.classList.toggle('open');

    if (openNav.classList.contains('open')) {
        mobileNav.style.display = 'flex';
        mobileNav.style.transform = 'translateX(0)';
        desktopNav.style.display= 'none';
    }
    else {
        mobileNav.style.transform = 'translateX(-100%)';
        mobileNav.style.display = 'none';
    }
});


  // Mobile nav toggle
  const toggle = document.querySelector('.nav-toggle');
  const nav = document.querySelector('nav.main');
  if (toggle && nav) {
    toggle.addEventListener('click', () => {
      const open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      nav.style.display = open ? 'flex' : '';
      if (open) {
        nav.style.position = 'absolute';
        nav.style.top = '100%';
        nav.style.left = '0';
        nav.style.right = '0';
        nav.style.flexDirection = 'column';
        nav.style.background = '#0D0C0A';
        nav.style.padding = '18px 32px';
        nav.style.gap = '16px';
        nav.style.borderTop = '1px solid rgba(246,241,230,.12)';
      }
    });
  }

  // Contact form
  const form = document.querySelector('.contact-form');
  if (form) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const msg = document.querySelector('.form-msg');
      if (msg) {
        msg.textContent = "Thank you — your message has been received. We'll reply within one business day.";
        msg.classList.add('show');
      }
      form.reset();
    });
  }

//   // Newsletter form(s)
//   document.querySelectorAll('.footer-newsletter-form').forEach(nform => {
//     nform.addEventListener('submit', (e) => {
//       e.preventDefault();
//       const btn = nform.querySelector('button');
//       const original = btn.textContent;
//       btn.textContent = 'Subscribed ✓';
//       setTimeout(() => { btn.textContent = original; nform.reset(); }, 2200);
//     });
//   });

  // Buy now buttons — simple cart-count demo
//   const cartCount = document.querySelector('.cart-count');
//   document.querySelectorAll('.btn-buy').forEach(btn => {
//     btn.addEventListener('click', () => {
//       if (cartCount) {
//         cartCount.textContent = (parseInt(cartCount.textContent || '0', 10) + 1).toString();
//       }
//       const original = btn.textContent;
//       btn.textContent = 'Added ✓';
//       setTimeout(() => { btn.textContent = original; }, 1400);
//     });
//   });

  // FAQ accordion
  document.querySelectorAll('.faq-item').forEach(item => {
    const q = item.querySelector('.faq-q');
    const a = item.querySelector('.faq-a');
    if (!q || !a) return;
    a.style.display = 'none';
    q.style.cursor = 'pointer';
    q.addEventListener('click', () => {
      const isOpen = a.style.display === 'block';
      a.style.display = isOpen ? 'none' : 'block';
    });
  });

function updateCartCount(count) {
    $('.cart-count').text(count);
}



//   const track = document.querySelector('.slideshow-track');
// const slides = document.querySelectorAll('.slide');
// const totalSlides = slides.length;

// // Clone ALL slides and append them (duplicate entire set)
// slides.forEach(slide => {
//   const clone = slide.cloneNode(true);
//   track.appendChild(clone);
// });

// // Clone ALL slides and prepend them (duplicate entire set)
// slides.forEach(slide => {
//   const clone = slide.cloneNode(true);
//   track.insertBefore(clone, track.firstChild);
// });

// // Now we have: [clone1, clone2, clone3, clone4, original1, original2, original3, original4, clone1, clone2, clone3, clone4]
// // We start at the first original slide (index = totalSlides)
// const allSlides = track.querySelectorAll('.slide');
// const totalAllSlides = allSlides.length;
// let currentIndex = totalSlides; // Start at first original slide
// let isTransitioning = false;

// function slideTo(index, instant = false) {
//   if (isTransitioning && !instant) return;
 
//   if (instant) {
//     track.style.transition = 'none';
//   } else {
//     track.style.transition = 'transform 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
//   }
 
//   track.style.transform = `translateX(-${index * 100}%)`;
//   currentIndex = index;
 
//   if (!instant) {
//     isTransitioning = true;
//     setTimeout(() => {
//       isTransitioning = false;
//       checkAndReset();
//     }, 850);
//   }
// }

// function checkAndReset() {
//   // If we reached the cloned slides at the end, jump back to the original equivalents
//   if (currentIndex >= totalSlides * 2) {
//     const newIndex = currentIndex - totalSlides;
//     slideTo(newIndex, true);
//   }
 
//   // If we reached the cloned slides at the beginning, jump forward to the original equivalents
//   if (currentIndex < totalSlides) {
//     const newIndex = currentIndex + totalSlides;
//     slideTo(newIndex, true);
//   }
// }

// function nextSlide() {
//   slideTo(currentIndex + 1);
// }

// // Initialize - start at first original slide
// slideTo(totalSlides, true);

// // Auto-slide every 4 seconds
// let autoSlide = setInterval(nextSlide, 4000);

// // Pause on hover
// const hero = document.querySelector('.hero');
// hero.addEventListener('mouseenter', () => clearInterval(autoSlide));
// hero.addEventListener('mouseleave', () => {
//   autoSlide = setInterval(nextSlide, 4000);
// });

// // Fix for when user leaves tab and comes back
// document.addEventListener('visibilitychange', () => {
//   if (document.hidden) {
//     clearInterval(autoSlide);
//   } else {
//     autoSlide = setInterval(nextSlide, 4000);
//   }
// });


  const track = document.querySelector('.slideshow-track');
const slides = document.querySelectorAll('.slide');
const totalSlides = slides.length;


slides.forEach(slide => {
  const clone = slide.cloneNode(true);
  track.appendChild(clone);
});

slides.forEach(slide => {
  const clone = slide.cloneNode(true);
  track.insertBefore(clone, track.firstChild);
});

// const track = document.querySelector('.slideshow-track');
// const slides = document.querySelectorAll('.slide');
// let currentIndex = 0;
// const totalSlides = slides.length;
// let isTransitioning = false;

const allSlides = track.querySelectorAll('.slide');
const totalAllSlides = allSlides.length;
let currentIndex = totalSlides; // Start at first original slide
let isTransitioning = false;



function slideTo(index, instant =  false) {
if (isTransitioning && !instant) return;

  if (instant) {
    track.style.transition = 'none';
  } else {
    track.style.transition = 'transform 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
  }

  track.style.transform = `translateX(-${index * 100}%)`;
  currentIndex = index;

    if (!instant) {
    isTransitioning = true;
    setTimeout(() => {
      isTransitioning = false;
      checkAndReset();
    }, 850);
  }
}

function checkAndReset() {
  // If we reached the cloned slides at the end, jump back to the original equivalents
  if (currentIndex >= totalSlides * 2) {
    const newIndex = currentIndex - totalSlides;
    slideTo(newIndex, true);
  }
 
  // If we reached the cloned slides at the beginning, jump forward to the original equivalents
  if (currentIndex < totalSlides) {
    const newIndex = currentIndex + totalSlides;
    slideTo(newIndex, true);
  }
}

function nextSlide() {
  const nextIndex = (currentIndex + 1);
  slideTo(nextIndex);
}
slideTo(totalSlides, true);

// Auto-slide every 4 seconds
let autoSlide = setInterval(nextSlide, 4000);

// Pause on hover
// const hero = document.querySelector('.hero');
// hero.addEventListener('mouseenter', () => clearInterval(autoSlide));
// hero.addEventListener('mouseleave', () => {
//   autoSlide = setInterval(nextSlide, 4000);
// });


         AOS.init ({
          duration: 800,
            easing: 'ease-in-out',
            once: false,
            offset: 100,
            delay: 0,
    });


 document.addEventListener('DOMContentLoaded', function() {
            AOS.refresh();
        });

     // Also refresh after all images load
        window.addEventListener('load', function() {
            AOS.refresh();
        });





});
