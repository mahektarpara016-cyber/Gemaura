from app import create_app
from database.models import db, Product

def update_batch_2():
    app = create_app()
    with app.app_context():
        # Mapping filename to (Name, Category_ID, Price, Description)
        # Category IDs: 1: Rings, 2: Necklaces, 3: Bracelets, 4: Earrings, 5: Bangles, 6: Bridal Jewellery, 7: Others
        updates = {
            '18.jpg': ("Midnight Sapphire Studs", 4, 25000.0, "Square-cut deep blue sapphires set in a radiant diamond sunburst, offering a bold yet sophisticated look."),
            '19.jpg': ("Golden Blossom Necklace", 2, 14000.0, "A delicate rose gold vine chain featuring a pure white flower charm, perfect for feminine and everyday elegance."),
            '20.jpg': ("Delicate Ruby Choker", 2, 9500.0, "A minimalist gold thread chain with a tiny, vibrant ruby heart, designed for a subtle romantic touch."),
            '21.jpg': ("Sunlit Bloom Pendant", 2, 12000.0, "A radiant gold flower pendant with a shimmering diamond center, capturing the essence of a sunny day."),
            '22.jpg': ("Sunlit Bloom Pendant", 2, 12000.0, "A radiant gold flower pendant with a shimmering diamond center, capturing the essence of a sunny day."),
            '23.jpg': ("Regal Emerald Gala", 6, 150000.0, "A grand statement necklace featuring cascading diamonds and a magnificent emerald centerpiece, designed for high-profile events."),
            '24.jpg': ("Lush Emerald Gold Studs", 4, 18000.0, "Classic emerald-cut green gemstones set in rich 22K gold, combining traditional charm with modern simplicity."),
            '25.jpg': ("Ruby Square Bracelet", 3, 45000.0, "A bold silver link bracelet featuring a series of vibrant square-cut rubies, each framed by a shimmering halo of diamonds."),
            '26.jpg': ("Sapphire-Tip Gold Cuff", 3, 22000.0, "A contemporary open gold cuff with two brilliant blue sapphire tips, offering a chic and minimalist aesthetic."),
            '27.jpg': ("Azure Dream Oval Bracelet", 3, 55000.0, "An elegant silver tennis bracelet featuring a row of oval-cut blue sapphires, accented with brilliant marquise diamonds."),
            '28.jpg': ("Grand Estate Emerald", 6, 180000.0, "An opulent bridal necklace set with teardrop emeralds and layered diamond strands, the epitome of luxury."),
            '30.jpg': ("Verdant Teardrop Pendant", 2, 65000.0, "A luxurious rose gold chain holding a large, vivid emerald teardrop pendant surrounded by a double halo of diamonds."),
            '31.jpg': ("Ruby Teardrop Bracelet", 3, 38000.0, "A graceful silver chain bracelet featuring alternating ruby teardrops and diamond accents for a refined sparkle."),
            '32.jpg': ("Velvet Ruby Halo Studs", 4, 22000.0, "Deep red rubies encased in a brilliant diamond halo, these studs are a timeless addition to any fine jewellery collection."),
            '33.jpg': ("Blush Royale Banquet Set", 6, 220000.0, "A magnificent white gold necklace and earring set featuring rare pink teardrop gemstones and intricate floral diamond work."),
            '34.jpg': ("Crimson Eternity Choker", 2, 75000.0, "An enchanting silver choker featuring a continuous row of oval-cut rubies, perfect for an evening of luxury."),
            '35.jpg': ("Diamond Willow Bridal Set", 6, 350000.0, "An extraordinary masterpiece of white gold and diamonds, inspired by weeping willow leaves, designed for the ultimate bridal look."),
            '36.jpg': ("Twig & Marquise Ring", 1, 32000.0, "A unique branch-inspired gold band featuring a large marquise-cut diamond, blending nature's beauty with fine craftsmanship."),
            '37.jpg': ("Triple Dew Bracelet", 3, 18000.0, "A delicate rose gold chain featuring three small pear-cut diamond \"dew drops\", perfect for stacking."),
            '38.jpg': ("Sleek Gold Orbit Bangle", 5, 28000.0, "A highly polished 18K gold bangle with subtle diamond-set indentations, offering a modern and sleek profile."),
            '39.jpg': ("Pave-Set Glamour Hoops", 4, 45000.0, "Chunky silver hoop earrings fully encrusted with pavé-set diamonds for a bold and glamorous statement."),
            '40.jpg': ("Nature’s Deep Blue Ring", 1, 58000.0, "A stunning rose gold ring featuring a large teardrop sapphire nestled within a leaf-motif diamond setting.")
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
        print(f"Successfully updated {count} products in Batch 2.")

if __name__ == "__main__":
    update_batch_2()
