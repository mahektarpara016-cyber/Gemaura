from app import create_app, db
from database.models import Product

def update_batch_1():
    app = create_app()
    with app.app_context():
        # Mapping: filename -> (Name, CategoryID, Price, Description)
        # Note: Prices are in INR (₹)
        updates = {
            '01.webp': ("Elegant Emerald Pendant", 2, 18000, "A sophisticated 18K gold chain featuring a radiant emerald-cut green gemstone, perfect for adding a touch of nature-inspired luxury to any outfit."),
            '03.webp': ("Ruby Blossom Earrings", 4, 35000, "Exquisite dangle earrings featuring ruby-red stones in a delicate floral-leaf gold setting, accented with brilliant white diamonds."),
            '04.webp': ("Sapphire Galaxy Bracelet", 3, 85000, "A breathtaking white gold tennis bracelet featuring deep blue sapphire rounds encircled by a shimmering halo of pavé diamonds."),
            '05.webp': ("Jeweled Hummingbird", 2, 22000, "A whimsical and artistic hummingbird pendant crafted in gold, adorned with vibrant ruby and diamond detailing for a joyful look."),
            '06.webp': ("Modern Twist Diamond Ring", 1, 15000, "An avant-garde open-wrap gold ring featuring two brilliant-cut diamonds, combining contemporary design with timeless elegance."),
            '07.webp': ("Radiant Ruby Mangalsutra", 2, 28000, "A beautiful fusion of tradition and luxury, this black-beaded gold chain features a centered ruby pendant surrounded by a diamond halo."),
            '08.webp': ("Blooming Ruby Bangle", 5, 42000, "A unique open gold bangle featuring delicate ruby 'buds' at either end, designed to be a subtle yet striking statement piece."),
            '09.webp': ("Ocean Tear Drop Earrings", 4, 12000, "Stunning blue teardrop crystals suspended from a diamond-studded silver setting, inspired by the serene beauty of the deep sea."),
            '112.jpg': ("Silver Glow Emerald", 2, 12000, "A minimalist silver chain featuring a dainty pear-cut emerald pendant, ideal for everyday luxury and effortless style."),
            '123.jpg': ("Geometric V-Band Ring", 1, 8000, "A sleek and modern V-shaped gold band, perfect for stacking or wearing alone as a bold geometric statement."),
            '15.jpg': ("Lucky Clover Bracelet", 3, 15000, "A charming gold chain bracelet featuring a four-leaf clover emerald charm, blending luck and luxury in one beautiful design."),
            '16.jpg': ("Azure Butterfly Bangle", 5, 9500, "A delicate silver bangle adorned with two radiant blue butterflies, capturing the essence of spring and transformation."),
            '17.jpg': ("Princess Pink Bracelet", 3, 11000, "A feminine and graceful silver chain bracelet featuring a centered pink sapphire for a soft, regal touch.")
        }

        count = 0
        for img, (name, cat_id, price, desc) in updates.items():
            product = Product.query.filter(Product.image == img).first()
            if product:
                product.name = name
                product.category_id = cat_id
                product.price = price
                product.description = desc
                count += 1
        
        db.session.commit()
        print(f"Successfully updated {count} products in Batch 1.")

if __name__ == "__main__":
    update_batch_1()
