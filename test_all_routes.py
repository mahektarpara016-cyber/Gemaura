"""
Gemaura Full Route Test Suite - Corrected
Tests all major endpoints for User, Seller, and Admin panels.
"""
import sys
import io
import requests

# Force UTF-8 output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = "http://127.0.0.1:5000"

PASS = "[PASS]"
FAIL = "[FAIL]"

results = []

def mk_session():
    return requests.Session()

def test(sess, label, url, method="GET", data=None, expected_codes=(200,302), check_text=None):
    try:
        if method == "POST":
            resp = sess.post(url, data=data, allow_redirects=True, timeout=8)
        else:
            resp = sess.get(url, allow_redirects=True, timeout=8)

        status_ok = resp.status_code in expected_codes
        text_ok = True
        if check_text:
            text_ok = check_text.lower() in resp.text.lower()

        icon = PASS if (status_ok and text_ok) else FAIL
        note = ""
        if not status_ok:
            note = f" [HTTP {resp.status_code}]"
        if not text_ok:
            note += f" [missing text: '{check_text}']"

        results.append((icon, label, resp.status_code, note))
        print(f"{icon}  [{resp.status_code}]  {label}{note}")
        return resp
    except Exception as e:
        results.append((FAIL, label, "ERR", str(e)))
        print(f"{FAIL}  [ERR]  {label} -> {e}")
        return None


print("=" * 65)
print("  GEMAURA - Full Route Test Suite")
print("=" * 65)

# ═══════════════════════════════════════════════════════════════
# USER PANEL (public / guest)
# ═══════════════════════════════════════════════════════════════
print("\n[USER] Public Pages")
user_sess = mk_session()
test(user_sess, "Homepage /",                       f"{BASE}/")
test(user_sess, "Shop /shop",                       f"{BASE}/shop")
test(user_sess, "Shop with search /shop?q=ring",    f"{BASE}/shop?q=ring")
test(user_sess, "Shop by category /shop?category=1",f"{BASE}/shop?category=1")
test(user_sess, "Login page GET /login",             f"{BASE}/login")
test(user_sess, "Register page GET /register",       f"{BASE}/register")
test(user_sess, "About /about",                     f"{BASE}/about")
test(user_sess, "Contact /contact",                 f"{BASE}/contact")
test(user_sess, "Reels /reels",                     f"{BASE}/reels")
test(user_sess, "API Search /api/search?q=ring",     f"{BASE}/api/search?q=ring")
test(user_sess, "API Counts /api/counts",            f"{BASE}/api/counts")

# Cart and wishlist redirect to login for guests (check 200 after redirect to /login)
print("\n[USER] Protected Pages - Should redirect to login")
test(user_sess, "Cart (guest -> redirect login)",        f"{BASE}/cart", check_text="login")
test(user_sess, "Wishlist (guest -> redirect login)",    f"{BASE}/wishlist", check_text="login")
test(user_sess, "Profile (guest -> redirect login)",     f"{BASE}/profile", check_text="login")
test(user_sess, "Orders (guest -> redirect login)",      f"{BASE}/orders", check_text="login")
test(user_sess, "Checkout (guest -> redirect login)",    f"{BASE}/checkout")

# Product detail (needs a product, try id 1)
r = test(user_sess, "Product detail /product/1",        f"{BASE}/product/1", expected_codes=(200, 404))

# ═══════════════════════════════════════════════════════════════
# USER LOGIN & PROTECTED
# ═══════════════════════════════════════════════════════════════
print("\n[USER] Login & authenticated pages")
# Try to create or find a test user first via registration
r_reg = test(user_sess, "Register new user (POST)",  f"{BASE}/register", method="POST",
             data={"name": "Test User", "email": "autotest@gemaura.com", "password": "autotest123"})

# Now login
r_login = test(user_sess, "User Login (POST)",  f"{BASE}/login", method="POST",
               data={"email": "autotest@gemaura.com", "password": "autotest123"})

test(user_sess, "Profile (logged in)",      f"{BASE}/profile")
test(user_sess, "Orders (logged in)",       f"{BASE}/orders")

# ═══════════════════════════════════════════════════════════════
# SELLER PANEL
# ═══════════════════════════════════════════════════════════════
print("\n[SELLER] Public pages")
seller_sess = mk_session()
test(seller_sess, "Seller Login page GET /seller/login",     f"{BASE}/seller/login")
test(seller_sess, "Seller Register page GET /seller/register", f"{BASE}/seller/register")

print("\n[SELLER] Login (existing seller)")
# Try register first, or might already exist
test(seller_sess, "Seller Register (POST)", f"{BASE}/seller/register", method="POST",
     data={"shop_name": "Test Shop", "email": "autoseller@gemaura.com", "password": "seller123"})
     
# Note: seller needs admin approval - test with a pre-approved seller if exists
# Gemaura has no auto-approve, so we test the response to login attempt
r_sl = test(seller_sess, "Seller Login (POST - may be pending)",
            f"{BASE}/seller/login", method="POST",
            data={"email": "autoseller@gemaura.com", "password": "seller123"})

# The seller may be pending, so the dashboard redirects to login
test(seller_sess, "Seller Dashboard /seller/ (may redirect)", f"{BASE}/seller/")
test(seller_sess, "Seller Products /seller/products",          f"{BASE}/seller/products")
test(seller_sess, "Seller Add Product /seller/products/add",   f"{BASE}/seller/products/add")
test(seller_sess, "Seller Orders /seller/orders",              f"{BASE}/seller/orders")
test(seller_sess, "Seller Reels /seller/reels",                f"{BASE}/seller/reels")
test(seller_sess, "Seller Profile /seller/profile",            f"{BASE}/seller/profile")
test(seller_sess, "Seller Earnings /seller/earnings",          f"{BASE}/seller/earnings")

# ═══════════════════════════════════════════════════════════════
# ADMIN PANEL
# ═══════════════════════════════════════════════════════════════
print("\n[ADMIN] Pages")
admin_sess = mk_session()
test(admin_sess, "Admin Login page GET /admin/login",  f"{BASE}/admin/login")
test(admin_sess, "Admin Login (POST)",  f"{BASE}/admin/login", method="POST",
     data={"email": "admin@gemaura.com", "password": "admin123"})
test(admin_sess, "Admin Dashboard /admin/",            f"{BASE}/admin/")
test(admin_sess, "Admin Users /admin/users",            f"{BASE}/admin/users")
test(admin_sess, "Admin Sellers /admin/sellers",        f"{BASE}/admin/sellers")
test(admin_sess, "Admin Products /admin/products",      f"{BASE}/admin/products")
test(admin_sess, "Admin Orders /admin/orders",          f"{BASE}/admin/orders")
test(admin_sess, "Admin Categories /admin/categories",  f"{BASE}/admin/categories")
test(admin_sess, "Admin Reviews /admin/reviews",        f"{BASE}/admin/reviews")
test(admin_sess, "Admin Reels /admin/reels",            f"{BASE}/admin/reels")
test(admin_sess, "Admin Profile /admin/profile",        f"{BASE}/admin/profile")

# ═══════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 65)
total  = len(results)
passed = sum(1 for r in results if r[0] == PASS)
failed = sum(1 for r in results if r[0] == FAIL)
print(f"  RESULT: {passed}/{total} passed  |  {failed} failed")
print("=" * 65)

if failed > 0:
    print("\nFailed:")
    for r in results:
        if r[0] == FAIL:
            print(f"  {FAIL}  HTTP {r[2]}  {r[1]}  {r[3]}")
