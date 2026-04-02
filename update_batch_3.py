from app import create_app
from database.models import db, Product

def update_batch_3():
    app = create_app()
    with app.app_context():
        # Mapping filename to (Name, Category_ID, Price, Description)
        # Category IDs: 1: Rings, 2: Necklaces, 3: Bracelets, 4: Earrings, 5: Bangles, 6: Bridal Jewellery, 7: Others
        updates = {
            '41.jpg': ("Silver Spirit Leaf Ring", 1, 4500.0, "A delicate silver adjustable leaf ring with shimmering diamond accents, perfect for nature lovers."),
            '42.jpg': ("Trio-Sapphire Silver Cuff", 3, 28000.0, "A sleek silver cuff bracelet featuring three flush-set brilliant blue sapphires for a modern touch."),
            '43.jpg': ("Rose Dew Diamond Dangles", 4, 35000.0, "Rose gold teardrop earrings featuring a large center diamond and a shimmering halo, inspired by morning dew."),
            '44.jpg': ("Royal Verdant Halo Ring", 1, 42000.0, "A majestic gold ring with an oval emerald and a brilliant diamond halo, featuring an elegant split shank."),
            '45.jpg': ("Ethereal Swirl Diamond Pendant", 2, 18000.0, "A silver drop pendant with a round diamond nestled in a graceful swirl setting, symbolizing eternal flow."),
            '46.jpg': ("Sapphire Horizon Bangle", 5, 22000.0, "A minimalist rose gold bangle featuring a single rectangular blue sapphire, reminiscent of the evening horizon."),
            '47.jpg': ("Crimson Banquet Dangles", 4, 55000.0, "Exquisite white gold drop earrings with large ruby-red stones and intricate floral diamond work."),
            '48.jpg': ("Midnight Star Sapphire Studs", 4, 25000.0, "Deep blue sapphires set in a radiant diamond starburst, offering a bold and celestial aesthetic."),
            '49.jpg': ("Autumn Gold Leaf Studs", 4, 12000.0, "Graceful gold leaf-shaped stud earrings with small diamond accents, capturing the essence of fall."),
            '50.jpg': ("Peony Frost Bolo Bracelet", 3, 32000.0, "A charming rose gold bolo bracelet featuring a floral diamond cluster, delicate and sophisticated."),
            '51.jpg': ("Majestic Emerald Halo Pendant", 2, 75000.0, "A grand silver chain with a large, vivid emerald teardrop pendant surrounded by a double halo of diamonds."),
            '52.jpg': ("Rose Blossom Heart Studs", 4, 15000.0, "Romantic rose gold heart-shaped stud earrings featuring a delicate rose motif and diamond accents."),
            '53.jpg': ("Sapphire Blue Solitaire Pendant", 2, 12000.0, "A minimalist silver chain with a crisp rectangular blue sapphire solitaire, the epitome of simple elegance."),
            '54.jpg': ("Ruby Glow Halo Pendant", 2, 9500.0, "A dainty gold chain with a vibrant round ruby pendant surrounded by a shimmering diamond halo."),
            '55.jpg': ("Triple Tier Gold Hoops", 4, 28000.0, "Sophisticated gold triple-hoop earrings with brilliant diamond accents on the central tier."),
            '56.jpg': ("Celestial Sapphire Teardrops", 4, 22000.0, "Silver stud earrings featuring a blue sapphire teardrop and a radiant half-halo of diamonds."),
            '57.jpg': ("Infinity Rose Gold Studs", 4, 14000.0, "Chic rose gold stud earrings with a symbolic double-ring infinity design and diamond accents."),
            '58.jpg': ("Diamond Starburst Halo Pendant", 2, 11000.0, "A silver cluster pendant with a central round diamond and a double halo for maximum brilliance."),
            '59.jpg': ("Eternal Love Ruby Bracelet", 3, 19000.0, "A graceful silver chain bracelet featuring multiple small rubies and a romantic heart-shaped ruby center."),
            '60.jpg': ("Azure Majesty Halo Pendant", 2, 65000.0, "A stunning silver chain with a large oval blue sapphire pendant showcased in a radiant diamond halo.")
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
        print(f"Successfully updated {count} products in Batch 3.")

if __name__ == "__main__":
    update_batch_3()
