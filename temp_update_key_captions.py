from app import create_app, db
from database.models import Product

def update_key_captions():
    app = create_app()
    with app.app_context():
        # Map of partial filename to (Name, Description)
        updates = {
            '12.jpg': ("Golden Swan Pearl Ring", "A masterpiece of elegance, this 22K gold ring is meticulously crafted in the shape of a graceful swan, accented with a shimmering natural pearl."),
            '13.jpg': ("Eternal Heart Emerald Ring", "Celebrate love with this delicate gold band featuring a vibrant heart-shaped emerald, flanked by brilliant-cut diamonds for a touch of royal sparkle."),
            '14.jpg': ("Teardrop Emerald Promise Ring", "A minimalist yet sophisticated design, showcasing a fine pear-cut emerald set on a slender gold band with a single diamond accent."),
            'brace1.jpg': ("Royal Diamond Solitaire", "A timeless classic, this ring features a majestic round-cut diamond solitaire held in a luxurious gold pave setting."),
            'ear1.jpg': ("Starlight Diamond Studs", "Radiant 1.0ct diamond studs set in 18K white gold, presented in our signature Aurelia luxury velvet gift box."),
            'neck1.jpg': ("Majestic Emerald Teardrop Necklace", "An opulent statement piece featuring a row of premium emeralds and diamonds, culminating in a grand teardrop emerald pendant surrounded by gold leaf motifs.")
        }

        count = 0
        for img_part, (name, desc) in updates.items():
            product = Product.query.filter(Product.image == img_part).first()
            if product:
                product.name = name
                product.description = desc
                count += 1
        
        db.session.commit()
        print(f"Successfully updated {count} key product captions.")

if __name__ == "__main__":
    update_key_captions()
