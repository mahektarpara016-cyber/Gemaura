from app import create_app
from database.models import db, Product

def update_batch_5():
    app = create_app()
    with app.app_context():
        # Mapping filename to (Name, Category_ID, Price, Description)
        # Category IDs: 1: Rings, 2: Necklaces, 3: Bracelets, 4: Earrings, 5: Bangles, 6: Bridal Jewellery, 7: Others
        updates = {
            '81.jpg': ("Crimson Flora Pendant", 2, 12000.0, "A delicate gold chain featuring a beautiful red-petal flower pendant with a sparkling white center."),
            '82.jpg': ("Infinity Sparkle Rose Gold Ring", 1, 15000.0, "An elegant rose gold ring with delicate diamond accents on a modern bypass band design."),
            '83.jpg': ("Deep Sea & Snow Bangle", 5, 18000.0, "A striking silver open-end bangle featuring contrasting blue and white pear-shaped gemstones."),
            '84.jpg': ("Celestial Solitaire Necklace", 2, 28000.0, "A refined silver chain with a brilliant round diamond pendant and smaller diamond accents along the chain."),
            '85.jpg': ("Double Radiance Drop Pendant", 2, 45000.0, "A sophisticated silver necklace featuring a dual-stone drop with a square and a pear-shaped diamond."),
            '86.jpg': ("Ruby Teardrop Elegance", 2, 32000.0, "A luxurious gold chain featuring a vibrant ruby teardrop pendant suspended from a diamond-set bar."),
            '87.jpg': ("Petite Sapphire Silver Bangle", 5, 9500.0, "A sleek and minimalist thin silver bangle with a small, perfectly centered blue sapphire."),
            '88.jpg': ("Ruby Blossom Jewelry Set", 2, 25000.0, "A charming silver jewelry suite featuring a ruby flower pendant and matching stud earrings."),
            '89.jpg': ("Love & Infinity Rose Bangle", 5, 22000.0, "A romantic rose gold bangle with a heart-and-infinity motif encrusted with radiant diamonds."),
            '90.jpg': ("Classic Sapphire Rose Pendant", 2, 16000.0, "A timeless rose gold necklace featuring a stunning oval blue sapphire in a secure four-prong setting."),
            '91.jpg': ("Emerald Deco Silver Ring", 1, 24000.0, "A vintage-inspired silver ring with a bold rectangular emerald center and a diamond-encrusted band."),
            '92.jpg': ("Celestial Hoop Dangles", 4, 18000.0, "Playful rose gold hoop earrings accented with diamond-set star and circle charms."),
            '93.jpg': ("Emerald Garden Choker", 2, 75000.0, "An exquisite gold choker featuring a series of lush emerald and diamond circular links."),
            '94.jpg': ("Golden C-Script Diamond Pendant", 2, 11000.0, "A minimalist gold chain featuring a brilliant round diamond nestled in a graceful C-shaped setting."),
            '95.jpg': ("Sapphire Trio Orbit Ring", 1, 14000.0, "A unique gold ring featuring three small sapphires arranged in a delicate circular orbit."),
            '96.jpg': ("Regal Ruby Suite", 2, 55000.0, "A high-jewelry rose gold suite featuring a rectangular ruby pendant and matching earrings."),
            '97.jpg': ("Verdant Bypass Ring", 1, 26000.0, "A vibrant rose gold bypass ring featuring a brilliant oval-cut emerald."),
            '98.jpg': ("Emerald Empress Frame Pendant", 2, 42000.0, "A regal gold chain featuring a rectangular emerald framed by a halo of sparkling diamonds.")
        }

        count = 0
        for filename, (name, cat_id, price, desc) in updates.items():
            product = Product.query.filter(Product.image.contains(filename)).first()
            if product:
                product.name = name
                product.category_id = cat_id
                product.price = price
                product.description = desc
                count += 1
        
        db.session.commit()
        print(f"Successfully updated {count} products in Batch 5.")

if __name__ == "__main__":
    update_batch_5()
