from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from database.models import db, User, Seller, Product, Category, Order, OrderItem, Review, Reel
from sqlalchemy import func
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

admin_bp = Blueprint('admin', __name__)

ADMIN_EMAIL = 'admin@gemaura.com'
ADMIN_PASSWORD_HASH = generate_password_hash('admin123')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('Please log in as Admin to continue.', 'warning')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated

@admin_bp.route('/')
@admin_required
def dashboard():
    filter_type = request.args.get('filter', 'all')
    now = datetime.utcnow()
    
    query = Order.query
    if filter_type == 'today':
        query = query.filter(Order.created_at >= now.replace(hour=0, minute=0, second=0, microsecond=0))
    elif filter_type == 'week':
        query = query.filter(Order.created_at >= now - timedelta(days=7))
    elif filter_type == 'month':
        query = query.filter(Order.created_at >= now.replace(day=1, hour=0, minute=0, second=0, microsecond=0))
    
    total_users = User.query.count()
    total_sellers = Seller.query.count()
    total_orders = query.count()
    
    # Financial Stats
    orders = query.all()
    
    total_revenue = 0
    total_admin_profit = 0
    total_loss = 0
    
    for o in orders:
        if o.status.lower() != 'cancelled':
            total_revenue += float(o.total_price)
            total_admin_profit += float(o.total_admin_commission)
        else:
            # Avoid double counting: use refund_amount if present, otherwise total_price for paid-cancelled
            if o.refund_amount and o.refund_amount > 0:
                total_loss += float(o.refund_amount)
            elif o.payment_status.lower() in ['paid', 'paid (simulation)', 'completed']:
                total_loss += float(o.total_price)
                
            total_loss += float(o.discount_amount or 0)
    
    net_profit = float(total_admin_profit) - float(total_loss)
    
    # Recent Orders
    recent_orders = query.order_by(Order.created_at.desc()).limit(5).all()
    pending_sellers = Seller.query.filter_by(status='pending').all()
    
    # Chart Data: Daily Stats (Last 30 Days if month, else 7 days)
    days_limit = 30 if filter_type == 'month' else 7
    daily_stats = db.session.query(
        func.date(Order.created_at).label('date'),
        func.sum(Order.total_price).label('revenue'),
        func.sum(Order.total_admin_commission).label('profit'),
        func.sum(Order.refund_amount + Order.discount_amount).label('loss')
    ).group_by(func.date(Order.created_at)).order_by(func.date(Order.created_at).desc()).limit(days_limit).all()
    
    chart_labels = [str(s.date) for s in reversed(daily_stats)]
    chart_revenue = [float(s.revenue) for s in reversed(daily_stats)]
    chart_profit = [float(s.profit) for s in reversed(daily_stats)]
    chart_loss = [float(s.loss) for s in reversed(daily_stats)]
    
    # Top Products
    top_products = db.session.query(
        Product.name,
        func.sum(OrderItem.quantity).label('total_sold')
    ).join(OrderItem).group_by(Product.product_id).order_by(func.sum(OrderItem.quantity).desc()).limit(5).all()
    
    # Top Sellers
    top_sellers = db.session.query(
        Seller.shop_name,
        func.sum(OrderItem.price_at_time * OrderItem.quantity).label('total_sales')
    ).join(Product, Seller.seller_id == Product.seller_id)\
     .join(OrderItem, Product.product_id == OrderItem.product_id)\
     .group_by(Seller.seller_id).order_by(func.sum(OrderItem.price_at_time * OrderItem.quantity).desc()).limit(5).all()

    return render_template('admin/dashboard.html',
                           total_users=total_users, total_sellers=total_sellers,
                           total_orders=total_orders, total_revenue=total_revenue,
                           total_admin_profit=total_admin_profit, total_loss=total_loss,
                           net_profit=net_profit, filter_type=filter_type,
                           recent_orders=recent_orders, pending_sellers=pending_sellers,
                           chart_labels=chart_labels, chart_revenue=chart_revenue, 
                           chart_profit=chart_profit, chart_loss=chart_loss,
                           top_products=top_products, top_sellers=top_sellers)

# ---- Users ----
@admin_bp.route('/users')
@admin_required
def users():
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=all_users)

@admin_bp.route('/users/delete/<int:user_id>')
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted.', 'success')
    return redirect(url_for('admin.users'))

# ---- Sellers ----
@admin_bp.route('/sellers')
@admin_required
def sellers():
    all_sellers = Seller.query.order_by(Seller.created_at.desc()).all()
    return render_template('admin/sellers.html', sellers=all_sellers)

@admin_bp.route('/profile', methods=['GET', 'POST'])
@admin_required
def profile():
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'update_profile':
            user.name = request.form.get('name', user.name)
            
            if 'profile_image' in request.files:
                file = request.files['profile_image']
                if file and file.filename and allowed_file(file.filename):
                    upload_path = os.path.join(current_app.root_path, 'static/uploads/profiles')
                    os.makedirs(upload_path, exist_ok=True)
                    filename = secure_filename(f"admin_{user.user_id}_{file.filename}")
                    file.save(os.path.join(upload_path, filename))
                    user.profile_image = filename
            
            db.session.commit()
            session['name'] = user.name
            flash('Admin profile updated successfully!', 'success')
        elif action == 'remove_photo':
            user.profile_image = None
            db.session.commit()
            flash('Profile photo removed.', 'info')
        return redirect(url_for('admin.profile'))
    return render_template('admin/profile.html', user=user)

@admin_bp.route('/sellers/approve/<int:seller_id>')
@admin_required
def approve_seller(seller_id):
    seller = Seller.query.get_or_404(seller_id)
    seller.status = 'approved'
    db.session.commit()
    flash(f'{seller.shop_name} approved!', 'success')
    return redirect(url_for('admin.sellers'))

@admin_bp.route('/sellers/disable/<int:seller_id>')
@admin_required
def disable_seller(seller_id):
    seller = Seller.query.get_or_404(seller_id)
    seller.status = 'disabled'
    db.session.commit()
    flash(f'{seller.shop_name} disabled.', 'warning')
    return redirect(url_for('admin.sellers'))

@admin_bp.route('/sellers/delete/<int:seller_id>')
@admin_required
def delete_seller(seller_id):
    seller = Seller.query.get_or_404(seller_id)
    db.session.delete(seller)
    db.session.commit()
    flash('Seller deleted.', 'success')
    return redirect(url_for('admin.sellers'))

# ---- Categories ----
@admin_bp.route('/categories')
@admin_required
def categories():
    cats = Category.query.all()
    return render_template('admin/categories.html', categories=cats)

@admin_bp.route('/categories/add', methods=['POST'])
@admin_required
def add_category():
    name = request.form.get('name', '').strip()
    if name and not Category.query.filter_by(category_name=name).first():
        cat = Category(category_name=name)
        db.session.add(cat)
        db.session.commit()
        flash('Category added!', 'success')
    else:
        flash('Category already exists or invalid name.', 'danger')
    return redirect(url_for('admin.categories'))

@admin_bp.route('/categories/delete/<int:category_id>')
@admin_required
def delete_category(category_id):
    cat = Category.query.get_or_404(category_id)
    db.session.delete(cat)
    db.session.commit()
    flash('Category deleted.', 'success')
    return redirect(url_for('admin.categories'))

# ---- Products ----
@admin_bp.route('/products')
@admin_required
def products():
    prods = Product.query.order_by(Product.created_at.desc()).all()
    return render_template('admin/products.html', products=prods)

@admin_bp.route('/products/delete/<int:product_id>')
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted.', 'success')
    return redirect(url_for('admin.products'))

# ---- Orders ----
@admin_bp.route('/orders')
@admin_required
def orders():
    all_orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin/orders.html', orders=all_orders)

@admin_bp.route('/orders/update/<int:order_id>', methods=['POST'])
@admin_required
def update_order(order_id):
    order = Order.query.get_or_404(order_id)
    order.status = request.form.get('status', order.status)
    db.session.commit()
    flash('Order status updated!', 'success')
    return redirect(url_for('admin.orders'))

# ---- Reviews ----
@admin_bp.route('/reviews')
@admin_required
def reviews():
    all_reviews = Review.query.order_by(Review.created_at.desc()).all()
    return render_template('admin/reviews.html', reviews=all_reviews)

@admin_bp.route('/reviews/delete/<int:review_id>')
@admin_required
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)
    db.session.delete(review)
    db.session.commit()
    flash('Review deleted.', 'success')
    return redirect(url_for('admin.reviews'))

# ---- Reels ----
@admin_bp.route('/reels')
@admin_required
def reels():
    all_reels = Reel.query.order_by(Reel.created_at.desc()).all()
    return render_template('admin/reels.html', reels=all_reels)

@admin_bp.route('/reels/delete/<int:reel_id>')
@admin_required
def delete_reel(reel_id):
    reel = Reel.query.get_or_404(reel_id)
    # Delete file
    reels_path = os.path.join(current_app.root_path, 'static', 'reels')
    try:
        os.remove(os.path.join(reels_path, reel.video))
    except Exception:
        pass
    db.session.delete(reel)
    db.session.commit()
    flash('Reel deleted by admin.', 'success')
    return redirect(url_for('admin.reels'))

# ---- Auth ----
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'admin_id' in session:
        return redirect(url_for('admin.dashboard'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if email == ADMIN_EMAIL and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session.clear()
            # Ensure Admin User exists in DB for profile system
            admin_user = User.query.filter_by(email=ADMIN_EMAIL).first()
            if not admin_user:
                admin_user = User(name='Admin', email=ADMIN_EMAIL, password=ADMIN_PASSWORD_HASH)
                db.session.add(admin_user)
                db.session.commit()
            
            session['user_id'] = admin_user.user_id
            session['role'] = 'admin'
            session['name'] = admin_user.name
            flash('Welcome, Admin!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid credentials.', 'danger')
    return render_template('admin/login.html')

@admin_bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out.', 'info')
    return redirect(url_for('admin.login'))
