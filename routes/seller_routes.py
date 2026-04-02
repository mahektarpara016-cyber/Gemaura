import os
import shutil
import uuid
import random
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app, jsonify
from database.models import db, Seller, Product, Category, Order, OrderItem, Reel
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import os
from datetime import datetime, timedelta

seller_bp = Blueprint('seller', __name__)

REELS_FOLDER = ""

@seller_bp.before_app_request
def set_reels_folder():
    global REELS_FOLDER
    REELS_FOLDER = os.path.join(current_app.root_path, 'static', 'reels')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'mov', 'avi'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_video(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_VIDEO_EXTENSIONS

def seller_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('user.login'))
        if session.get('role') != 'seller':
            flash('Access Denied', 'danger')
            return redirect(url_for('user.index'))
        seller = Seller.query.get(session['user_id'])
        if not seller or seller.status != 'approved':
            flash('Your account is pending approval or has been disabled.', 'warning')
            return redirect(url_for('user.login'))
        return f(*args, **kwargs)
    return decorated

@seller_bp.context_processor
def inject_seller():
    if 'seller_id' in session:
        seller = Seller.query.get(session['seller_id'])
        return dict(seller=seller)
    return dict(seller=None)

@seller_bp.route('/')
@seller_required
def dashboard():
    seller_id = session['seller_id']
    filter_type = request.args.get('filter', 'all')
    now = datetime.utcnow()
    
    # Base query for orders containing this seller's products
    order_query = db.session.query(Order).join(OrderItem).join(Product)\
        .filter(Product.seller_id == seller_id)
    
    if filter_type == 'today':
        order_query = order_query.filter(Order.created_at >= now.replace(hour=0, minute=0, second=0, microsecond=0))
    elif filter_type == 'week':
        order_query = order_query.filter(Order.created_at >= now - timedelta(days=7))
    elif filter_type == 'month':
        order_query = order_query.filter(Order.created_at >= now.replace(day=1, hour=0, minute=0, second=0, microsecond=0))
    
    orders = order_query.all()
    
    # Financial Stats for this seller
    total_sales = 0
    seller_earnings = 0
    total_loss = 0
    
    # Detailed Order List for the table
    order_details = []
    
    for order in orders:
        # Calculate seller's share in this order
        order_items = [item for item in order.items if item.product.seller_id == seller_id]
        
        o_sales = sum(item.price_at_time * item.quantity for item in order_items)
        o_earnings = sum(item.seller_profit for item in order_items)
        
        # Loss: if cancelled after payment
        o_loss = 0
        if order.status == 'cancelled' and order.payment_status.lower() in ['paid', 'paid (simulation)', 'completed']:
            o_loss = o_sales
            
        total_sales += o_sales
        seller_earnings += o_earnings
        total_loss += o_loss

        # Add to details for the table
        for item in order_items:
            i_loss = item.price_at_time * item.quantity if o_loss > 0 else 0
            order_details.append({
                'product_name': item.product.name,
                'quantity': item.quantity,
                'price': item.price_at_time,
                'status': order.status,
                'earnings': item.seller_profit,
                'loss': i_loss,
                'created_at': order.created_at
            })
    
    net_earnings = float(seller_earnings) - float(total_loss)
    
    total_orders = len(orders)
    pending_orders = len([o for o in orders if o.status == 'pending'])
    
    # Chart Data: Daily Stats for Last 30 Days
    days_limit = 30
    start_date = now - timedelta(days=days_limit)
    
    daily_stats_query = db.session.query(
        func.date(Order.created_at).label('date'),
        func.sum(OrderItem.seller_profit).label('profit'),
        func.sum(OrderItem.price_at_time * OrderItem.quantity).label('sales')
    ).join(OrderItem).join(Product)\
     .filter(Product.seller_id == seller_id)\
     .filter(Order.created_at >= start_date)\
     .group_by(func.date(Order.created_at))\
     .order_by('date').all()
    
    chart_labels = [str(s.date) for s in daily_stats_query]
    chart_sales = [float(s.sales) for s in daily_stats_query]
    chart_profit = [float(s.profit) for s in daily_stats_query]
    
    # Top Products
    top_products = db.session.query(
        Product.name,
        func.sum(OrderItem.quantity).label('total_sold')
    ).join(OrderItem).filter(Product.seller_id == seller_id)\
     .group_by(Product.product_id).order_by(func.sum(OrderItem.quantity).desc()).limit(5).all()
    
    # Status Breakdown
    status_stats = db.session.query(
        Order.status,
        func.count(func.distinct(Order.order_id)).label('count')
    ).join(OrderItem).join(Product)\
     .filter(Product.seller_id == seller_id)\
     .group_by(Order.status).all()
    
    status_labels = [s.status.title() for s in status_stats]
    status_counts = [s.count for s in status_stats]
    
    return render_template('seller/dashboard.html',
                           total_sales=total_sales, seller_earnings=seller_earnings,
                           total_loss=total_loss, net_earnings=net_earnings,
                           total_orders=total_orders, pending_orders=pending_orders,
                           chart_labels=chart_labels, chart_profit=chart_profit,
                           chart_sales=chart_sales, filter_type=filter_type,
                           top_products=top_products, 
                           status_labels=status_labels, status_counts=status_counts,
                           orders=orders,
                           order_details=order_details)

@seller_bp.route('/products')
@seller_required
def products():
    seller_id = session['seller_id']
    prods = Product.query.filter_by(seller_id=seller_id).order_by(Product.created_at.desc()).all()
    return render_template('seller/products.html', products=prods)

@seller_bp.route('/products/add', methods=['GET', 'POST'])
@seller_required
def add_product():
    categories = Category.query.all()
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = float(request.form.get('price', 0))
        category_id = int(request.form.get('category_id'))
        stock = int(request.form.get('stock', 0))
        image_filename = None
        
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
                filename = secure_filename(file.filename)
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                image_filename = filename

        is_flash = 'is_flash_deal' in request.form
        deal_price = request.form.get('deal_price')
        
        product = Product(seller_id=session['seller_id'], name=name, description=description,
                          price=price, category_id=category_id, stock=stock, image=image_filename,
                          is_flash_deal=is_flash,
                          deal_price=float(deal_price) if deal_price and is_flash else None)
        db.session.add(product)
        db.session.commit()
        flash('Product added successfully!', 'success')
        return redirect(url_for('seller.products'))
    return render_template('seller/add_product.html', categories=categories)

@seller_bp.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
@seller_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    if product.seller_id != session['seller_id']:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('seller.products'))
    categories = Category.query.all()
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.price = float(request.form.get('price', product.price))
        product.category_id = int(request.form.get('category_id'))
        product.stock = int(request.form.get('stock', product.stock))
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
                filename = secure_filename(file.filename)
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                product.image = filename
        
        product.is_flash_deal = 'is_flash_deal' in request.form
        if product.is_flash_deal:
            product.deal_price = float(request.form.get('deal_price', product.price))
        else:
            product.deal_price = None
        db.session.commit()
        flash('Product updated!', 'success')
        return redirect(url_for('seller.products'))
    return render_template('seller/edit_product.html', product=product, categories=categories)

@seller_bp.route('/products/delete/<int:product_id>', methods=['POST'])
@seller_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    if product.seller_id == session['seller_id']:
        db.session.delete(product)
        db.session.commit()
        flash('Product deleted successfully.', 'success')
    else:
        flash('Unauthorized action.', 'danger')
    return redirect(url_for('seller.products'))

@seller_bp.route('/auto_generate_products/<int:category_id>', methods=['POST'])
@seller_required
def auto_generate_products(category_id):
    seller_id = session['seller_id']
    category = Category.query.get(category_id)
    if not category:
        return jsonify({'success': False, 'message': 'Category not found'})

    # Check if this seller already has products in this category
    existing_count = Product.query.filter_by(seller_id=seller_id, category_id=category_id).count()
    if existing_count >= 10:
        # User requested to only generate 10 products ONCE per category to prevent duplicates
        return jsonify({
            'success': False, 
            'message': f'Products already exist in {category.category_name}. Auto-generation skipped.'
        })

    cat_name = category.category_name.lower()
    cat_key = None
    if 'ring' in cat_name: cat_key = 'rings'
    elif 'necklace' in cat_name: cat_key = 'necklaces'
    elif 'earring' in cat_name or 'jhumka' in cat_name: cat_key = 'earrings'
    elif 'bracelet' in cat_name: cat_key = 'bracelets'
    elif 'bangle' in cat_name: cat_key = 'bangles'
    else:
        return jsonify({'success': False, 'message': 'Auto-generation not supported for this generic category.'})

    auto_data = {
        'rings': {
            'names': ['Elegant Gold Ring', 'Classic Engagement Ring', 'Luxury Diamond Ring', 'Minimal Daily Ring', 'Royal Wedding Ring', 'Premium Shine Ring', 'Designer Couple Ring', 'Modern Style Ring', 'Traditional Gold Ring', 'Lightweight Fashion Ring'],
            'titles': ['Premium Jewellery Collection', 'Trending Ring Design', 'Best Seller Jewellery', 'Luxury Handmade Jewellery', 'Designer Collection', 'Modern Gold Collection', 'Wedding Jewellery', 'Special Occasion Jewellery', 'New Arrival Jewellery', 'Elegant Fashion Jewellery'],
            'descriptions': [
                'A beautifully crafted jewellery piece designed with premium finishing and elegant shine suitable for weddings and special occasions.',
                'This jewellery item offers a luxurious design with high quality craftsmanship and long lasting durability.',
                'Perfect for daily wear as well as parties, this design combines modern style with traditional beauty.',
                'A premium jewellery product with fine polish and elegant structure that enhances your overall look.',
                'Lightweight and stylish jewellery made for comfort and elegance.',
                'Specially designed jewellery for modern fashion lovers with premium quality finishing.',
                'An eye-catching jewellery design perfect for gifting and celebrations.',
                'A luxurious jewellery product crafted carefully to deliver a royal appearance.',
                'Trendy jewellery with modern design and premium shine.',
                'Elegant handcrafted jewellery with superior finishing and stylish look.'
            ]
        },
        'necklaces': {
            'names': ['Bridal Necklace Set', 'Classic Kundan Necklace', 'Luxury Statement Choker', 'Minimal Daily Necklace', 'Royal Wedding Necklace', 'Premium Pearl Drop', 'Designer Long Chain', 'Modern Style Chain', 'Traditional Gold Choker', 'Lightweight Fashion Piece'],
            'titles': ['Premium Jewellery Collection', 'Trending Necklace Design', 'Best Seller Jewellery', 'Luxury Handmade Jewellery', 'Designer Collection', 'Modern Gold Collection', 'Wedding Jewellery', 'Special Occasion Jewellery', 'New Arrival Jewellery', 'Elegant Fashion Jewellery'],
            'descriptions': [
                'A beautifully crafted jewellery piece designed with premium finishing and elegant shine suitable for weddings and special occasions.',
                'This jewellery item offers a luxurious design with high quality craftsmanship and long lasting durability.',
                'Perfect for daily wear as well as parties, this design combines modern style with traditional beauty.',
                'A premium jewellery product with fine polish and elegant structure that enhances your overall look.',
                'Lightweight and stylish jewellery made for comfort and elegance.',
                'Specially designed jewellery for modern fashion lovers with premium quality finishing.',
                'An eye-catching jewellery design perfect for gifting and celebrations.',
                'A luxurious jewellery product crafted carefully to deliver a royal appearance.',
                'Trendy jewellery with modern design and premium shine.',
                'Elegant handcrafted jewellery with superior finishing and stylish look.'
            ]
        },
        'earrings': {
            'names': ['Bridal Jhumka Set', 'Classic Studs', 'Luxury Drop Earrings', 'Minimal Daily Hoops', 'Royal Wedding Earrings', 'Premium Pearl Drops', 'Designer Chandelier', 'Modern Style Studs', 'Traditional Gold Tops', 'Lightweight Fashion Hoops'],
            'titles': ['Premium Jewellery Collection', 'Trending Earring Design', 'Best Seller Jewellery', 'Luxury Handmade Jewellery', 'Designer Collection', 'Modern Gold Collection', 'Wedding Jewellery', 'Special Occasion Jewellery', 'New Arrival Jewellery', 'Elegant Fashion Jewellery'],
            'descriptions': [
                'A beautifully crafted jewellery piece designed with premium finishing and elegant shine suitable for weddings and special occasions.',
                'This jewellery item offers a luxurious design with high quality craftsmanship and long lasting durability.',
                'Perfect for daily wear as well as parties, this design combines modern style with traditional beauty.',
                'A premium jewellery product with fine polish and elegant structure that enhances your overall look.',
                'Lightweight and stylish jewellery made for comfort and elegance.',
                'Specially designed jewellery for modern fashion lovers with premium quality finishing.',
                'An eye-catching jewellery design perfect for gifting and celebrations.',
                'A luxurious jewellery product crafted carefully to deliver a royal appearance.',
                'Trendy jewellery with modern design and premium shine.',
                'Elegant handcrafted jewellery with superior finishing and stylish look.'
            ]
        },
        'bracelets': {
            'names': ['Bridal Golden Bracelet', 'Classic Chain Bracelet', 'Luxury Diamond Bracelet', 'Minimal Daily Wear', 'Royal Wedding Bangle-Style', 'Premium Charm Bracelet', 'Designer Hand Chain', 'Modern Style Bracelet', 'Traditional Gold Chain', 'Lightweight Fashion Cuff'],
            'titles': ['Premium Jewellery Collection', 'Trending Bracelet Design', 'Best Seller Jewellery', 'Luxury Handmade Jewellery', 'Designer Collection', 'Modern Gold Collection', 'Wedding Jewellery', 'Special Occasion Jewellery', 'New Arrival Jewellery', 'Elegant Fashion Jewellery'],
            'descriptions': [
                'A beautifully crafted jewellery piece designed with premium finishing and elegant shine suitable for weddings and special occasions.',
                'This jewellery item offers a luxurious design with high quality craftsmanship and long lasting durability.',
                'Perfect for daily wear as well as parties, this design combines modern style with traditional beauty.',
                'A premium jewellery product with fine polish and elegant structure that enhances your overall look.',
                'Lightweight and stylish jewellery made for comfort and elegance.',
                'Specially designed jewellery for modern fashion lovers with premium quality finishing.',
                'An eye-catching jewellery design perfect for gifting and celebrations.',
                'A luxurious jewellery product crafted carefully to deliver a royal appearance.',
                'Trendy jewellery with modern design and premium shine.',
                'Elegant handcrafted jewellery with superior finishing and stylish look.'
            ]
        },
        'bangles': {
            'names': ['Bridal Chura Set', 'Classic Kundan Kadas', 'Luxury Gold Bangles', 'Minimal Daily Glass Bangles', 'Royal Wedding Set', 'Premium Shine Kadas', 'Designer Enamel Bangles', 'Modern Style Cuff', 'Traditional Gold Plated', 'Lightweight Fashion Set'],
            'titles': ['Premium Jewellery Collection', 'Trending Bangle Design', 'Best Seller Jewellery', 'Luxury Handmade Jewellery', 'Designer Collection', 'Modern Gold Collection', 'Wedding Jewellery', 'Special Occasion Jewellery', 'New Arrival Jewellery', 'Elegant Fashion Jewellery'],
            'descriptions': [
                'A beautifully crafted jewellery piece designed with premium finishing and elegant shine suitable for weddings and special occasions.',
                'This jewellery item offers a luxurious design with high quality craftsmanship and long lasting durability.',
                'Perfect for daily wear as well as parties, this design combines modern style with traditional beauty.',
                'A premium jewellery product with fine polish and elegant structure that enhances your overall look.',
                'Lightweight and stylish jewellery made for comfort and elegance.',
                'Specially designed jewellery for modern fashion lovers with premium quality finishing.',
                'An eye-catching jewellery design perfect for gifting and celebrations.',
                'A luxurious jewellery product crafted carefully to deliver a royal appearance.',
                'Trendy jewellery with modern design and premium shine.',
                'Elegant handcrafted jewellery with superior finishing and stylish look.'
            ]
        }
    }

    data = auto_data[cat_key]
    generated_products = []
    base_image_dir = os.path.join(current_app.root_path, 'static', 'images', 'products', cat_key)
    dest_dir = current_app.config['UPLOAD_FOLDER']
    
    os.makedirs(dest_dir, exist_ok=True)
    os.makedirs(os.path.join(dest_dir, 'products'), exist_ok=True)

    for i in range(10):
        c_name = data['names'][i]
        c_title = data['titles'][i]
        c_desc = data['descriptions'][i]
        
        # We store the title prominently in the description
        full_desc = f"Title: {c_title}\n\n{c_desc}"
        
        # Handle Image Copy
        src_img = os.path.join(base_image_dir, f"{i+1}.jpg")
        img_filename = os.path.join('products', f"{cat_key}_{uuid.uuid4().hex[:8]}.jpg")
        dest_img = os.path.join(dest_dir, img_filename)
        
        if os.path.exists(src_img):
            shutil.copy(src_img, dest_img)
        else:
            img_filename = "" # Fallback
            
        # Random Price
        price = random.randint(499, 14999)

        prod = Product(
            seller_id=seller_id,
            category_id=category_id,
            name=c_name,
            description=full_desc,
            price=price,
            stock=100,
            image=img_filename
        )
        db.session.add(prod)
        db.session.flush() # to get id if needed
        
        # Append for json response
        generated_products.append({
            'product_id': prod.product_id,
            'name': c_name,
            'title': c_title,
            'description': c_desc,
            'price': price,
            'image': img_filename
        })
        
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Automatically generated 10 {cat_key} products!',
        'products': generated_products
    })

@seller_bp.route('/orders')
@seller_required
def orders():
    seller_id = session['seller_id']
    products = Product.query.filter_by(seller_id=seller_id).all()
    product_ids = [p.product_id for p in products]
    
    if not product_ids:
        return render_template('seller/orders.html', orders_data=[])
        
    order_items = OrderItem.query.filter(OrderItem.product_id.in_(product_ids)).all()
    order_ids = list(set(oi.order_id for oi in order_items))
    orders = Order.query.filter(Order.order_id.in_(order_ids)).order_by(Order.created_at.desc()).all()
    
    orders_data = []
    for o in orders:
        # Calculate seller specific total and profit for this order
        items_in_order = OrderItem.query.filter(OrderItem.order_id == o.order_id, OrderItem.product_id.in_(product_ids)).all()
        seller_total = sum(float(i.price_at_time) * i.quantity for i in items_in_order)
        seller_profit = sum(float(i.seller_profit) for i in items_in_order)
        orders_data.append({
            'order': o,
            'seller_total': seller_total,
            'seller_profit': seller_profit,
            'items_count': sum(i.quantity for i in items_in_order)
        })
        
    return render_template('seller/orders.html', orders_data=orders_data)

@seller_bp.route('/orders/update/<int:order_id>', methods=['POST'])
@seller_required
def update_order(order_id):
    order = Order.query.get_or_404(order_id)
    order.status = request.form.get('status', order.status)
    db.session.commit()
    flash('Order status updated!', 'success')
    return redirect(url_for('seller.orders'))

@seller_bp.route('/earnings')
@seller_required
def earnings():
    seller_id = session['seller_id']
    products = Product.query.filter_by(seller_id=seller_id).all()
    product_ids = [p.product_id for p in products]
    
    if not product_ids:
        return render_template('seller/earnings.html', earnings_data=[], summary={})
        
    order_items = OrderItem.query.filter(OrderItem.product_id.in_(product_ids)).all()
    order_ids = list(set(oi.order_id for oi in order_items))
    orders = Order.query.filter(Order.order_id.in_(order_ids)).order_by(Order.created_at.desc()).all()
    
    earnings_data = []
    total_sales = 0
    total_profit = 0
    total_loss = 0
    
    for o in orders:
        items = OrderItem.query.filter(OrderItem.order_id == o.order_id, OrderItem.product_id.in_(product_ids)).all()
        order_total = sum(float(i.price_at_time) * i.quantity for i in items)
        order_profit = sum(float(i.seller_profit) for i in items)
        
        loss = 0
        if o.status == 'cancelled' and o.payment_status.lower() in ['paid', 'paid (simulation)', 'completed']:
            loss = order_profit
            total_loss += loss
        else:
            total_sales += order_total
            total_profit += order_profit
            
        earnings_data.append({
            'order_id': o.order_id,
            'date': o.created_at,
            'status': o.status,
            'total': order_total,
            'profit': order_profit,
            'loss': loss
        })
        
    summary = {
        'total_sales': total_sales,
        'total_profit': total_profit,
        'total_loss': total_loss,
        'net_earnings': total_profit - total_loss
    }
    
    return render_template('seller/earnings.html', earnings_data=earnings_data, summary=summary)

@seller_bp.route('/profile', methods=['GET', 'POST'])
@seller_required
def profile():
    seller = Seller.query.get(session['seller_id'])
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'update_profile':
            seller.shop_name = request.form.get('shop_name', seller.shop_name)
            seller.bio = request.form.get('bio', seller.bio)
            seller.email = request.form.get('email', seller.email)
            
            if 'logo' in request.files:
                file = request.files['logo']
                if file and file.filename and allowed_file(file.filename):
                    upload_path = os.path.join(current_app.root_path, 'static', 'uploads', 'profiles')
                    os.makedirs(upload_path, exist_ok=True)
                    filename = secure_filename(f"seller_{seller.seller_id}_{file.filename}")
                    file.save(os.path.join(upload_path, filename))
                    seller.logo = filename
            
            db.session.commit()
            flash('Profile updated successfully!', 'success')
        elif action == 'change_password':
            old_pass = request.form.get('old_password')
            new_pass = request.form.get('new_password')
            if check_password_hash(seller.password, old_pass):
                seller.password = generate_password_hash(new_pass)
                db.session.commit()
                flash('Password changed successfully!', 'success')
            else:
                flash('Incorrect current password.', 'danger')
        elif action == 'remove_photo':
            seller.logo = None
            db.session.commit()
            flash('Profile photo removed.', 'info')
        return redirect(url_for('seller.profile'))
    return render_template('seller/profile.html', seller=seller)

@seller_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'seller_id' in session:
        return redirect(url_for('seller.dashboard'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        seller = Seller.query.filter_by(email=email).first()
        if seller and check_password_hash(seller.password, password):
            session.clear()
            session['user_id'] = seller.seller_id
            session['seller_id'] = seller.seller_id
            session['role'] = 'seller'
            session['name'] = seller.shop_name
            flash(f'Welcome, {seller.shop_name}!', 'success')
            return redirect(url_for('seller.dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('seller/login.html')

@seller_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        shop_name = request.form.get('shop_name')
        email = request.form.get('email')
        password = request.form.get('password')
        if Seller.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
        else:
            seller = Seller(shop_name=shop_name, email=email,
                            password=generate_password_hash(password), status='pending')
            db.session.add(seller)
            db.session.commit()
            flash('Registration submitted! Awaiting admin approval.', 'success')
            return redirect(url_for('seller.login'))
    return render_template('seller/register.html')

@seller_bp.route('/reels', methods=['GET'])
@seller_required
def reels():
    seller_id = session['seller_id']
    all_reels = Reel.query.filter_by(seller_id=seller_id).order_by(Reel.created_at.desc()).all()
    return render_template('seller/reels.html', reels=all_reels)

@seller_bp.route('/reels/add', methods=['GET', 'POST'])
@seller_required
def add_reel():
    seller_id = session['seller_id']
    products = Product.query.filter_by(seller_id=seller_id).all()
    
    if request.method == 'POST':
        caption = request.form.get('caption')
        product_id = request.form.get('product_id')
        
        if 'video' in request.files:
            file = request.files['video']
            if file and file.filename and allowed_video(file.filename):
                os.makedirs(REELS_FOLDER, exist_ok=True)
                filename = secure_filename(file.filename)
                # Add timestamp to avoid duplicates
                filename = f"{int(datetime.utcnow().timestamp())}_{filename}"
                file.save(os.path.join(REELS_FOLDER, filename))
                
                reel = Reel(seller_id=seller_id, 
                            video=filename, 
                            caption=caption,
                            product_id=int(product_id) if product_id and product_id != 'none' else None)
                db.session.add(reel)
                db.session.commit()
                flash('Reel uploaded successfully!', 'success')
                return redirect(url_for('seller.reels'))
        flash('Invalid video file.', 'danger')
    return render_template('seller/add_reel.html', products=products)

@seller_bp.route('/reels/delete/<int:reel_id>', methods=['POST'])
@seller_required
def delete_reel(reel_id):
    reel = Reel.query.get_or_404(reel_id)
    if reel.seller_id == session['seller_id']:
        # Delete file
        try:
            video_path = os.path.join(REELS_FOLDER, reel.video)
            if os.path.exists(video_path):
                os.remove(video_path)
        except Exception as e:
            print(f"Error deleting reel file: {e}")
            
        db.session.delete(reel)
        db.session.commit()
        flash('Reel deleted successfully.', 'success')
    else:
        flash('Unauthorized action.', 'danger')
    return redirect(url_for('seller.reels'))

@seller_bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out.', 'info')
    return redirect(url_for('user.index'))
