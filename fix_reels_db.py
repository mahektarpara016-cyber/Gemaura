import sys
import os

# Add the project root to sys.path
sys.path.append(os.getcwd())

from flask import Flask
from app import app
from database.models import db, Reel

def fix_reels_filenames():
    with app.app_context():
        reels = Reel.query.all()
        actual_files = os.listdir(os.path.join('static', 'reels'))
        
        print(f"Found {len(reels)} reels in DB and {len(actual_files)} files in static/reels")
        
        for reel in reels:
            old_name = reel.video
            # If the filename is not in actual_files, try to find a match
            if old_name not in actual_files:
                # Try to find if the filename ends with one of the actual files
                found = False
                for actual in actual_files:
                    if old_name.endswith(actual) or actual.endswith(old_name):
                        print(f"Fixing {old_name} -> {actual}")
                        reel.video = actual
                        found = True
                        break
                if not found:
                    # Special case: try removing the first part before underscore
                    if '_' in old_name:
                        parts = old_name.split('_')
                        if len(parts) > 1:
                            potential = '_'.join(parts[1:])
                            if potential in actual_files:
                                print(f"Fixing {old_name} -> {potential} (underscore split)")
                                reel.video = potential
                                found = True
                
                if not found:
                    print(f"Could not find match for {old_name}")
            else:
                print(f"File {old_name} exists.")
        
        db.session.commit()
        print("Database commit successful.")

if __name__ == "__main__":
    fix_reels_filenames()
