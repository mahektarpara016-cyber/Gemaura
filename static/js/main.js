// ========================================
// GEMAURA - Main JavaScript
// ========================================

// Auto-dismiss flash messages & Loader
document.addEventListener('DOMContentLoaded', function () {
    // Hide Luxury Loader
    const loader = document.getElementById('luxury-loader');
    if (loader) {
        window.addEventListener('load', () => {
            setTimeout(() => {
                loader.style.opacity = '0';
                loader.style.visibility = 'hidden';
            }, 800);
        });
    }

    setTimeout(() => {
        document.querySelectorAll('.alert').forEach(a => {
            a.style.opacity = '0';
            a.style.transform = 'translateX(40px)';
            a.style.transition = 'all 0.4s ease';
            setTimeout(() => a.remove(), 400);
        });
    }, 4000);

    // Close btn
    document.querySelectorAll('.close-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const alert = btn.closest('.alert');
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        });
    });

    // ========================================
    // PROFILE DROPDOWN TOGGLE
    // ========================================
    const profileTrigger = document.querySelector('.profile-avatar-trigger');
    const dropdownMenu = document.querySelector('.user-dropdown-menu');
    const dropdownWrapper = document.querySelector('.profile-dropdown-wrapper');

    if (profileTrigger && dropdownMenu) {
        // Toggle dropdown on click
        profileTrigger.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();
            const isOpen = dropdownMenu.classList.contains('active');
            closeAllDropdowns();
            if (!isOpen) {
                dropdownMenu.classList.add('active');
                profileTrigger.classList.add('active');
            }
        });

        // Close when clicking outside
        document.addEventListener('click', function (e) {
            if (dropdownWrapper && !dropdownWrapper.contains(e.target)) {
                closeAllDropdowns();
            }
        });

        // Escape key closes dropdown
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') closeAllDropdowns();
        });
    }

    function closeAllDropdowns() {
        const dd = document.querySelector('.user-dropdown-menu');
        const trigger = document.querySelector('.profile-avatar-trigger');
        if (dd) dd.classList.remove('active');
        if (trigger) trigger.classList.remove('active');
    }

    // Hamburger / Mobile Menu
    const hamburger = document.getElementById('mobile-menu-btn');
    const navMenu = document.querySelector('.nav-links'); // Updated selector
    if (hamburger && navMenu) {
        hamburger.addEventListener('click', function(e) {
            e.stopPropagation();
            navMenu.classList.toggle('active'); // Use active instead of open for consistency
            this.classList.toggle('active');
        });
    }

    // Wishlist AJAX toggle - Global
    window.toggleWishlist = function(btn, productId) {
        fetch(`/wishlist/toggle/${productId}`, {
            method: 'POST',
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        }).then(r => r.json()).then(data => {
            const icon = btn.querySelector('i');
            if (data.in_wishlist) {
                btn.classList.add('active');
                icon.className = 'fas fa-heart';
                showNotification('Added to Wishlist!', 'success');
            } else {
                btn.classList.remove('active');
                icon.className = 'far fa-heart';
                showNotification('Removed from Wishlist', 'info');
            }
            updateNavCounts();
        }).catch(() => {
            window.location.href = '/login';
        });
    };

    // Product zoom on detail page
    const mainImg = document.querySelector('.main-image img');
    const mainWrap = document.querySelector('.main-image');
    if (mainImg && mainWrap) {
        mainWrap.addEventListener('mousemove', function (e) {
            const rect = this.getBoundingClientRect();
            const x = ((e.clientX - rect.left) / rect.width) * 100;
            const y = ((e.clientY - rect.top) / rect.height) * 100;
            mainImg.style.transformOrigin = `${x}% ${y}%`;
        });
    }

    // Rating star interaction
    const ratingInputs = document.querySelectorAll('.star-rating input');
    ratingInputs.forEach(input => {
        input.addEventListener('change', function () {
            document.querySelectorAll('.star-rating label').forEach((lbl, idx) => {
                lbl.style.color = idx < this.value ? '#C9A84C' : '#ccc';
            });
        });
    });

    // Global Fixed Navbar Scroll Effect
    const header = document.querySelector('.main-header');
    if (header) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 10) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
        });
    }
});

// ========================================
// LUXURY SENSORY & ANIMATION
// ========================================
document.addEventListener('DOMContentLoaded', function() {
    // 1. Hero Audio Toggle
    const heroVid = document.getElementById('hero-vid');
    const audioBtn = document.getElementById('hero-audio-toggle');
    if (heroVid && audioBtn) {
        audioBtn.addEventListener('click', function() {
            const icon = this.querySelector('i');
            if (heroVid.muted) {
                heroVid.muted = false;
                icon.className = 'fas fa-volume-up';
                showNotification('Audio Unmuted - Experience Gemaura', 'success');
            } else {
                heroVid.muted = true;
                icon.className = 'fas fa-volume-mute';
                showNotification('Audio Muted', 'info');
            }
        });
    }

    // 2. Reveal on Scroll (Intersection Observer)
    const revealElements = document.querySelectorAll('.reveal-on-scroll');
    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');
            }
        });
    }, { threshold: 0.15 });

    revealElements.forEach(el => revealObserver.observe(el));

    // 3. Global Event Delegation for Dynamic Elements
    document.addEventListener('click', function(e) {
        const isGuest = document.body.dataset.loggedIn === 'false';
        
        // Helper to show auth modal
        const showAuthModal = () => {
            const modal = document.getElementById('auth-modal');
            if (modal) modal.style.display = 'block';
        };

        // Product Interaction - Redirect on click handled by HTML links

        // Add to Cart
        const cartBtn = e.target.closest('.add-to-cart-simple, .cart-btn-ajax');
        if (cartBtn) {
            if (isGuest) {
                showAuthModal();
                return;
            }
            if (typeof addToCartAjax === 'function') {
                addToCartAjax(cartBtn.dataset.productId);
            }
        }

        // Reel Likes
        const likeBtn = e.target.closest('.like-btn');
        if (likeBtn && likeBtn.dataset.reelId) {
            if (isGuest) {
                showAuthModal();
                return;
            }
            if (typeof likeReel === 'function') {
                likeReel(likeBtn.dataset.reelId, likeBtn);
            }
        }

        // Reel Comments
        const commentBtn = e.target.closest('.comment-trigger');
        if (commentBtn && commentBtn.dataset.reelId) {
            if (isGuest) {
                showAuthModal();
                return;
            }
            if (typeof openComments === 'function') {
                openComments(commentBtn.dataset.reelId);
            }
        }

        // Reel Share
        const shareBtn = e.target.closest('.share-trigger');
        if (shareBtn && shareBtn.dataset.reelId) {
            if (isGuest) {
                showAuthModal();
                return;
            }
            if (typeof shareReel === 'function') {
                shareReel(shareBtn.dataset.reelId);
            }
        }

        // Wishlist Toggle
        const wishlistBtn = e.target.closest('.wishlist-toggle-btn');
        if (wishlistBtn && wishlistBtn.dataset.productId) {
            if (isGuest) {
                window.location.href = '/login';
                return;
            }
            if (typeof toggleWishlist === 'function') {
                toggleWishlist(wishlistBtn, wishlistBtn.dataset.productId);
            }
        }

        // Data-Href Links (Reels items)
        const hrefItem = e.target.closest('[data-href]');
        if (hrefItem && !e.target.closest('.reel-action-btn')) {
            window.location.href = hrefItem.dataset.href;
        }

        // Mute Toggle
        const muteBtn = e.target.closest('.mute-trigger');
        if (muteBtn && typeof toggleMute === 'function') {
            toggleMute(muteBtn);
        }
    });

    // Close Modals
    document.querySelectorAll('.close-modal').forEach(btn => {
        btn.onclick = function() {
            const modal = btn.closest('.modal');
            if (modal) modal.style.display = 'none';
        }
    });
    
    // Window click to close modal
    window.onclick = function(event) {
        if (event.target.classList.contains('modal')) {
            event.target.style.display = 'none';
        }
    }
});

// Cart quantity controls
function changeQty(inputId, delta) {
    const input = document.getElementById(inputId);
    if (input) {
        let val = parseInt(input.value) + delta;
        if (val < 1) val = 1;
        input.value = val;
    }
}

// Show toast notification
function showNotification(message, type = 'success') {
    const container = document.querySelector('.flash-container');
    if (!container) return;
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    const icon = type === 'success' ? '✅' : (type === 'warning' ? '⚠️' : (type === 'danger' ? '❌' : 'ℹ️'));
    
    alert.innerHTML = `
        <span>${icon}</span>
        <span>${message}</span>
        <span class="close-btn" onclick="this.parentElement.remove()">×</span>
    `;
    
    container.appendChild(alert);
    
    // Auto-dismiss
    setTimeout(() => {
        alert.style.opacity = '0';
        alert.style.transform = 'translateX(40px)';
        alert.style.transition = 'all 0.4s ease';
        setTimeout(() => alert.remove(), 400);
    }, 4000);
}

// Buy Now Functionality
window.buyNow = function(productId) {
    const qty = document.getElementById('qty') ? document.getElementById('qty').value : 1;
    const isGuest = document.body.dataset.loggedIn === 'false';
    
    if (isGuest) {
        window.location.href = '/login?msg=Please login to checkout';
        return;
    }

    const formData = new FormData();
    formData.append('quantity', qty);

    fetch(`/cart/add/${productId}`, {
        method: 'POST',
        body: formData,
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(r => r.json())
    .then(data => {
        if (data.status === 'success') {
            window.location.href = '/checkout';
        } else if (data.redirect) {
            window.location.href = data.redirect;
        } else {
            showNotification(data.message, 'danger');
        }
    })
    .catch(() => {
        showNotification('Failed to process checkout.', 'danger');
    });
}

// Add to Cart AJAX
function addToCartAjax(productId) {
    const isGuest = document.body.dataset.loggedIn === 'false';
    if (isGuest) {
        const modal = document.getElementById('auth-modal');
        if (modal) modal.style.display = 'block';
        return;
    }

    const formData = new FormData();
    formData.append('quantity', 1);

    fetch(`/cart/add/${productId}`, {
        method: 'POST',
        body: formData,
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(r => r.json())
    .then(data => {
        if (data.status === 'success') {
            showNotification(data.message, 'success');
            updateNavCounts();
        } else if (data.redirect) {
            window.location.href = data.redirect;
        } else {
            showNotification(data.message, 'danger');
        }
    })
    .catch(() => {
        showNotification('Failed to add to cart.', 'danger');
    });
}

// Update Navigation Counts
function updateNavCounts() {
    fetch('/api/counts')
        .then(r => r.json())
        .then(data => {
            const wishlistBadge = document.querySelector('.wishlist-toggle-btn .badge');
            const cartBadge = document.querySelector('.cart-btn-ajax .badge');

            if (data.wishlist > 0) {
                if (wishlistBadge) wishlistBadge.innerText = data.wishlist;
                else {
                    const wrap = document.querySelector('.wishlist-toggle-btn .icon-wrap');
                    if (wrap) wrap.insertAdjacentHTML('beforeend', `<span class="badge">${data.wishlist}</span>`);
                }
            } else if (wishlistBadge) wishlistBadge.remove();

            if (data.cart > 0) {
                if (cartBadge) cartBadge.innerText = data.cart;
                else {
                    const wrap = document.querySelector('.cart-btn-ajax .icon-wrap');
                    if (wrap) wrap.insertAdjacentHTML('beforeend', `<span class="badge">${data.cart}</span>`);
                }
            } else if (cartBadge) cartBadge.remove();
        });
}

// ========================================
// HERO SLIDER LOGIC
// ========================================
document.addEventListener('DOMContentLoaded', function() {
    const slides = document.querySelectorAll('.hero-slider .slide');
    const dotsContainer = document.getElementById('slider-dots');
    const prevBtn = document.querySelector('.prev-btn');
    const nextBtn = document.querySelector('.next-btn');
    
    if (slides.length > 0) {
        let currentSlide = 0;
        let slideInterval;

        // Create dots
        slides.forEach((_, idx) => {
            const dot = document.createElement('div');
            dot.classList.add('dot');
            if (idx === 0) dot.classList.add('active');
            dot.addEventListener('click', () => goToSlide(idx));
            dotsContainer.appendChild(dot);
        });

        const dots = document.querySelectorAll('.slider-dots .dot');

        function goToSlide(n) {
            slides[currentSlide].classList.remove('active');
            dots[currentSlide].classList.remove('active');
            currentSlide = (n + slides.length) % slides.length;
            slides[currentSlide].classList.add('active');
            dots[currentSlide].classList.add('active');
            resetInterval();
        }

        function nextSlide() { goToSlide(currentSlide + 1); }
        function prevSlide() { goToSlide(currentSlide - 1); }

        if (nextBtn) nextBtn.addEventListener('click', nextSlide);
        if (prevBtn) prevBtn.addEventListener('click', prevSlide);

        function startInterval() {
            slideInterval = setInterval(nextSlide, 5000);
        }

        function resetInterval() {
            clearInterval(slideInterval);
            startInterval();
        }

        startInterval();
    }
});

// ========================================
// SMART SEARCH LOGIC
// ========================================
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('search-input');
    const searchSuggestions = document.getElementById('search-suggestions');

    if (searchInput && searchSuggestions) {
        let debounceTimer;

        searchInput.addEventListener('input', function() {
            clearTimeout(debounceTimer);
            const query = this.value.trim();

            if (query.length < 2) {
                searchSuggestions.style.display = 'none';
                return;
            }

            debounceTimer = setTimeout(() => {
                fetch(`/api/search?q=${encodeURIComponent(query)}`)
                    .then(response => response.json())
                    .then(data => {
                        searchSuggestions.innerHTML = '';
                        if (data.length > 0) {
                            data.forEach(item => {
                                const div = document.createElement('div');
                                div.className = 'search-suggestion-item';
                                
                                div.innerHTML = `
                                    <img src="${item.image || 'https://via.placeholder.com/40'}" alt="${item.name}">
                                    <div class="suggestion-info">
                                        <h5>${item.name}</h5>
                                        <p>₹${item.price} - ${item.category}</p>
                                    </div>
                                `;
                                
                                div.onclick = () => window.location.href = `/product/${item.id}`;
                                searchSuggestions.appendChild(div);
                            });
                            searchSuggestions.style.display = 'block';
                        } else {
                            const div = document.createElement('div');
                            div.style.padding = '12px 16px';
                            div.style.color = '#666';
                            div.style.fontSize = '14px';
                            div.textContent = 'No products found.';
                            searchSuggestions.appendChild(div);
                            searchSuggestions.style.display = 'block';
                        }
                    })
                    .catch(err => console.error('Search error:', err));
            }, 300); // 300ms debounce
        });

        // Hide suggestions when clicking outside
        document.addEventListener('click', function(e) {
            if (!searchInput.contains(e.target) && !searchSuggestions.contains(e.target)) {
                searchSuggestions.style.display = 'none';
            }
        });
    }
});

// ========================================
// NEWSLETTER SUBSCRIPTION AJAX
// ========================================
document.addEventListener('DOMContentLoaded', function() {
    const newsForms = document.querySelectorAll('.newsletter-form');
    
    newsForms.forEach(newsForm => {
        newsForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const emailInput = this.querySelector('input[name="email"]');
            const submitBtn = this.querySelector('button');
            const originalBtnText = submitBtn.innerHTML;
            
            // Find the closest message div, either sibling or within the same container
            let newsMsg = this.nextElementSibling;
            if (!newsMsg || newsMsg.id !== 'newsletter-msg') {
                // If it doesn't exist next to it (like in the footer), create or find one
                let container = this.parentElement;
                newsMsg = container.querySelector('.newsletter-msg-dynamic');
                if (!newsMsg) {
                    newsMsg = document.createElement('div');
                    newsMsg.className = 'newsletter-msg-dynamic';
                    newsMsg.style.marginTop = '15px';
                    newsMsg.style.fontWeight = '500';
                    newsMsg.style.fontSize = '14px';
                    container.appendChild(newsMsg);
                }
            }
            
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            submitBtn.disabled = true;
            
            fetch('/subscribe', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: emailInput.value })
            })
            .then(response => response.json())
            .then(data => {
                newsMsg.textContent = data.message;
                newsMsg.style.color = data.status === 'success' ? '#C9A84C' : '#e74c3c';
                if (data.status === 'success') {
                    emailInput.value = '';
                }
                setTimeout(() => { newsMsg.textContent = ''; }, 5000);
            })
            .catch(error => {
                newsMsg.textContent = 'An error occurred. Please try again.';
                newsMsg.style.color = '#e74c3c';
            })
            .finally(() => {
                submitBtn.innerHTML = originalBtnText;
                submitBtn.disabled = false;
            });
        });
    });
});
