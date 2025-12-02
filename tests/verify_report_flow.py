import requests
import time
import sys

BASE_URL = "http://127.0.0.1:5000"
TIMESTAMP = int(time.time())

REPORTER_EMAIL = f"reporter_{TIMESTAMP}@test.com"
ADMIN_EMAIL = f"admin_{TIMESTAMP}@test.com"
VALIDATOR_EMAIL = f"validator_{TIMESTAMP}@test.com"
PASSWORD = "123"

def register_and_login(email, role):
    print(f"--- Registering {role} ({email}) ---")
    resp = requests.post(f"{BASE_URL}/register", json={
        "user_id": email,
        "password": PASSWORD,
        "role": role
    })
    if resp.status_code != 200:
        print(f"Failed to register {role}: {resp.text}")
        sys.exit(1)
    
    print(f"--- Logging in {role} ---")
    resp = requests.post(f"{BASE_URL}/login", json={
        "user_id": email,
        "password": PASSWORD
    })
    if resp.status_code != 200:
        print(f"Failed to login {role}: {resp.text}")
        sys.exit(1)
    
    return resp.json()["token"]

def main():
    try:
        # 1. Setup Users
        reporter_token = register_and_login(REPORTER_EMAIL, "Reporter")
        admin_token = register_and_login(ADMIN_EMAIL, "Admin")
        validator_token = register_and_login(VALIDATOR_EMAIL, "Validator")

        # 2. Submit Report
        print("\n--- Submitting Report ---")
        report_desc = f"Test Report {TIMESTAMP}"
        resp = requests.post(f"{BASE_URL}/submit_report", 
            headers={"Authorization": f"Bearer {reporter_token}"},
            data={"description": report_desc}
        )
        if resp.status_code != 200:
            print(f"Failed to submit report: {resp.text}")
            sys.exit(1)
        
        report_id = resp.json()["report_id"]
        print(f"Report Submitted. ID: {report_id}")

        # 3. Verify Reporter can see it
        print("\n--- Verifying Reporter View ---")
        resp = requests.get(f"{BASE_URL}/get_reports?role=Reporter", 
            headers={"Authorization": f"Bearer {reporter_token}"}
        )
        reports = resp.json()
        # reports is a list of timelines
        found = False
        for timeline in reports:
            if timeline[0]["report_id"] == report_id:
                found = True
                break
        
        if found:
            print("SUCCESS: Reporter can see the report.")
        else:
            print("FAILURE: Reporter cannot see the report.")
            sys.exit(1)

        # 4. Verify Admin can see it
        print("\n--- Verifying Admin View ---")
        resp = requests.get(f"{BASE_URL}/get_reports?role=Admin", 
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        all_reports = resp.json()
        if report_id in all_reports:
            print("SUCCESS: Admin can see the report.")
        else:
            print("FAILURE: Admin cannot see the report.")
            sys.exit(1)

        # 5. Escalate to Validator
        print("\n--- Escalating to Validator ---")
        resp = requests.post(f"{BASE_URL}/update_report",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "report_id": report_id,
                "action_type": "Escalated to Validator",
                "remarks": "Escalating for review"
            }
        )
        if resp.status_code == 200:
            print("SUCCESS: Report escalated.")
        else:
            print(f"FAILURE: Could not escalate: {resp.text}")
            sys.exit(1)

        # 6. Verify Validator can see it
        print("\n--- Verifying Validator View ---")
        resp = requests.get(f"{BASE_URL}/get_reports?role=Validator", 
            headers={"Authorization": f"Bearer {validator_token}"}
        )
        escalated_reports = resp.json()
        # escalated_reports is a list of timelines
        found_val = False
        for timeline in escalated_reports:
            if timeline[0]["report_id"] == report_id:
                found_val = True
                break
        
        if found_val:
            print("SUCCESS: Validator can see the report.")
        else:
            print("FAILURE: Validator cannot see the report.")
            sys.exit(1)

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
