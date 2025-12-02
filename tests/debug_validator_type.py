from blockchain_module import Blockchain
import json

bc = Blockchain()
reports = bc.get_all_reports()
print(f"Type of reports: {type(reports)}")
if isinstance(reports, dict):
    print(f"Keys: {list(reports.keys())}")
elif isinstance(reports, list):
    print(f"Length: {len(reports)}")
