from app import create_app
from database.models import db, Product

def update_batch_6():
    app = create_app()
    with app.app_context():
        # Mapping filename to (Name, Category_ID, Price, Description)
        # Category IDs: 1: Rings, 2: Necklaces, 3: Bracelets, 4: Earrings, 5: Bangles
        updates = {
            '112.jpg': ("Classic 22K Gold Band", 1, 18000.0, "A timeless, high-polish 22K gold band designed for lasting elegance and comfort."),
            '123.jpg': ("Emerald Halo Tear Pendant", 2, 22000.0, "A refined silver necklace featuring a lush teardrop emerald surrounded by a brilliant diamond halo."),
            'A0028_2_7a5bd132-a234-4460-a887-8a78500ddcce.webp': ("Chevron Sparkle Ring", 1, 12000.0, "A modern V-shaped gold ring accented with fine diamond pave for a subtle yet striking look."),
            'RE10NS410686_1.webp': ("Heart & Soul Infinity Anklet", 3, 8500.0, "A delicate rose gold heart-linked anklet featuring infinity charms representing eternal love."),
            'ey2.webp': ("Imperial Meenakari Choker Set", 2, 120000.0, "An ornate traditional choker set featuring exquisite meenakari work, emeralds, pearls, and matching jhumkas."),
            'image.avif': ("Golden Petal Stud Earrings", 4, 15000.0, "Exquisite gold flower stud earrings centered with brilliant diamonds for a fresh, botanical look."),
            'jew1102821-t_1.webp': ("Pearlescent Evening Drops", 4, 12000.0, "Elegant ivory pearl drop earrings with sophisticated gold accents, perfect for evening wear."),
            'jew1102871_1_.webp': ("Monarch Wing Ear Climber", 4, 18000.0, "A unique gold butterfly wing ear climber featuring intricate filigree and a modern silhouette."),
            'jew1103889-2-2.webp': ("Midnight Layered Pendant", 2, 24000.0, "A chic layered gold chain necklace featuring a striking black onyx-style stone and horizontal bar."),
            'jew1104338-2-2.webp': ("Modern Pearl & Cube Bracelet", 3, 14000.0, "A contemporary gold chain bracelet featuring organic pearls and polished geometric cubes."),
            'jew1105319-m1-1.webp': ("Victorian Pearl Cuff", 3, 35000.0, "An ornate multi-strand pearl cuff bracelet with a vintage-inspired gold filigree clasp."),
            'jew1108053-m1-1-1.jpg': ("Grand Pearl Strand Choker", 2, 65000.0, "A magnificent multi-strand pearl choker designed to make a statement at high-fashion occasions."),
            'jew1108557-m1-1.jpg': ("Artisan Statement Choker", 2, 48000.0, "A bold traditional choker with intricate floral embroidery, pearls, and vibrant semi-precious stones."),
            'jew1108960-1-1.webp': ("Heritage Jhumka Dangles", 4, 28000.0, "Traditional temple-style earrings featuring delicate pearls and colorful gemstone accents."),
            'jew97551062-1-1_1.webp': ("United Hearts Bangle", 5, 16000.0, "A romantic rose gold bangle featuring two interlocking hearts in a shimmering diamond pave setting."),
            'bangles.jpg': ("Signature Gold Bangle", 5, 25000.0, "A classic high-polish gold bangle, a cornerstone of our signature heritage collection."),
            'rings.jpg': ("Solitaire Promise Ring", 1, 35000.0, "A brilliant round-cut solitaire ring representing a lifetime of love and commitment."),
            'necklaces.jpg': ("Golden Eternity Chain", 2, 45000.0, "A continuous gold link necklace designed for a bold and modern aesthetic."),
            'bracelets.jpg': ("Radiant Link Bracelet", 3, 22000.0, "A high-shine gold link bracelet that seamlessly blends traditional craft with modern design."),
            'earrings.jpg': ("Diamond Radiance Studs", 4, 55000.0, "Hand-selected brilliant-cut diamond stud earrings for an unmatched sparkle."),
            '01.webp': ("Pearl Harmony Necklace", 2, 18000.0, "A modern pearl drop necklace suspended from a delicate polished silver chain."),
            '03.webp': ("Azure Sky Ring", 1, 14000.0, "A minimalist ring featuring a round, brilliant sky blue topaz in a clean silver setting."),
            '04.webp': ("Golden Wave Bangle", 5, 21000.0, "A beautifully textured gold bangle with a unique wave-patterned finish."),
            '05.webp': ("Ruby Star Earrings", 4, 9000.0, "Delicate star-shaped ruby studs that bring a touch of celestial magic to your style."),
            '06.webp': ("Emerald Leaf Pendant", 2, 15500.0, "A dainty gold leaf pendant set with a vibrant tiny emerald for a natural look."),
            '07.webp': ("Infinity Bond Bracelet", 3, 11000.0, "A polished silver infinity charm bracelet, the perfect symbol of eternal connection."),
            '08.webp': ("Sapphire Petal Studs", 4, 13000.0, "Feminine petal-shaped sapphire studs set in a warm rose gold mounting."),
            '09.webp': ("Minimalist Gold Torque", 2, 32000.0, "A sleek, open-style gold torque necklace for a sophisticated contemporary statement.")
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
        print(f"Successfully updated {count} products in Batch 6.")

if __name__ == "__main__":
    update_batch_6()
