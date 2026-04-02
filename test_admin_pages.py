import requests

def test_admin():
    s = requests.Session()
    # Login
    url = "http://127.0.0.1:5000/admin/login"
    r = s.get(url)
    if r.status_code != 200:
        print("Failed to get login page")
        return
    
    r = s.post(url, data={'email': 'admin@gemaura.com', 'password': 'admin123'})
    
    # Test dashboard
    pages = [
        "/admin/",
        "/admin/users",
        "/admin/sellers",
        "/admin/profile",
        "/admin/categories",
        "/admin/products",
        "/admin/orders",
        "/admin/reviews",
        "/admin/reels",
    ]
    
    for page in pages:
        res = s.get(f"http://127.0.0.1:5000{page}")
        if res.status_code == 200:
            print(f"SUCCESS: {page}")
        else:
            print(f"ERROR: {page} returned {res.status_code}")

if __name__ == '__main__':
    test_admin()
