import requests
import time

BASE_URL = "http://127.0.0.1:5000"

def run_verification():
    user_id = f"rereg_test_{int(time.time())}@example.com"
    password = "password123"
    device_a = "device_A_111"
    device_b = "device_B_222"

    # 1. Register with Device A
    print(f"1. Registering {user_id} with Device A...")
    res = requests.post(f"{BASE_URL}/register", json={
        "user_id": user_id,
        "password": password,
        "role": "Reporter",
        "device_hash": device_a
    })
    if res.status_code != 200:
        print("Registration failed:", res.text)
        return

    # 2. Login with Device A (Should Success)
    print("2. Logging in with Device A (Expected: Success)...")
    res = requests.post(f"{BASE_URL}/login", json={
        "user_id": user_id,
        "password": password,
        "device_hash": device_a
    })
    if res.status_code == 200:
        print("SUCCESS: Login with Device A passed.")
    else:
        print("FAILURE: Login with Device A failed:", res.text)

    # 3. Login with Device B (Should Fail)
    print("3. Logging in with Device B (Expected: Failure)...")
    res = requests.post(f"{BASE_URL}/login", json={
        "user_id": user_id,
        "password": password,
        "device_hash": device_b
    })
    if res.status_code == 403:
        print("SUCCESS: Login with Device B blocked.")
    else:
        print(f"FAILURE: Login with Device B unexpected status: {res.status_code}")

    # 4. Re-register with Device B
    print("4. Re-registering with Device B (Expected: Success)...")
    res = requests.post(f"{BASE_URL}/register", json={
        "user_id": user_id,
        "password": password,
        "role": "Reporter",
        "device_hash": device_b
    })
    if res.status_code == 200:
        print("SUCCESS: Re-registration passed.")
    else:
        print("FAILURE: Re-registration failed:", res.text)
        return

    # 5. Login with Device B (Should Success now)
    print("5. Logging in with Device B (Expected: Success)...")
    res = requests.post(f"{BASE_URL}/login", json={
        "user_id": user_id,
        "password": password,
        "device_hash": device_b
    })
    if res.status_code == 200:
        print("SUCCESS: Login with Device B passed after re-registration.")
    else:
        print("FAILURE: Login with Device B failed after re-registration:", res.text)

    # 6. Login with Device A (Should Fail now)
    print("6. Logging in with Device A (Expected: Failure)...")
    res = requests.post(f"{BASE_URL}/login", json={
        "user_id": user_id,
        "password": password,
        "device_hash": device_a
    })
    if res.status_code == 403:
        print("SUCCESS: Login with Device A blocked after re-registration.")
    else:
        print(f"FAILURE: Login with Device A unexpected status: {res.status_code}")

if __name__ == "__main__":
    try:
        run_verification()
    except Exception as e:
        print(f"An error occurred: {e}")
