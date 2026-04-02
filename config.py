import os
from sqlalchemy.pool import NullPool

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super_secret_gemaura_key_123'

    # FIXED DATABASE PATH (no instance folder)
    basedir = os.path.abspath(os.path.dirname(__file__))
    
    # Support for DATABASE_URL environment variable (common in production like Render/Heroku)
    # Default to SQLite at the root directory
    _db_url = os.environ.get('DATABASE_URL')
    if _db_url:
        # Handle SQLAlchemy 1.4+ requirement for "postgresql://" instead of "postgres://"
        if _db_url.startswith("postgres://"):
            _db_url = _db_url.replace("postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = _db_url
    else:
        # Ensure SQLite path is formatted correctly for Linux (sqlite:////absolute/path)
        _db_path = os.path.join(basedir, "gemaura.db")
        if os.name == 'nt': # Windows
            SQLALCHEMY_DATABASE_URI = f"sqlite:///{_db_path}"
        else: # Linux/macOS
            # Standard absolute path URI for Linux is sqlite:////path/to/db
            SQLALCHEMY_DATABASE_URI = f"sqlite:///{_db_path}"



    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_ENGINE_OPTIONS = {
        'poolclass': NullPool,
        'connect_args': {'check_same_thread': False}
    }

    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024