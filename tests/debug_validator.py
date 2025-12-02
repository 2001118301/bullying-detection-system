from blockchain_module import Blockchain
import json

bc = Blockchain()
print(f"Chain length: {len(bc.chain)}")

print("--- Registered Users ---")
found_validator = False
for block in bc.chain:
    if block["action_type"] == "Register":
        data = block.get("data", {})
        uid = data.get("user_id")
        role = data.get("role")
        print(f"User: {uid}, Role: {role}")
        if uid == "validator":
            found_validator = True

if not found_validator:
    print("WARNING: 'validator' user NOT found!")
else:
    print("SUCCESS: 'validator' user found.")
