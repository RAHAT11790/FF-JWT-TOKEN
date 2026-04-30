import jwt
import json
import datetime
import hashlib
import uuid
import secrets
import time
import platform
import os
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # CORS enabled for Vercel deployment

# ==================== AUTO SECRET GENERATOR ====================

class AutoSecretGenerator:
    def __init__(self):
        self._secret_key = None
        
    def _generate_chaotic_secret(self) -> str:
        entropy1 = secrets.token_hex(64)
        entropy2 = hashlib.sha256(f"{platform.platform()}{time.time_ns()}".encode()).hexdigest()
        entropy3 = hashlib.sha256(str(time.time_ns()).encode()).hexdigest()
        entropy4 = base64.b64encode(os.urandom(48)).decode()
        entropy5 = str(uuid.uuid4()) + str(uuid.uuid4())
        entropy6 = hashlib.sha256(os.getenv("VERCEL_URL", "local").encode()).hexdigest()
        
        combined_entropy = f"{entropy1}{entropy2}{entropy3}{entropy4}{entropy5}{entropy6}"
        final_key = hashlib.sha512(combined_entropy.encode()).hexdigest()
        return final_key
    
    def get_secret_key(self):
        if self._secret_key is None:
            self._secret_key = self._generate_chaotic_secret()
        return self._secret_key

secret_manager = AutoSecretGenerator()
ALGORITHM = "HS256"

def generate_token(uid=None, expiry_minutes=60):
    token_id = str(uuid.uuid4())[:8]
    
    payload = {
        "jti": token_id,
        "iat": datetime.datetime.utcnow().isoformat(),
        "exp": (datetime.datetime.utcnow() + datetime.timedelta(minutes=expiry_minutes)).isoformat(),
        "timestamp_ns": time.time_ns(),
        "session_id": hashlib.md5(str(time.time_ns()).encode()).hexdigest()[:16]
    }
    
    if uid:
        payload["uid"] = str(uid)
        payload["password_hash"] = hashlib.md5(str(uid).encode()).hexdigest()[:16]
    
    headers = {
        "typ": "JWT",
        "alg": ALGORITHM,
        "kid": hashlib.md5(secret_manager.get_secret_key().encode()).hexdigest()[:8]
    }
    
    token = jwt.encode(payload, secret_manager.get_secret_key(), algorithm=ALGORITHM, headers=headers)
    return token, payload

def verify_token(token):
    try:
        payload = jwt.decode(token, secret_manager.get_secret_key(), algorithms=[ALGORITHM])
        return True, payload
    except jwt.ExpiredSignatureError:
        return False, "Token expired"
    except jwt.InvalidTokenError:
        return False, "Invalid token"

# ==================== API ENDPOINTS ====================

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "name": "Auto JWT Generator API",
        "version": "2.0",
        "platform": "Vercel",
        "endpoints": {
            "/auto-token": "Generate auto token (GET)",
            "/token-with-uid": "Generate token with UID (GET with ?uid=123)",
            "/verify": "Verify token (POST with {\"token\":\"...\"})"
        }
    })

@app.route('/auto-token', methods=['GET'])
def auto_token():
    token, payload = generate_token(expiry_minutes=60)
    return jsonify({
        "success": True,
        "token": token,
        "token_id": payload["jti"],
        "expires_in": "60 minutes"
    })

@app.route('/token-with-uid', methods=['GET'])
def token_with_uid():
    uid = request.args.get('uid')
    password = request.args.get('password')
    
    if not uid:
        return jsonify({
            "success": False,
            "error": "Missing uid parameter",
            "usage": "/token-with-uid?uid=YOUR_UID&password=YOUR_PASS"
        }), 400
    
    # Password is optional for token generation
    token, payload = generate_token(uid=uid, expiry_minutes=120)
    
    return jsonify({
        "success": True,
        "uid": uid,
        "token": token,
        "token_id": payload["jti"],
        "expires_in": "120 minutes"
    })

@app.route('/verify', methods=['POST'])
def verify():
    data = request.get_json()
    if not data or 'token' not in data:
        return jsonify({"error": "No token provided"}), 400
    
    is_valid, result = verify_token(data['token'])
    return jsonify({
        "valid": is_valid,
        "result": result if is_valid else {"error": result}
    })
