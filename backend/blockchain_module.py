# backend/blockchain_module.py
import json
import hashlib
import time
from datetime import datetime, timedelta
from pathlib import Path


CHAIN_FILE = Path(__file__).parent / "chain.json"


class Blockchain:
    def __init__(self):
        self.chain = []
        self.load_chain()
        if not self.chain:
            self.create_genesis_block()

    # ---------- CORE BLOCKCHAIN ----------

    def create_genesis_block(self):
        genesis_block = {
            "index": 0,
            "timestamp": time.time(),
            "action_type": "Genesis",
            "report_id": None,
            "actor": "System",
            "data": {},
            "data_hash": self.hash_data({}),
            "previous_hash": "0",
            "sla_deadline": None,
        }
        self.chain.append(genesis_block)
        self.save_chain()

    def create_block(self, action_type, report_id, actor, data):
        previous_block = self.chain[-1]
        block = {
            "index": len(self.chain),
            "timestamp": time.time(),
            "action_type": action_type,  # e.g. Created / Under Review / Escalated / Validated / Commented
            "report_id": report_id,      # None for user registration
            "actor": actor,              # Reporter/Admin/Validator/System
            "data": data or {},
            "data_hash": self.hash_data(data or {}),
            "previous_hash": self.hash(previous_block),
            "sla_deadline": self.calculate_sla() if action_type == "Created" else None,
        }
        self.chain.append(block)
        self.save_chain()
        return block

    def hash(self, block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def hash_data(self, data):
        data_string = json.dumps(data, sort_keys=True).encode()
        return hashlib.sha256(data_string).hexdigest()

    def calculate_sla(self):
        # 7 days from now
        return (datetime.now() + timedelta(days=7)).timestamp()

    def save_chain(self):
        with open(CHAIN_FILE, "w") as f:
            json.dump(self.chain, f, indent=2)

    def load_chain(self):
        if CHAIN_FILE.exists():
            with open(CHAIN_FILE, "r") as f:
                self.chain = json.load(f)
        else:
            self.chain = []

    # ---------- USERS ----------

    def get_user(self, user_id):
        """
        user_id = the login identifier (we'll use email as user_id in frontend)
        """
        for block in reversed(self.chain):
            if block["action_type"] == "Register":
                data = block.get("data", {})
                if data.get("user_id") == user_id:
                    return data
        return None

    # ---------- REPORTS (Reporter/Admin/Validator) ----------

    def get_reports_for_reporter(self, reporter_email):
        """
        Returns list of timelines. Each timeline = list of blocks for that report.
        """
        report_ids = set()
        for block in self.chain:
            if block["action_type"] == "Created":
                data = block.get("data", {})
                if data.get("reporter_email") == reporter_email:
                    report_ids.add(block["report_id"])

        return [self.get_report_timeline(rid) for rid in report_ids]

    def get_all_reports(self):
        """
        Returns dict: report_id -> list of blocks (timeline).
        """
        reports = {}
        for block in self.chain:
            rid = block.get("report_id")
            if rid is not None:
                reports.setdefault(rid, []).append(block)
        return reports

    def get_report_timeline(self, report_id):
        return [b for b in self.chain if b.get("report_id") == report_id]

    def get_escalated_reports(self):
        """
        Returns list of timelines for reports that were escalated to Validator.
        """
        escalated = []
        for report_id, blocks in self.get_all_reports().items():
            if any(b["action_type"] == "Escalated to Validator" for b in blocks):
                escalated.append(blocks)
        return escalated

    def update_report(self, report_id, action_type, actor, data):
        """
        Adds a new block to the chain representing a status update or comment.
        """
        self.create_block(action_type, report_id, actor, data)
