import os
from flask import Flask
from config import Config
from database.models import db, Product, Category

def audit_images():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    with app.app_context():
        print("--- Auditing Products ---")
        products = Product.query.all()
        uploads_dir = app.config['UPLOAD_FOLDER']
        
        missing_count = 0
        total_count = len(products)
        
        for p in products:
            if not p.image:
                continue
                
            img_path = os.path.join(uploads_dir, p.image)
            if not os.path.exists(img_path):
                print(f"❌ Missing: Product {p.product_id} ('{p.name}') expects '{p.image}'")
                missing_count += 1
            else:
                # print(f"✅ Found: {p.image}")
                pass
        
        print(f"\nSummary: {missing_count}/{total_count} product images missing from '{uploads_dir}'")
        
        print("\n--- Auditing Categories ---")
        cats = Category.query.all()
        for c in cats:
            if c.image:
                img_path = os.path.join(uploads_dir, c.image)
                if not os.path.exists(img_path):
                    print(f"❌ Missing: Category '{c.category_name}' expects '{c.image}'")

if __name__ == "__main__":
    audit_images()
