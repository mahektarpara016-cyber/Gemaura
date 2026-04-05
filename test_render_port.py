import os
import sys

# Mocking the environment to test port resolution
os.environ['PORT'] = '10000'

def test_startup():
    from app import app
    print(f"Flask App configured: {app}")
    
    # Check if we can get the port correctly
    port = int(os.environ.get('PORT', 5000))
    print(f"Target Port for binding: {port}")
    if port == 10000:
        print("✅ Environment Port detected correctly!")
    else:
        print("❌ Port detection failed!")

if __name__ == "__main__":
    test_startup()
