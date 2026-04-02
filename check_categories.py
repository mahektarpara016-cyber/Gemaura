from app import create_app
from database.models import Category

app = create_app()
with app.app_context():
    categories = Category.query.all()
    for c in categories:
        print(f"{c.category_id}: {c.category_name}")
