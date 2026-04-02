from flask import Flask, render_template, session
from config import Config
from database.models import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # Import Blueprints
    from routes.user_routes import user_bp
    from routes.seller_routes import seller_bp
    from routes.admin_routes import admin_bp

    # Register Blueprints
    app.register_blueprint(user_bp)
    app.register_blueprint(seller_bp, url_prefix='/seller')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # Context Processor
    @app.context_processor
    def inject_globals():
        from database.models import User, Seller, Cart, Wishlist
        current_user = None
        current_seller = None
        nav_counts = {'cart': 0, 'wishlist': 0}
        role = session.get('role')
        user_id = session.get('user_id')

        if role in ['admin', 'user']:
            if user_id:
                current_user = User.query.get(user_id)
                if role == 'user':
                    try:
                        nav_counts['cart'] = Cart.query.filter_by(user_id=user_id, is_saved_for_later=False).count()
                        nav_counts['wishlist'] = Wishlist.query.filter_by(user_id=user_id).count()
                    except:
                        pass
        elif role == 'seller':
            seller_id = session.get('seller_id')
            if seller_id:
                current_seller = Seller.query.get(seller_id)
                current_user = current_seller

        return dict(current_user=current_user, current_seller=current_seller, nav_counts=nav_counts)

    # Static files (WhiteNoise)
    from whitenoise import WhiteNoise
    app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/', prefix='static/')

    @app.errorhandler(404)
    def page_not_found(e):
        return "404 Not Found", 404

    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()
        return f"500 Internal Server Error: {e}", 500

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)