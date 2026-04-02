from app import create_app
from database.models import db, Reel, Seller

app = create_app()
with app.app_context():
    seller = Seller.query.first()
    if seller:
        reels_data = [
            {'video': '1.mp4', 'caption': 'Exquisite Diamond Choker Reveal 💎 #Luxury #Gemaura'},
            {'video': '2.mp4', 'caption': 'The Art of Gold Craftsmanship ✨ #Handmade #Jewellery'},
            {'video': '3.mp4', 'caption': 'Perfect Bridal Set for your big day 🤵👰 #BridalJewellery'},
            {'video': '4.mp4', 'caption': 'Sparkle like never before with our new Diamond Collection 💍'},
            {'video': '5.mp4', 'caption': 'Legacy in every detail. Discover Gemaura Heritage.'}
        ]
        
        for r in reels_data:
            if not Reel.query.filter_by(video=r['video']).first():
                reel = Reel(seller_id=seller.seller_id, video=r['video'], caption=r['caption'])
                db.session.add(reel)
        
        db.session.commit()
        print("Reels seeded successfully.")
    else:
        print("No seller found to associate with reels.")
