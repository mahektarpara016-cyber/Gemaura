import os
import time
from app import create_app, db
from database.models import Product
import google.generativeai as genai

# --- CONFIGURATION ---
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE" # Get one from https://aistudio.google.com/
IMAGE_FOLDER = "static/uploads"
MODEL_NAME = "gemini-1.5-flash"

# Initialize Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(MODEL_NAME)

def generate_caption(image_path):
    """Sends image to Gemini and gets a (Name, Description) tuple."""
    try:
        # Load image
        with open(image_path, "rb") as f:
            image_data = f.read()
        
        # Prepare the prompt
        prompt = (
            "You are a professional luxury jewellery copywriter. "
            "Analyze this image and provide: "
            "1. A short, elegant Product Name (3-5 words). "
            "2. A sophisticated, seductive Description (20-40 words). "
            "Format the output exactly as: NAME: [Product Name] | DESC: [Description]"
        )

        # Generate content
        response = model.generate_content([prompt, {"mime_type": "image/jpeg", "data": image_data}])
        text = response.text.replace("\n", " ").strip()
        
        # Extract name and desc
        if "NAME:" in text and "| DESC:" in text:
            name = text.split("NAME:")[1].split("| DESC:")[0].strip()
            desc = text.split("| DESC:")[1].strip()
            return name, desc
        return None, None
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return None, None

def run_auto_caption():
    app = create_app()
    with app.app_context():
        # Get all products that have default names (e.g., "Luxury Rings 12")
        products = Product.query.filter(
            Product.name.like("Luxury%") | Product.description.like("Exquisite handcrafted%")
        ).all()

        print(f"Found {len(products)} products that need better captions.")
        
        if GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
            print("\n[!] Please put your Gemini API Key in the script to start automation.")
            return

        for product in products:
            img_path = os.path.join(IMAGE_FOLDER, product.image)
            if not os.path.exists(img_path):
                continue
            
            print(f"Captioning: {product.image}...")
            name, desc = generate_caption(img_path)
            
            if name and desc:
                product.name = name
                product.description = desc
                db.session.commit()
                print(f"  + Updated: {name}")
                # Be kind to API rate limits
                time.sleep(2) 
            else:
                print(f"  - Failed to generate caption for {product.image}")

if __name__ == "__main__":
    run_auto_caption()
