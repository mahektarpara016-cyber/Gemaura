from app import create_app
from database.models import db, User, Product, Category, Reel

app = create_app()

def audit():
    with app.app_context():
        print("=== GEMAURA DATABASE AUDIT ===")
        
        # 1. Users Audit
        users = User.query.all()
        print(f"\n[Users] Total: {len(users)}")
        for u in users:
            role = 'Admin' if u.email == 'admin@gemaura.com' else 'User'
            print(f" - ID: {u.user_id} | Name: {u.name} | Email: {u.email} | Role: {role}")
        
        # 2. Categories Audit
        cats = Category.query.all()
        print(f"\n[Categories] Total: {len(cats)}")
        for c in cats:
            print(f" - ID: {c.category_id} | Name: {c.category_name} | Products: {len(c.products)}")
            
        # 3. Products Audit
        prods = Product.query.all()
        print(f"\n[Products] Total: {len(prods)}")
        flash_deals = Product.query.filter_by(is_flash_deal=True).count()
        print(f" - Flash Deals: {flash_deals}")
        
        # 4. Reels Audit
        reels = Reel.query.count()
        print(f"\n[Reels] Total: {reels}")
        
        print("\n=== AUDIT COMPLETE ===")

if __name__ == "__main__":
    audit()
