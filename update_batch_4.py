from app import create_app
from database.models import db, Product

def update_batch_4():
    app = create_app()
    with app.app_context():
        # Mapping filename to (Name, Category_ID, Price, Description)
        # Category IDs: 1: Rings, 2: Necklaces, 3: Bracelets, 4: Earrings, 5: Bangles, 6: Bridal Jewellery, 7: Others
        updates = {
            '61.jpg': ("Emerald Drop Halo Necklace", 2, 55000.0, "A stunning silver chain featuring a vivid emerald teardrop pendant surrounded by a shimmering diamond halo."),
            '62.jpg': ("Petite Sapphire Solitaire", 2, 8500.0, "A minimalist gold chain with a delicate round blue sapphire solitaire, perfect for everyday elegance."),
            '63.jpg': ("Meadow Whisper Diamond Ring", 1, 12000.0, "A charming rose gold ring featuring a small, intricate diamond floral cluster inspired by spring meadows."),
            '64.jpg': ("Ruby Infinity Rose Bangle", 5, 45000.0, "An elegant rose gold bangle with a central ruby and two diamond-encrusted pear-shaped side accents."),
            '65.jpg': ("Azure Crystal Bead Bracelet", 3, 3500.0, "A delicate silver beaded bracelet featuring five diamond-shaped light blue crystals for a touch of color."),
            '66.jpg': ("Geometric Glamour Charm Bracelet", 3, 18000.0, "A modern silver chain bracelet with multiple geometric charms encrusted with radiant diamonds."),
            '67.jpg': ("Sapphire Heart Rose Gold Pendant", 2, 22000.0, "A romantic rose gold necklace featuring a heart-shaped blue sapphire in a secure bezel setting."),
            '68.jpg': ("Ethereal Butterfly Enamel Bangle", 5, 35000.0, "A unique gold bangle with a beautiful blue-green enamel butterfly and a marquise diamond center."),
            '69.jpg': ("Silver Floral Lace Studs", 4, 6500.0, "Exquisite silver flower-shaped stud earrings with intricate openwork and bright diamond centers."),
            '70.jpg': ("Verdant Circle Motif Bangle", 5, 28000.0, "A chic rose gold bangle featuring a central diamond-set circle with a delicate emerald accent."),
            '71.jpg': ("Lucky Clover Diamond Bangle", 5, 32000.0, "A sophisticated gold bangle featuring a central four-leaf clover motif encrusted with brilliant diamonds."),
            '72.jpg': ("Regal Sapphire Deco Pendant", 2, 48000.0, "A vintage-inspired silver chain with a rectangular emerald-cut blue sapphire and a diamond halo."),
            '73.jpg': ("Blossom Silver Bangle", 5, 15000.0, "A graceful silver bangle featuring a central flower motif set with a delicate pink gemstone."),
            '74.jpg': ("Emerald Twin Leaf Bangle", 5, 42000.0, "A luxurious gold bypass bangle featuring two vibrant pear-shaped emeralds resembling twin leaves."),
            '75.jpg': ("Ruby Rose Bud Ring", 1, 65000.0, "A masterpiece rose gold ring with a large ruby center and green gemstone leaf accents on the bypass shank."),
            '76.jpg': ("Teal Enchantment Leaf Ring", 1, 38000.0, "A rose gold ring featuring a round teal sapphire and multiple diamond-encrusted leaves along the band."),
            '77.jpg': ("Sapphire Cascade Tennis Necklace", 2, 85000.0, "An opulent silver tennis necklace culminating in a majestic pear-shaped blue sapphire drop."),
            '78.jpg': ("Golden Vortex Diamond Pendant", 2, 14000.0, "A striking gold chain with a dynamic spiral swirl pendant accented with a central brilliant diamond."),
            '79.jpg': ("Eternal Bond Rose Bangle", 5, 26000.0, "A romantic rose gold bangle featuring two interlocking circles, one detailed with shimmering diamonds."),
            '80.jpg': ("Ruby Commander Lux Bracelet", 3, 120000.0, "A heavy gold chain bracelet featuring a central bar of channel-set rubies and diamond halos.")
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
        print(f"Successfully updated {count} products in Batch 4.")

if __name__ == "__main__":
    update_batch_4()
