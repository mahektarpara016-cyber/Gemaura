from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, current_app
from database.models import db, User, Seller, Product, Category, Cart, Wishlist, Order, OrderItem, Review, Reel, ReelLike, ReelComment, Newsletter, Banner, Address, Coupon, GiftCard
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from functools import wraps

user_bp = Blueprint('user', __name__)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to continue.', 'warning')
            return redirect(url_for('user.login'))
        return f(*args, **kwargs)
    return decorated


@user_bp.route('/')

def index():
    categories = Category.query.all()
    featured = Product.query.order_by(Product.created_at.desc()).limit(8).all()
    trending = Product.query.order_by(Product.product_id.desc()).limit(4).all()
    flash_deals = Product.query.filter_by(is_flash_deal=True).limit(4).all()
    reels = Reel.query.order_by(Reel.created_at.desc()).limit(10).all()
    banners = Banner.query.all()
    # Wishlist IDs for the current user (so heart buttons show correct state)
    wishlist_ids = []
    if 'user_id' in session:
        from database.models import Wishlist
        wishlist_ids = [w.product_id for w in Wishlist.query.filter_by(user_id=session['user_id']).all()]
    return render_template('user/index.html', categories=categories, featured=featured,
                           trending=trending, flash_deals=flash_deals, reels=reels,
                           banners=banners, wishlist_ids=wishlist_ids)


@user_bp.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.json.get('email') if request.is_json else request.form.get('email')
    if not email:
        return jsonify({'status': 'error', 'message': 'Email is required'}), 400
    
    existing = Newsletter.query.filter_by(email=email).first()
    if existing:
        return jsonify({'status': 'info', 'message': 'You are already subscribed!'})
    
    new_sub = Newsletter(email=email)
    db.session.add(new_sub)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Thank you for joining Gemaura!'})

@user_bp.route('/reels')
def reels():
    # Fetch reels with seller and product info eagerly
    from sqlalchemy.orm import joinedload
    all_reels = Reel.query.options(joinedload(Reel.seller), joinedload(Reel.product)).order_by(Reel.created_at.desc()).all()
    return render_template('user/reels.html', reels=all_reels)

@user_bp.route('/reel/like/<int:reel_id>', methods=['POST'])
@login_required
def like_reel(reel_id):
    existing = ReelLike.query.filter_by(user_id=session['user_id'], reel_id=reel_id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        return jsonify({'liked': False, 'count': ReelLike.query.filter_by(reel_id=reel_id).count()})
    else:
        like = ReelLike(user_id=session['user_id'], reel_id=reel_id)
        db.session.add(like)
        db.session.commit()
        return jsonify({'liked': True, 'count': ReelLike.query.filter_by(reel_id=reel_id).count()})

@user_bp.route('/reel/comment/<int:reel_id>', methods=['POST'])
@login_required
def add_reel_comment(reel_id):
    content = request.form.get('comment')
    if not content:
        return jsonify({'status': 'error', 'message': 'Comment cannot be empty'}), 400
    
    comment = ReelComment(reel_id=reel_id, user_id=session['user_id'], comment=content)
    db.session.add(comment)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'user': session.get('name', 'User'),
        'comment': content,
        'created_at': 'Just now'
    })

@user_bp.route('/reel/comments/<int:reel_id>')
def get_reel_comments(reel_id):
    comments = ReelComment.query.filter_by(reel_id=reel_id).order_by(ReelComment.created_at.desc()).all()
    results = []
    for c in comments:
        results.append({
            'user': c.user.name,
            'comment': c.comment,
            'created_at': c.created_at.strftime('%b %d, %Y')
        })
    return jsonify(results)

@user_bp.route('/api/counts')
def get_counts():
    counts = {'wishlist': 0, 'cart': 0}
    if 'user_id' in session:
        counts['wishlist'] = Wishlist.query.filter_by(user_id=session['user_id']).count()
        counts['cart'] = Cart.query.filter_by(user_id=session['user_id']).count()
    return jsonify(counts)

@user_bp.route('/api/search')
def api_search():
    q = request.args.get('q', '')
    if len(q) < 2:
        return jsonify([])
    
    products = Product.query.filter(Product.name.ilike(f'%{q}%')).limit(5).all()
    results = []
    for p in products:
        results.append({
            'id': p.product_id,
            'name': p.name,
            'price': float(p.price),
            'image': url_for('static', filename='uploads/' + p.image) if p.image else None,
            'category': p.category.category_name
        })
    return jsonify(results)

@user_bp.route('/shop')
def shop():
    q = request.args.get('q', '')
    category_param = request.args.get('category', '')
    min_price = request.args.get('min_price', 0, type=float)
    max_price = request.args.get('max_price', 999999, type=float)
    sort = request.args.get('sort', 'newest')

    query = Product.query
    
    current_category = None
    if category_param:
        # Check if it's an ID or a Name
        if category_param.isdigit():
            current_category = Category.query.get(int(category_param))
        else:
            current_category = Category.query.filter(Category.category_name.ilike(category_param)).first()
        
        if current_category:
            query = query.filter_by(category_id=current_category.category_id)

    if q:
        query = query.filter(Product.name.ilike(f'%{q}%'))
        
    query = query.filter(Product.price >= min_price, Product.price <= max_price)
    
    if sort == 'price_low':
        query = query.order_by(Product.price.asc())
    elif sort == 'price_high':
        query = query.order_by(Product.price.desc())
    else:
        query = query.order_by(Product.created_at.desc())

    products = query.all()
    categories = Category.query.all()
    
    wishlist_ids = []
    if 'user_id' in session:
        wishlist_ids = [w.product_id for w in Wishlist.query.filter_by(user_id=session['user_id']).all()]
    
    return render_template('user/shop.html', products=products, categories=categories,
                           q=q, current_category=current_category, sort=sort, wishlist_ids=wishlist_ids)

@user_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    reviews = Review.query.filter_by(product_id=product_id).all()
    avg_rating = 0
    if reviews:
        avg_rating = sum(r.rating for r in reviews) / len(reviews)
    in_wishlist = False
    if 'user_id' in session:
        in_wishlist = Wishlist.query.filter_by(user_id=session['user_id'], product_id=product_id).first() is not None
    related = Product.query.filter_by(category_id=product.category_id).filter(Product.product_id != product_id).limit(4).all()
    return render_template('user/product_detail.html', product=product, reviews=reviews,
                           avg_rating=avg_rating, in_wishlist=in_wishlist, related=related)

@user_bp.route('/product/<int:product_id>/review', methods=['POST'])
@login_required
def add_review(product_id):
    rating = int(request.form.get('rating', 5))
    comment = request.form.get('comment', '')
    existing = Review.query.filter_by(user_id=session['user_id'], product_id=product_id).first()
    if existing:
        flash('You have already reviewed this product.', 'info')
    else:
        review = Review(user_id=session['user_id'], product_id=product_id, rating=rating, comment=comment)
        db.session.add(review)
        db.session.commit()
        flash('Review submitted!', 'success')
    return redirect(url_for('user.product_detail', product_id=product_id))

@user_bp.route('/cart')
@login_required
def cart():
    items = Cart.query.filter_by(user_id=session['user_id'], is_saved_for_later=False).all()
    saved_items = Cart.query.filter_by(user_id=session['user_id'], is_saved_for_later=True).all()
    total = sum(item.product.price * item.quantity for item in items if item.product)
    return render_template('user/cart.html', items=items, saved_items=saved_items, total=total)

@user_bp.route('/cart/add/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'user_id' not in session:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'error', 'message': 'You must login to add items to your cart.', 'redirect': url_for('user.login')}), 401
        flash('You must login to add items to your cart.', 'info')
        return redirect(url_for('user.login'))
    
    quantity = int(request.form.get('quantity', 1))
    item = Cart.query.filter_by(user_id=session['user_id'], product_id=product_id).first()
    if item:
        item.quantity += quantity
    else:
        item = Cart(user_id=session['user_id'], product_id=product_id, quantity=quantity)
        db.session.add(item)
    db.session.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'status': 'success', 'message': 'Added to cart!', 'count': Cart.query.filter_by(user_id=session['user_id']).count()})
    
    flash('Added to cart!', 'success')
    return redirect(request.referrer or url_for('user.cart'))

@user_bp.route('/cart/remove/<int:cart_id>')
@login_required
def remove_from_cart(cart_id):
    item = Cart.query.get_or_404(cart_id)
    if item.user_id == session['user_id']:
        db.session.delete(item)
        db.session.commit()
    return redirect(url_for('user.cart'))

@user_bp.route('/cart/update/<int:cart_id>', methods=['POST'])
@login_required
def update_cart(cart_id):
    item = Cart.query.get_or_404(cart_id)
    if item.user_id == session['user_id']:
        item.quantity = int(request.form.get('quantity', 1))
        db.session.commit()
    return redirect(url_for('user.cart'))

@user_bp.route('/cart/save-for-later/<int:cart_id>')
@login_required
def toggle_save_for_later(cart_id):
    item = Cart.query.get_or_404(cart_id)
    if item.user_id == session['user_id']:
        item.is_saved_for_later = not item.is_saved_for_later
        db.session.commit()
        msg = "Item saved for later." if item.is_saved_for_later else "Item moved to cart."
        flash(msg, 'success')
    return redirect(url_for('user.cart'))

@user_bp.route('/wishlist')
@login_required
def wishlist():
    items = Wishlist.query.filter_by(user_id=session['user_id']).all()
    return render_template('user/wishlist.html', items=items)

@user_bp.route('/wishlist/toggle/<int:product_id>', methods=['POST'])
@login_required
def toggle_wishlist(product_id):
    item = Wishlist.query.filter_by(user_id=session['user_id'], product_id=product_id).first()
    if item:
        db.session.delete(item)
        db.session.commit()
        return jsonify({'in_wishlist': False})
    else:
        w = Wishlist(user_id=session['user_id'], product_id=product_id)
        db.session.add(w)
        db.session.commit()
        return jsonify({'in_wishlist': True})

@user_bp.route('/checkout')
@login_required
def checkout():
    items = Cart.query.filter_by(user_id=session['user_id'], is_saved_for_later=False).all()
    if not items:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('user.cart'))

    addresses = Address.query.filter_by(user_id=session['user_id']).order_by(Address.is_default.desc()).all()
    subtotal = sum(item.product.price * item.quantity for item in items if item.product)
    
    # Simple logic for shipping and tax for now
    shipping_fee = 150.00 if subtotal < 5000 else 0.00
    tax = float(subtotal) * 0.03 # 3% GST for jewellery
    total = float(subtotal) + shipping_fee + tax

    return render_template('user/checkout.html', 
                           items=items, 
                           addresses=addresses,
                           subtotal=subtotal,
                           shipping_fee=shipping_fee,
                           tax=tax,
                           total=total)

@user_bp.route('/address/add', methods=['POST'])
@login_required
def add_address():
    name = request.form.get('name')
    phone = request.form.get('phone')
    pincode = request.form.get('pincode')
    city = request.form.get('city')
    state = request.form.get('state')
    full_address = request.form.get('full_address')
    is_default = 'is_default' in request.form

    if is_default:
        Address.query.filter_by(user_id=session['user_id']).update({'is_default': False})

    new_address = Address(
        user_id=session['user_id'],
        name=name,
        phone=phone,
        pincode=pincode,
        city=city,
        state=state,
        full_address=full_address,
        is_default=is_default
    )
    db.session.add(new_address)
    db.session.commit()
    flash('Address added successfully!', 'success')
    return redirect(url_for('user.checkout'))

@user_bp.route('/address/edit/<int:address_id>', methods=['POST'])
@login_required
def edit_address(address_id):
    address = Address.query.get_or_404(address_id)
    if address.user_id != session['user_id']:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
    
    address.name = request.form.get('name')
    address.phone = request.form.get('phone')
    address.pincode = request.form.get('pincode')
    address.city = request.form.get('city')
    address.state = request.form.get('state')
    address.full_address = request.form.get('full_address')
    
    if 'is_default' in request.form:
        Address.query.filter_by(user_id=session['user_id']).update({'is_default': False})
        address.is_default = True
        
    db.session.commit()
    flash('Address updated successfully!', 'success')
    return redirect(url_for('user.checkout'))

@user_bp.route('/address/delete/<int:address_id>')
@login_required
def delete_address(address_id):
    address = Address.query.get_or_404(address_id)
    if address.user_id == session['user_id']:
        db.session.delete(address)
        db.session.commit()
        flash('Address deleted successfully!', 'success')
    return redirect(url_for('user.checkout'))

@user_bp.route('/coupon/apply', methods=['POST'])
@login_required
def apply_coupon():
    code = request.json.get('code')
    subtotal = float(request.json.get('subtotal', 0))
    
    coupon = Coupon.query.filter_by(code=code, is_active=True).first()
    if not coupon:
        return jsonify({'status': 'error', 'message': 'Invalid or inactive coupon code.'}), 400
    
    if datetime.utcnow() > coupon.expiry_date:
        return jsonify({'status': 'error', 'message': 'This coupon has expired.'}), 400
    
    if subtotal < float(coupon.min_purchase):
        return jsonify({'status': 'error', 'message': f'Minimum purchase of {coupon.min_purchase} required.'}), 400
    
    discount = 0
    if coupon.discount_type == 'percent':
        discount = subtotal * (float(coupon.discount_value) / 100)
    else:
        discount = float(coupon.discount_value)
    
    return jsonify({
        'status': 'success',
        'coupon_id': coupon.coupon_id,
        'discount': discount,
        'message': f'Coupon "{code}" applied!'
    })

@user_bp.route('/giftcard/apply', methods=['POST'])
@login_required
def apply_gift_card():
    code = request.json.get('code')
    
    gc = GiftCard.query.filter_by(code=code, is_active=True).first()
    if not gc:
        return jsonify({'status': 'error', 'message': 'Invalid or inactive gift card.'}), 400
    
    if datetime.utcnow() > gc.expiry_date:
        return jsonify({'status': 'error', 'message': 'This gift card has expired.'}), 400
    
    return jsonify({
        'status': 'success',
        'card_id': gc.card_id,
        'balance': float(gc.balance),
        'message': 'Gift card applied!'
    })

@user_bp.route('/order/place', methods=['POST'])
@login_required
def place_order():
    address_id = request.form.get('address_id')
    payment_method = request.form.get('payment_method')
    coupon_id = request.form.get('coupon_id')
    gift_card_id = request.form.get('gift_card_id')
    order_notes = request.form.get('order_notes')
    
    if not address_id:
        flash('Please select a delivery address.', 'danger')
        return redirect(url_for('user.checkout'))
    
    gc_deduction = float(request.form.get('gc_deduction', 0))
    upi_id = request.form.get('upi_id')
    address = Address.query.get(address_id)
    
    if not address:
        flash('Invalid delivery address selected.', 'danger')
        return redirect(url_for('user.checkout'))
        
    cart_items = Cart.query.filter_by(user_id=session['user_id'], is_saved_for_later=False).all()
    
    if not cart_items:
        return redirect(url_for('user.cart'))
        
    subtotal = sum(item.product.price * item.quantity for item in cart_items)
    shipping = float(request.form.get('shipping_fee', 0))
    tax = float(request.form.get('tax', 0))
    
    discount = float(request.form.get('discount_amount', 0))

    final_total = float(subtotal) + shipping + tax - discount
    
    # Set payment status based on method
    payment_status = 'Pending'
    if payment_method in ['upi', 'card']:
        payment_status = 'Paid (Simulation)'
        
    order = Order(
        user_id=session['user_id'],
        subtotal=subtotal,
        shipping_fee=shipping,
        tax=tax,
        discount_amount=discount,
        total_price=max(0, final_total),
        status='pending', # New orders start as Pending
        shipping_name=address.name,
        shipping_phone=address.phone,
        shipping_address=f"{address.full_address}, {address.city}, {address.state} - {address.pincode}",
        payment_method=payment_method,
        upi_id=upi_id if payment_method == 'upi' else None,
        payment_status=payment_status,
        coupon_id=coupon_id if coupon_id else None,
        gift_card_id=gift_card_id if gift_card_id else None,
        total_admin_commission=0,
        total_seller_profit=0,
        order_notes=order_notes
    )
    
    db.session.add(order)
    db.session.flush()
    
    for item in cart_items:
        price = float(item.product.price)
        comm = price * 0.10
        profit = price - comm
        
        oi = OrderItem(
            order_id=order.order_id, 
            product_id=item.product_id,
            quantity=item.quantity, 
            price_at_time=price,
            admin_commission=comm * item.quantity,
            seller_profit=profit * item.quantity
        )
        order.total_admin_commission += (comm * item.quantity)
        order.total_seller_profit += (profit * item.quantity)
        item.product.stock = max(0, item.product.stock - item.quantity)
        db.session.add(oi)
        db.session.delete(item)
    
    if gift_card_id and gc_deduction > 0:
        gc = GiftCard.query.get(gift_card_id)
        if gc:
            gc.balance = float(gc.balance) - gc_deduction
            if gc.balance <= 0:
                gc.is_active = False
            
    db.session.commit()
    flash('Your royal order has been placed successfully!', 'success')
    return render_template('user/order_success.html', order=order)

@user_bp.route('/orders')
@login_required
def orders():
    search_query = request.args.get('search', '')
    status_filter = request.args.get('status', 'all')
    sort_order = request.args.get('sort', 'newest')
    
    query = Order.query.filter_by(user_id=session['user_id'])
    
    if search_query:
        # Search by order ID or product names within the order
        search_pattern = f"%{search_query}%"
        query = query.join(OrderItem).join(Product).filter(
            db.or_(
                Order.order_id.like(search_pattern),
                Product.name.ilike(search_pattern)
            )
        ).distinct()
    
    if status_filter != 'all':
        query = query.filter(Order.status == status_filter.lower())
        
    if sort_order == 'oldest':
        query = query.order_by(Order.created_at.asc())
    else:
        query = query.order_by(Order.created_at.desc())
        
    user_orders = query.all()
    return render_template('user/orders.html', orders=user_orders, search=search_query, status=status_filter, sort=sort_order)

@user_bp.route('/order/<int:order_id>')
@login_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != session['user_id']:
        flash('Unauthorized access to order.', 'danger')
        return redirect(url_for('user.orders'))
    return render_template('user/order_detail.html', order=order)

@user_bp.route('/order/cancel/<int:order_id>', methods=['POST'])
@login_required
def cancel_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != session['user_id']:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
    
    # Allowed to cancel if Pending or Shipped
    if order.status.lower() in ['pending', 'confirmed', 'shipped']:
        order.status = 'cancelled'
        order.cancel_date = datetime.utcnow()
        order.cancel_reason = request.form.get('reason', 'User cancelled')
        
        # Handle Refund Logic
        if order.payment_status.lower() in ['paid', 'paid (simulation)', 'completed']:
            order.refund_amount = order.total_price
            order.refund_status = 'processing'
            flash(f'Order #GEM-{order_id} cancelled. Refund of ₹{order.total_price} initiated.', 'success')
        else:
            order.refund_status = 'na'
            flash(f'Order #GEM-{order_id} has been cancelled successfully.', 'success')
            
        # Restock products
        for item in order.items:
            item.product.stock += item.quantity
            
        db.session.commit()
    else:
        flash('Order cannot be cancelled at this stage.', 'warning')
        
    return redirect(url_for('user.orders'))

@user_bp.route('/order/reorder/<int:order_id>')
@login_required
def reorder(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != session['user_id']:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('user.orders'))
    
    # Add all items from the old order back to the cart
    for item in order.items:
        # Check if item already exists in cart for this user
        existing_cart = Cart.query.filter_by(user_id=session['user_id'], product_id=item.product_id).first()
        if existing_cart:
            existing_cart.quantity += item.quantity
        else:
            new_cart = Cart(user_id=session['user_id'], product_id=item.product_id, quantity=item.quantity)
            db.session.add(new_cart)
            
    db.session.commit()
    flash('Items from previous order added to your cart!', 'success')
    return redirect(url_for('user.cart'))

@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'update_profile':
            user.name = request.form.get('name', user.name)
            user.phone = request.form.get('phone', user.phone)
            user.address = request.form.get('address', user.address)
            db.session.commit()
            flash('Personal information updated successfully!', 'success')
        elif action == 'change_password':
            old_pass = request.form.get('old_password')
            new_pass = request.form.get('new_password')
            if check_password_hash(user.password, old_pass):
                user.password = generate_password_hash(new_pass)
                db.session.commit()
                flash('Password updated successfully!', 'success')
            else:
                flash('Current password incorrect.', 'error')
        elif action == 'update_preferences':
            # Handle preferences in a real app (e.g. settings table)
            flash('Preferences updated!', 'success')
        return redirect(url_for('user.profile'))
    return render_template('user/profile.html', user=user)

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('user.index'))
    
    # Handle custom message from guest redirect
    msg = request.args.get('msg')
    if msg:
        flash(msg, 'info')

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session.clear()
            session['user_id'] = user.user_id
            session['role'] = 'user'
            session['name'] = user.name
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(url_for('user.index'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('user/login.html')

@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
        else:
            user = User(name=name, email=email, password=generate_password_hash(password))
            db.session.add(user)
            db.session.commit()
            session.clear()
            session['user_id'] = user.user_id
            session['role'] = 'user'
            session['name'] = user.name
            flash('Registration successful!', 'success')
            return redirect(url_for('user.index'))
    return render_template('user/register.html')

@user_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('user.index'))

@user_bp.route('/about')
def about():
    return render_template('user/about.html')

@user_bp.route('/contact')
def contact():
    return render_template('user/contact.html')
