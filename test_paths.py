import os
import sys

# Mocking the environment to test path resolution
os.environ['DATABASE_URL'] = '' # Ensure we test the SQLite logic

from config import Config

def test_paths():
    print(f"OS Name: {os.name}")
    print(f"Base Dir: {Config.basedir}")
    print(f"DB URI: {Config.SQLALCHEMY_DATABASE_URI}")
    print(f"Upload Folder: {Config.UPLOAD_FOLDER}")

    # Test the directory creation logic from app.py
    db_path = Config.SQLALCHEMY_DATABASE_URI
    if db_path.startswith('sqlite:///'):
        actual_path = db_path.replace('sqlite://///', '/').replace('sqlite:///', '')
        db_dir = os.path.dirname(actual_path)
        print(f"Target DB Dir: {db_dir}")
        if db_dir and not os.path.exists(db_dir):
            print(f"WOULD CREATE DIR: {db_dir}")
        else:
            print(f"DIR EXISTS OR ROOT: {db_dir}")

if __name__ == "__main__":
    test_paths()
