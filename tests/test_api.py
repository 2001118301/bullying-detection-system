import requests
import time

BASE_URL = "http://127.0.0.1:5000"
USER_ID = f"test_user_{int(time.time())}@example.com"
PASSWORD = "test_password"

def test_auth_flow():
    print("Testing Auth Flow...")

    # 1. Register
    print(f"Registering user: {USER_ID}")
    resp = requests.post(f"{BASE_URL}/register", json={
        "user_id": USER_ID,
        "password": PASSWORD,
        "role": "Reporter"
    })
    print(f"Register Status: {resp.status_code}")
    if resp.status_code != 200:
        print(f"Register Failed: {resp.text}")
        return

    # 2. Login
    print("Logging in...")
    resp = requests.post(f"{BASE_URL}/login", json={
        "user_id": USER_ID,
        "password": PASSWORD
    })
    print(f"Login Status: {resp.status_code}")
    if resp.status_code != 200:
        print(f"Login Failed: {resp.text}")
        return
    
    data = resp.json()
    token = data.get("token")
    if not token:
        print("Error: No token received!")
        return
    print("Token received successfully.")

    # 3. Access Protected Route (Submit Report)
    print("Accessing protected route (Submit Report)...")
    headers = {"Authorization": f"Bearer {token}"}
    report_data = {
        "description": "Test report description",
        "witness": "Test witness"
    }
    resp = requests.post(f"{BASE_URL}/submit_report", headers=headers, data=report_data)
    print(f"Submit Report Status: {resp.status_code}")
    if resp.status_code == 200:
        print("Report submitted successfully!")
        print(resp.json())
    else:
        print(f"Submit Report Failed: {resp.text}")

    # 4. Access Protected Route without Token (Should Fail)
    print("Accessing protected route without token...")
    resp = requests.post(f"{BASE_URL}/submit_report", data=report_data)
    print(f"Status (should be 401): {resp.status_code}")
    if resp.status_code == 401:
        print("Correctly denied access.")
    else:
        print(f"Error: Access granted without token! Status: {resp.status_code}")

if __name__ == "__main__":
    try:
        test_auth_flow()
    except Exception as e:
        print(f"Test failed with exception: {e}")
