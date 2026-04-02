from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    profile_image = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def initial_avatar(self):
        return self.name[0].upper() if self.name else "?"

    @property
    def avatar_color(self):
        colors = ['#d4af37', '#c5a02e', '#b69125', '#a7821c', '#987313']
        return colors[self.user_id % len(colors)]
    
    orders = db.relationship('Order', backref='user', lazy=True)
    wishlist = db.relationship('Wishlist', backref='user', lazy=True)
    cart = db.relationship('Cart', backref='user', lazy=True)
    reviews = db.relationship('Review', backref='user', lazy=True)
    recently_viewed = db.relationship('RecentlyViewed', backref='user', lazy=True)
    addresses = db.relationship('Address', backref='user', lazy=True)

class Seller(db.Model):
    __tablename__ = 'sellers'
    seller_id = db.Column(db.Integer, primary_key=True)
    shop_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), default='pending') # pending, approved, disabled
    logo = db.Column(db.String(255))
    banner = db.Column(db.String(255))
    bio = db.Column(db.Text)
    rating = db.Column(db.Numeric(3, 2), default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def initial_avatar(self):
        return self.shop_name[0].upper() if self.shop_name else "?"

    @property
    def avatar_color(self):
        colors = ['#d4af37', '#c5a02e', '#b69125', '#a7821c', '#987313']
        return colors[self.seller_id % len(colors)]
    
    products = db.relationship('Product', backref='seller', lazy=True)
    reels = db.relationship('Reel', backref='seller', lazy=True)

class Category(db.Model):
    __tablename__ = 'categories'
    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(100), unique=True, nullable=False)
    image = db.Column(db.String(255)) # For icon grid
    
    products = db.relationship('Product', backref='category', lazy=True)

class Product(db.Model):
    __tablename__ = 'products'
    product_id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('sellers.seller_id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id'), nullable=False)
    stock = db.Column(db.Integer, default=0)
    image = db.Column(db.String(255)) # Main image
    is_flash_deal = db.Column(db.Boolean, default=False)
    deal_price = db.Column(db.Numeric(10, 2))
    deal_expiry = db.Column(db.DateTime)
    is_featured = db.Column(db.Boolean, default=False)
    is_trending = db.Column(db.Boolean, default=False)
    view_count = db.Column(db.Integer, default=0)
    avg_rating = db.Column(db.Numeric(3, 2), default=0.0)
    
    # Jewellery specific metadata
    materials = db.Column(db.String(255))
    weight = db.Column(db.String(50))
    occasion = db.Column(db.String(100))
    warranty = db.Column(db.String(100))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def is_new(self):
        delta = datetime.utcnow() - self.created_at
        return delta.days <= 4

    images = db.relationship('ProductImage', backref='product', lazy=True)
    order_items = db.relationship('OrderItem', backref='product', lazy=True)
    reviews = db.relationship('Review', backref='product', lazy=True)
    wishlist_items = db.relationship('Wishlist', backref='product', lazy=True)
    cart_items = db.relationship('Cart', backref='product', lazy=True)

class ProductImage(db.Model):
    __tablename__ = 'product_images'
    image_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)
    image_filename = db.Column(db.String(255), nullable=False)

class Order(db.Model):
    __tablename__ = 'orders'
    order_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(50), default='pending') # pending, processing, shipped, delivered, cancelled
    
    # Shipping Details
    shipping_name = db.Column(db.String(100))
    shipping_phone = db.Column(db.String(20))
    shipping_address = db.Column(db.Text)
    payment_method = db.Column(db.String(50))
    upi_id = db.Column(db.String(100))
    payment_status = db.Column(db.String(50), default='pending') # pending, paid, failed
    
    subtotal = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    shipping_fee = db.Column(db.Numeric(10, 2), default=0.00)
    tax = db.Column(db.Numeric(10, 2), default=0.00)
    discount_amount = db.Column(db.Numeric(10, 2), default=0.00)
    coupon_id = db.Column(db.Integer, db.ForeignKey('coupons.coupon_id'), nullable=True)
    gift_card_id = db.Column(db.Integer, db.ForeignKey('gift_cards.card_id'), nullable=True)
    total_admin_commission = db.Column(db.Numeric(10, 2), default=0.00)
    total_seller_profit = db.Column(db.Numeric(10, 2), default=0.00)
    refund_amount = db.Column(db.Numeric(10, 2), default=0.00)
    refund_status = db.Column(db.String(50), default='na') # na, pending, processing, completed
    cancel_reason = db.Column(db.String(255))
    cancel_date = db.Column(db.DateTime)
    order_notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    items = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    order_item_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_time = db.Column(db.Numeric(10, 2), nullable=False)
    admin_commission = db.Column(db.Numeric(10, 2), default=0.00)
    seller_profit = db.Column(db.Numeric(10, 2), default=0.00)

class Wishlist(db.Model):
    __tablename__ = 'wishlist'
    wishlist_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Cart(db.Model):
    __tablename__ = 'cart'
    cart_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    is_saved_for_later = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Review(db.Model):
    __tablename__ = 'reviews'
    review_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False) # 1-5 scale
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Reel(db.Model):
    __tablename__ = 'reels'
    reel_id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('sellers.seller_id'), nullable=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=True) # Link to product
    video = db.Column(db.String(255), nullable=False)
    caption = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Product relationship (Product model doesn't have 'reels' property yet)
    product = db.relationship('Product', backref='reels', lazy=True)
    likes = db.relationship('ReelLike', backref='reel', lazy=True)
    comments = db.relationship('ReelComment', backref='reel', lazy=True, cascade="all, delete-orphan")

class ReelLike(db.Model):
    __tablename__ = 'reel_likes'
    like_id = db.Column(db.Integer, primary_key=True)
    reel_id = db.Column(db.Integer, db.ForeignKey('reels.reel_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ReelComment(db.Model):
    __tablename__ = 'reel_comments'
    comment_id = db.Column(db.Integer, primary_key=True)
    reel_id = db.Column(db.Integer, db.ForeignKey('reels.reel_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='reel_comments', lazy=True)

class Banner(db.Model):
    __tablename__ = 'banners'
    banner_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    subtitle = db.Column(db.String(200))
    image = db.Column(db.String(255), nullable=False)
    link = db.Column(db.String(255)) # URL to redirect to
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Newsletter(db.Model):
    __tablename__ = 'newsletter'
    subscriber_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class RecentlyViewed(db.Model):
    __tablename__ = 'recently_viewed'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)
    viewed_at = db.Column(db.DateTime, default=datetime.utcnow)

class Address(db.Model):
    __tablename__ = 'addresses'
    address_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    full_address = db.Column(db.Text, nullable=False)
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Coupon(db.Model):
    __tablename__ = 'coupons'
    coupon_id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    discount_type = db.Column(db.String(20), nullable=False) # 'percent' or 'fixed'
    discount_value = db.Column(db.Numeric(10, 2), nullable=False)
    min_purchase = db.Column(db.Numeric(10, 2), default=0.00)
    expiry_date = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class GiftCard(db.Model):
    __tablename__ = 'gift_cards'
    card_id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    balance = db.Column(db.Numeric(10, 2), nullable=False)
    expiry_date = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

