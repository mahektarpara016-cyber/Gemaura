import os
from datetime import datetime, timedelta
from app import create_app, db
from database.models import db, Category, User, Seller, Product, Banner, ProductImage, RecentlyViewed
from werkzeug.security import generate_password_hash

def init_db():
    app = create_app()
    with app.app_context():
        # Drop and Recreate tables for new schema
        print("Dropping all tables...")
        db.drop_all()
        print("Creating all tables...")
        db.create_all()
        
        # Add Categories with images for grid
        categories_data = [
            ('Rings', 'https://images.unsplash.com/photo-1605100804763-247f67b3557e?auto=format&fit=crop&w=400&q=80'),
            ('Necklaces', 'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?auto=format&fit=crop&w=400&q=80'),
            ('Bracelets', 'https://images.unsplash.com/photo-1611591437281-460bfbe1220a?auto=format&fit=crop&w=400&q=80'),
            ('Earrings', 'https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?auto=format&fit=crop&w=400&q=80'),
            ('Bangles', 'https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?auto=format&fit=crop&w=400&q=80'),
            ('Bridal Jewellery', 'https://images.unsplash.com/photo-1583939003579-730e3918a45a?auto=format&fit=crop&w=400&q=80')
        ]
        for cat_name, img in categories_data:
            if not Category.query.filter_by(category_name=cat_name).first():
                db.session.add(Category(category_name=cat_name, image=img))
        
        # Add a demo seller with shop details
        if not Seller.query.filter_by(email='seller@demo.com').first():
            demo_seller = Seller(
                shop_name="Radha Jewels",
                email="seller@demo.com",
                password=generate_password_hash('seller123'),
                status='approved',
                logo='seller_logo.png',
                banner='seller_banner.jpg',
                bio="Exquisite handcrafted jewellery since 1995.",
                rating=4.8
            )
            db.session.add(demo_seller)
            db.session.commit()

        # Add Banners
        banners = [
            Banner(title="Luxury Meets Elegance", subtitle="Exclusive gold collection now live.", image="banner1.jpg", link="/shop"),
            Banner(title="Wedding Special", subtitle="Discover the perfect bridal sets.", image="banner2.jpg", link="/shop?category=2"),
            Banner(title="New Arrivals", subtitle="The latest trends in diamond couture.", image="banner3.jpg", link="/shop")
        ]
        db.session.add_all(banners)
        
        # Seed Products
        # Seed Products
        seller = Seller.query.filter_by(email='seller@demo.com').first()
        if seller:
            cat_rings = Category.query.filter_by(category_name='Rings').first()
            cat_necklaces = Category.query.filter_by(category_name='Necklaces').first()
            cat_bracelets = Category.query.filter_by(category_name='Bracelets').first()
            cat_earrings = Category.query.filter_by(category_name='Earrings').first()
            cat_bangles = Category.query.filter_by(category_name='Bangles').first()
            cat_bridal = Category.query.filter_by(category_name='Bridal Jewellery').first()

            products = [
                Product(name='Eternal Gold Ring', description='Solid 22k gold ring with small diamond.', price=12000, category_id=cat_rings.category_id, seller_id=seller.seller_id, stock=10, image='ring1.jpg', is_featured=True, materials='22K Gold, 0.05ct Diamond', weight='4.5g', occasion='Daily Wear', warranty='Lifetime Polish', created_at=datetime.utcnow()),
                Product(name='Heart Necklace', description='Pearl necklace with heart pendant.', price=4500, category_id=cat_necklaces.category_id, seller_id=seller.seller_id, stock=5, image='neck1.jpg', is_flash_deal=True, deal_price=3999, materials='Freshwater Pearl, 18K Gold Plated', weight='12g', occasion='Special Occasion', warranty='6 Months', created_at=datetime.utcnow() - timedelta(days=2)),
                Product(name='Diamond Studs', description='Brilliant cut 0.5ct diamond earrings.', price=25000, category_id=cat_earrings.category_id, seller_id=seller.seller_id, stock=3, image='ear1.jpg', is_featured=True, is_trending=True, materials='18K White Gold, 0.5ct Diamond', weight='2.8g', occasion='Gift', warranty='1 Year International', created_at=datetime.utcnow() - timedelta(days=5)),
                Product(name='Royal Choker', description='Grand kundan choker set.', price=85000, category_id=cat_necklaces.category_id, seller_id=seller.seller_id, stock=2, image='neck2.jpg', is_trending=True, materials='Gold Plated Brass, Kundan, Pearls', weight='120g', occasion='Bridal', warranty='1 Year', created_at=datetime.utcnow() - timedelta(days=10)),
                Product(name='Gold Kada', description='Traditional 22k gold bangle/bracelelt.', price=55000, category_id=cat_bracelets.category_id, seller_id=seller.seller_id, stock=4, image='brace1.jpg', is_featured=True, materials='22K Hallmarked Gold', weight='18g', occasion='Traditional', warranty='Lifetime Polish', created_at=datetime.utcnow()),
                Product(name='Antique Bangles Set', description='Set of 4 antique finish gold plated bangles.', price=8500, category_id=cat_bangles.category_id, seller_id=seller.seller_id, stock=8, image='brace2.jpg', materials='Copper Mix, Gold Polish', weight='60g', occasion='Festive', warranty='6 Months', created_at=datetime.utcnow() - timedelta(days=3)),
                Product(name='Victorian Bridal Set', description='Full bridal set with necklace, earrings, and maang tikka.', price=150000, category_id=cat_bridal.category_id, seller_id=seller.seller_id, stock=1, image='bridal1.jpg', is_featured=True, is_trending=True, materials='18K Gold, Polki, Rubies', weight='250g', occasion='Wedding', warranty='2 Years', created_at=datetime.utcnow() - timedelta(days=1))
            ]
            db.session.add_all(products)

        db.session.commit()
        print("Database fully reset and Luxury seed data added!")

if __name__ == "__main__":
    init_db()

