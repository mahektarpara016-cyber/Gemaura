from app import create_app
from database.models import db, Seller

app = create_app()
with app.app_context():
    sellers = Seller.query.all()
    print(f"Total Sellers: {len(sellers)}")
    for s in sellers:
        print(f"ID: {s.seller_id} | Shop: {s.shop_name} | Email: {s.email} | Status: {s.status}")
