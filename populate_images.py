import os
from app import create_app, db
from database.models import Category, Seller, Product

def populate_images():
    app = create_app()
    with app.app_context():
        uploads_dir = os.path.join(app.root_path, 'static', 'uploads')
        if not os.path.exists(uploads_dir):
            print(f"Directory not found: {uploads_dir}")
            return

        # Get demo seller
        seller = Seller.query.filter_by(email='seller@demo.com').first()
        if not seller:
            print("Demo seller not found. Please run init_db.py first.")
            return

        # Get categories
        cat_map = {cat.category_name.lower(): cat.category_id for cat in Category.query.all()}
        
        # Mapping logic
        keywords = {
            'ring': 'Rings',
            'neck': 'Necklaces',
            'brace': 'Bracelets',
            'ear': 'Earrings',
            'bangl': 'Bangles'
        }

        # Fallback category if needed
        if 'others' not in cat_map:
            other_cat = Category(category_name='Others')
            db.session.add(other_cat)
            db.session.commit()
            cat_map['others'] = other_cat.category_id

        files = os.listdir(uploads_dir)
        extension_whitelist = {'.jpg', '.jpeg', '.png', '.webp', '.avif', '.jfif'}
        
        count = 0
        for filename in files:
            ext = os.path.splitext(filename)[1].lower()
            if ext not in extension_whitelist:
                continue
                
            # Check if product already exists with this image
            if Product.query.filter_by(image=filename).first():
                continue

            # Determine category
            category_id = cat_map['others']
            target_cat_name = "Jewellery"
            for key, val in keywords.items():
                if key in filename.lower():
                    category_id = cat_map.get(val.lower(), cat_map['others'])
                    target_cat_name = val
                    break
            
            # Create product
            name = filename.split('.')[0].replace('_', ' ').title()
            if len(name) < 3: # Handle simple numbered files
                name = f"Luxury {target_cat_name} {name}"
            
            description = f"Exquisite handcrafted {target_cat_name} featuring premium quality materials and timeless design."
            price = 15000 # Default price
            
            # Semi-randomize price based on category
            if target_cat_name == 'Rings': price = 12000
            elif target_cat_name == 'Necklaces': price = 45000
            elif target_cat_name == 'Earrings': price = 8000
            
            new_product = Product(
                name=name,
                description=description,
                price=price,
                category_id=category_id,
                seller_id=seller.seller_id,
                stock=10,
                image=filename,
                is_featured=False
            )
            db.session.add(new_product)
            count += 1
            
        db.session.commit()
        print(f"Successfully added {count} new products from uploads folder.")

if __name__ == "__main__":
    populate_images()
