from app import create_app
from database.models import db, User, Product, Category, Reel, Banner

app = create_app()

def audit():
    with app.app_context():
        print("=== GEMAURA DATABASE AUDIT (Fixed) ===")
        
        # 1. Users
        print(f"Users: {User.query.count()}")
        
        # 2. Categories
        print(f"Categories: {Category.query.count()}")
        for c in Category.query.all():
            print(f" - {c.category_name} (ID: {c.category_id})")
        
        # 3. Products
        print(f"Products: {Product.query.count()}")
        
        # 4. Reels
        print(f"Reels: {Reel.query.count()}")
        
        # 5. Banners
        print(f"Banners: {Banner.query.count()}")
        
        print("\n=== AUDIT COMPLETE ===")

if __name__ == "__main__":
    audit()
