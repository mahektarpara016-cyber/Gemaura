import os
from sqlalchemy.pool import NullPool

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super_secret_gemaura_key_123'
    # For SQLite (local testing, no server needed):
    db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance', 'gemaura.db')
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # NullPool prevents stale connections after server restarts
    SQLALCHEMY_ENGINE_OPTIONS = {
        'poolclass': NullPool,
        'connect_args': {'check_same_thread': False}
    }
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100 MB max upload size
