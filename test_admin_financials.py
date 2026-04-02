from app import create_app
from database.models import db, Order
from flask import current_app

app = create_app()
with app.app_context():
    orders = Order.query.all()
    
    total_revenue = 0
    total_admin_profit = 0
    total_loss = 0
    
    for o in orders:
        if o.status.lower() != 'cancelled':
            total_revenue += float(o.total_price)
            total_admin_profit += float(o.total_admin_commission)
        else:
            if o.refund_amount and o.refund_amount > 0:
                total_loss += float(o.refund_amount)
            elif o.payment_status.lower() in ['paid', 'paid (simulation)', 'completed']:
                total_loss += float(o.total_price)
            # Only count discount as a separate loss for non-cancelled orders if it's not already factored
            # Actually, total_admin_profit is sum of commissions. Discounts usually reduce the base price.
            # Let's keep it simple: total_loss = (discounts on all orders) + (refunds/losses on cancelled)
            total_loss += float(o.discount_amount or 0)
        
    net_profit = float(total_admin_profit) - float(total_loss)
    
    print(f"Total Revenue (non-cancelled): {total_revenue}")
    print(f"Total Admin Profit: {total_admin_profit}")
    print(f"Total Loss: {total_loss}")
    print(f"Net Profit: {net_profit}")
