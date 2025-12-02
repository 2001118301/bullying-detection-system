# backend/app.py
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from blockchain_module import Blockchain
from ai_module import analyze_text, analyze_image
import hashlib
import os
import uuid
import time
import jwt
import datetime
from functools import wraps
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)  # allow requests from frontend files
app.config['SECRET_KEY'] = 'your_secret_key_here_change_this_in_prod'  # TODO: Move to env var

blockchain = Blockchain()

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ---------- AUTH DECORATOR ----------

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
        
        if not token:
            return jsonify({'error': 'Token is missing!'}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = blockchain.get_user(data['user_id'])
            if not current_user:
                 return jsonify({'error': 'User not found!'}), 401
        except Exception as e:
            return jsonify({'error': 'Token is invalid!'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated


# ---------- AUTH ROUTES ----------

@app.route("/register", methods=["POST"])
def register():
    """
    Expected JSON:
    {
      "user_id": "user@example.com",
      "password": "plain-text",
      "role": "Reporter" | "Admin" | "Validator",
      "device_hash": "some_string" (optional now)
    }
    """
    data = request.json
    user_id = data.get("user_id")
    password_raw = data.get("password", "")
    role = data.get("role", "Reporter")
    device_hash = data.get("device_hash", "demo_device")

    if not user_id or not password_raw:
        return jsonify({"error": "user_id and password are required"}), 400

    # Allow re-registration to update device hash or password
    # if blockchain.get_user(user_id):
    #    return jsonify({"error": "User already exists"}), 400

    # Secure password hashing
    password_hash = generate_password_hash(password_raw)

    user_data = {
        "user_id": user_id,
        "password_hash": password_hash,
        "role": role,
        "device_hash": device_hash,
    }
    blockchain.create_block("Register", None, "System", user_data)
    return jsonify({"message": "Registered successfully", "user_id": user_id, "role": role})


@app.route("/login", methods=["POST"])
def login():
    """
    Expected JSON:
    {
      "user_id": "user@example.com",
      "password": "plain-text"
    }
    """
    data = request.json
    user_id = data.get("user_id")
    password_raw = data.get("password", "")

    user = blockchain.get_user(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 401

    # Verify password hash
    if not check_password_hash(user["password_hash"], password_raw):
        return jsonify({"error": "Invalid password"}), 401

    # Verify device hash
    request_device_hash = data.get("device_hash")
    stored_device_hash = user.get("device_hash")

    if stored_device_hash and request_device_hash != stored_device_hash:
         return jsonify({"error": "Login failed: Unrecognized device. Please register again."}), 403

    # Generate JWT
    token = jwt.encode({
        'user_id': user['user_id'],
        'role': user['role'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, app.config['SECRET_KEY'], algorithm="HS256")

    return jsonify({
        "message": "Logged in",
        "token": token,
        "role": user["role"],
        "user_id": user_id
    })


# ---------- REPORT SUBMISSION ----------

@app.route("/submit_report", methods=["POST"])
@token_required
def submit_report(current_user):
    """
    Content-Type: multipart/form-data
    Fields:
      - student_id
      - description
      - witness (optional)
      - evidence (file, required)
      - date
    """
    form = request.form
    reporter_email = current_user['user_id'] # Use email from token
    student_id = form.get("student_id")
    description = form.get("description")
    witness = form.get("witness", "")
    date_submitted = form.get("date")

    if not description or not student_id:
        return jsonify({"error": "description and student_id are required"}), 400

    # Handle file upload
    evidence = request.files.get("evidence")
    if not evidence:
        return jsonify({"error": "Evidence (photo/video) is required"}), 400

    report_id = str(uuid.uuid4())

    safe_name = secure_filename(evidence.filename)
    evidence_filename = f"{report_id}_{safe_name}"
    evidence_path = os.path.join(UPLOAD_FOLDER, evidence_filename)
    evidence.save(evidence_path)

    # AI analysis
    ai_text = analyze_text(description)
    ai_image = analyze_image(evidence_path)

    report_data = {
        "reporter_email": reporter_email,
        "student_id": student_id,
        "description": description,
        "witness": witness,
        "evidence": evidence_filename,
        "date_submitted": date_submitted,
        "ai_text": ai_text,
        "ai_image": ai_image,
        "status": "Submitted",
        "created_at": time.time(),
    }

    blockchain.create_block("Created", report_id, "Reporter", report_data)

    return jsonify({"message": "Report submitted", "report_id": report_id})


# ---------- REPORT RETRIEVAL ----------

@app.route("/get_reports", methods=["GET"])
@token_required
def get_reports(current_user):
    """
    Query params:
      role = Reporter | Admin | Validator
      (email is inferred from token for Reporter)
    """
    role = request.args.get("role")
    
    # Security check: Ensure user is requesting for their own role or has permission
    if role != current_user['role']:
         # Allow Admin/Validator to see everything, but Reporter can only see their own.
         # Actually, the logic below handles what is returned. 
         # But we should probably enforce that a Reporter cannot ask for Admin view.
         if current_user['role'] == 'Reporter' and role != 'Reporter':
             return jsonify({"error": "Unauthorized role access"}), 403

    if role == "Reporter":
        email = current_user['user_id']
        timelines = blockchain.get_reports_for_reporter(email)
        return jsonify(timelines)

    elif role == "Admin":
        if current_user['role'] != 'Admin': return jsonify({"error": "Unauthorized"}), 403
        reports = blockchain.get_all_reports()
        return jsonify(reports)

    elif role == "Validator":
        if current_user['role'] != 'Validator': return jsonify({"error": "Unauthorized"}), 403
        # Validator now sees ALL reports to oversee the workflow
        all_reports = blockchain.get_all_reports()
        return jsonify(all_reports)

    return jsonify({"error": "Invalid role"}), 400


# ---------- REPORT UPDATE (ADMIN & VALIDATOR) ----------

@app.route("/update_report", methods=["POST"])
@token_required
def update_report(current_user):
    """
    Expected JSON:
    {
      "report_id": "...",
      "action_type": "...",
      "remarks": "optional comments"
    }
    """
    # Role check
    if current_user['role'] not in ['Admin', 'Validator']:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json
    report_id = data.get("report_id")
    action_type = data.get("action_type")
    actor = current_user['role']
    remarks = data.get("remarks", "")

    if not report_id or not action_type:
        return jsonify({"error": "report_id and action_type are required"}), 400

    block_data = {"remarks": remarks}
    blockchain.update_report(report_id, action_type, actor, block_data)

    return jsonify({"message": "Report updated"})


# ---------- FILE SERVING ----------

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    # In a real app, you might want to protect this too, 
    # but for now we'll leave it open so <img> tags work easily.
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route("/frontend/<path:filename>")
def serve_frontend(filename):
    frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
    return send_from_directory(frontend_dir, filename)


if __name__ == "__main__":
    app.run(debug=False)
