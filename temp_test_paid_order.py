from app import create_app
from database.models import db, Order, OrderItem, Product, User
from datetime import datetime

app = create_app()
with app.app_context():
    # Get the admin user (id=1 typically or searching by email)
    user = User.query.filter_by(email='admin@gemaura.com').first()
    if not user:
        print("User not found")
        exit()
        
    # Get a random product
    product = Product.query.first()
    if not product:
        print("Product not found")
        exit()
        
    # Create a test PAID order
    test_order = Order(
        user_id=user.user_id,
        total_price=81370.00,
        subtotal=81370.00,
        status='pending',
        payment_method='UPI',
        payment_status='Paid (Simulation)',
        shipping_name=user.name,
        shipping_address='Luxurious Villa, Mumbai',
        shipping_phone='9876543210',
        created_at=datetime.utcnow()
    )
    db.session.add(test_order)
    db.session.flush()
    
    item = OrderItem(
        order_id=test_order.order_id,
        product_id=product.product_id,
        quantity=1,
        price_at_time=81370.00,
        seller_profit=73233.00,
        admin_commission=8137.00
    )
    db.session.add(item)
    
    test_order.total_admin_commission = 8137.00
    test_order.total_seller_profit = 73233.00
    
    db.session.commit()
    print(f"Test Paid Order created: #GEM-{test_order.order_id}")
