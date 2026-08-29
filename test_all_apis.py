import requests
import sys

BASE_URL = "https://santexnika-loyha.duckdns.org"

def main():
    print(f"==================================================")
    print(f"  Live Server API Testing: {BASE_URL}")
    print(f"==================================================\n")

    results = []

    # 1. Root Endpoint
    try:
        r = requests.get(f"{BASE_URL}/")
        print(f"[GET /] Status: {r.status_code} | Body: {r.json()}")
        results.append(("GET /", r.status_code == 200, r.status_code))
    except Exception as e:
        print(f"[GET /] Error: {e}")
        results.append(("GET /", False, str(e)))

    # 2. Register Test User
    user_phone = "+998901234567"
    user_pass = "password123"
    user_name = "test_user_qa"
    token = None
    refresh_token = None

    try:
        payload = {
            "phone_number": user_phone,
            "username": user_name,
            "password": user_pass
        }
        r = requests.post(f"{BASE_URL}/auth/register", json=payload)
        print(f"[POST /auth/register] Status: {r.status_code} | Body: {r.text[:150]}")
        results.append(("POST /auth/register", r.status_code in [200, 400], r.status_code))
    except Exception as e:
        print(f"[POST /auth/register] Error: {e}")
        results.append(("POST /auth/register", False, str(e)))

    # 3. Login Test User
    try:
        payload = {
            "phone_number": user_phone,
            "password": user_pass
        }
        r = requests.post(f"{BASE_URL}/auth/login", json=payload)
        print(f"[POST /auth/login] Status: {r.status_code} | Body: {r.text[:150]}")
        if r.status_code == 200:
            data = r.json()
            token = data.get("access_token")
            refresh_token = data.get("refresh_token")
            results.append(("POST /auth/login", True, 200))
        else:
            results.append(("POST /auth/login", False, r.status_code))
    except Exception as e:
        print(f"[POST /auth/login] Error: {e}")
        results.append(("POST /auth/login", False, str(e)))

    headers = {"Authorization": f"Bearer {token}"} if token else {}

    # 4. Refresh Token
    if refresh_token:
        try:
            r = requests.post(f"{BASE_URL}/auth/refresh", json={"refresh_token": refresh_token})
            print(f"[POST /auth/refresh] Status: {r.status_code} | Body: {r.text[:150]}")
            results.append(("POST /auth/refresh", r.status_code == 200, r.status_code))
        except Exception as e:
            results.append(("POST /auth/refresh", False, str(e)))

    # 5. Get Profile (/users/me)
    if token:
        try:
            r = requests.get(f"{BASE_URL}/users/me", headers=headers)
            print(f"[GET /users/me] Status: {r.status_code} | Profile: {r.text[:150]}")
            results.append(("GET /users/me", r.status_code == 200, r.status_code))
        except Exception as e:
            results.append(("GET /users/me", False, str(e)))

    # 6. List Categories
    try:
        r = requests.get(f"{BASE_URL}/categories/")
        print(f"[GET /categories/] Status: {r.status_code} | Categories count: {len(r.json()) if r.status_code==200 else 0}")
        results.append(("GET /categories/", r.status_code == 200, r.status_code))
    except Exception as e:
        results.append(("GET /categories/", False, str(e)))

    # 7. List Products
    try:
        r = requests.get(f"{BASE_URL}/products/")
        print(f"[GET /products/] Status: {r.status_code} | Products count: {len(r.json()) if r.status_code==200 else 0}")
        results.append(("GET /products/", r.status_code == 200, r.status_code))
    except Exception as e:
        results.append(("GET /products/", False, str(e)))

    # 8. List My Orders
    if token:
        try:
            r = requests.get(f"{BASE_URL}/orders/me", headers=headers)
            print(f"[GET /orders/me] Status: {r.status_code} | Orders count: {len(r.json()) if r.status_code==200 else 0}")
            results.append(("GET /orders/me", r.status_code == 200, r.status_code))
        except Exception as e:
            results.append(("GET /orders/me", False, str(e)))

    print("\n==================================================")
    print("  SUMMARY TEST RESULTS")
    print("==================================================")
    for name, ok, code in results:
        status_str = "SUCCESS" if ok else "FAILED"
        print(f" - {name:<25} : {status_str} (Status/Info: {code})")

if __name__ == "__main__":
    main()
