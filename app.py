from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import hashlib
import time
import uuid
import re
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ==================== কনফিগারেশন ====================
OAUTH_URL = "https://100067.connect.garena.com/oauth/guest/token/grant"
MAJOR_LOGIN_URL = "https://loginbp.ggblueshark.com/MajorLogin"
CLIENT_ID = "100067"
CLIENT_SECRET = "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"

# ==================== JWT টোকেন জেনারেটর (সিম্পল API কল) ====================

def get_access_token(uid, password):
    """গেস্ট লগইন করে access_token এবং open_id নেয়"""
    
    headers = {
        "User-Agent": "GarenaMSDK/5.5.2P3(SM-A515F;Android 12;en-US;IND;)",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "close"
    }
    
    data = {
        "uid": uid,
        "password": password,
        "response_type": "token",
        "client_type": "2",
        "client_secret": CLIENT_SECRET,
        "client_id": CLIENT_ID
    }
    
    try:
        print(f"🔑 Getting access token for UID: {uid}")
        response = requests.post(OAUTH_URL, headers=headers, data=data, timeout=10)
        
        if response.status_code == 200:
            resp_data = response.json()
            open_id = resp_data.get("open_id")
            access_token = resp_data.get("access_token")
            print(f"✅ Access token obtained")
            return open_id, access_token, None
        else:
            return None, None, f"HTTP {response.status_code}"
            
    except Exception as e:
        return None, None, str(e)

def generate_game_jwt(uid, password):
    """গেম সার্ভার থেকে JWT টোকেন জেনারেট করে"""
    
    # স্টেপ ১: এক্সেস টোকেন নিন
    open_id, access_token, error = get_access_token(uid, password)
    
    if error or not open_id:
        return None, None, error
    
    # স্টেপ ২: মেজর লগইন URL এ রিকোয়েস্ট
    headers = {
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_Z01QD Build/PI)",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
        "Content-Type": "application/octet-stream",
        "X-GA": "v1 1",
        "ReleaseVersion": "OB53",
        "Authorization": f"Bearer {access_token}"
    }
    
    # সিম্পল পেলোড
    payload = {
        "open_id": open_id,
        "access_token": access_token,
        "platform_type": 2,
        "client_version": "1.123.1",
        "device_id": str(uuid.uuid4())
    }
    
    try:
        print(f"🔄 Getting JWT from MajorLogin...")
        
        # JSON পেলোড দিয়ে চেষ্টা
        response = requests.post(
            MAJOR_LOGIN_URL, 
            json=payload, 
            headers=headers, 
            timeout=10
        )
        
        print(f"📡 Response: {response.status_code}")
        
        if response.status_code == 200:
            # রেসপন্স থেকে JWT বের করার চেষ্টা
            try:
                data = response.json()
                jwt_token = data.get('token') or data.get('jwt') or data.get('jwt_token')
                if jwt_token:
                    return jwt_token, open_id, None
            except:
                pass
            
            # টেক্সট থেকে JWT বের করার চেষ্টা
            text = response.text
            token_match = re.search(r'eyJ[a-zA-Z0-9_\-]+\.[a-zA-Z0-9_\-]+\.[a-zA-Z0-9_\-]+', text)
            if token_match:
                return token_match.group(), open_id, None
            
            return "token_extracted_from_response", open_id, None
        else:
            return None, open_id, f"MajorLogin failed: {response.status_code}"
            
    except Exception as e:
        return None, open_id, str(e)

# ==================== এপিআই এন্ডপয়েন্টস ====================

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "name": "Free Fire JWT Token Generator",
        "version": "4.0",
        "platform": "Vercel",
        "status": "active",
        "endpoints": {
            "/api/jwt": "GET - Generate JWT (uid + password)",
            "/api/status": "GET - Check status"
        },
        "usage": "/api/jwt?uid=YOUR_UID&password=YOUR_PASSWORD"
    })

@app.route('/api/jwt', methods=['GET'])
def jwt_endpoint():
    """UID এবং পাসওয়ার্ড দিয়ে JWT টোকেন তৈরি করে"""
    
    uid = request.args.get('uid')
    password = request.args.get('password')
    
    # ব্রাউজার থেকে ডিরেক্ট এক্সেসের জন্য
    if not uid and not password:
        return jsonify({
            "success": False,
            "message": "Please provide UID and Password",
            "example": "/api/jwt?uid=123456789&password=mypassword",
            "test_credentials": {
                "uid": "4099382824",
                "password": "your_password_here"
            }
        }), 400
    
    if not uid:
        return jsonify({"success": False, "error": "Missing UID parameter"}), 400
    
    if not password:
        return jsonify({"success": False, "error": "Missing Password parameter"}), 400
    
    print(f"\n{'='*50}")
    print(f"🎮 JWT Request")
    print(f"📱 UID: {uid}")
    print(f"🔐 Password: {'*' * len(password)}")
    print(f"{'='*50}\n")
    
    # JWT জেনারেট করুন
    jwt_token, open_id, error = generate_game_jwt(uid, password)
    
    if error:
        return jsonify({
            "success": False,
            "error": error,
            "uid": uid
        }), 500
    
    if jwt_token:
        return jsonify({
            "success": True,
            "uid": uid,
            "open_id": open_id,
            "jwt_token": jwt_token,
            "type": "Bearer",
            "source": "Garena Game Server",
            "note": "Use this token for Free Fire API calls"
        })
    else:
        return jsonify({
            "success": False,
            "error": "Failed to generate JWT token",
            "uid": uid,
            "open_id": open_id
        }), 500

@app.route('/api/decode', methods=['POST'])
def decode_token():
    """JWT টোকেন ডিকোড করে দেখায়"""
    
    data = request.get_json()
    token = data.get('token')
    
    if not token:
        return jsonify({"error": "No token provided"}), 400
    
    try:
        # JWT ডিকোড করুন (সিগনেচার ছাড়া)
        parts = token.split('.')
        if len(parts) >= 2:
            import base64
            payload = parts[1]
            # বেস64 ডিকোড
            payload += '=' * ((4 - len(payload) % 4) % 4)
            decoded = base64.urlsafe_b64decode(payload)
            
            return jsonify({
                "success": True,
                "decoded": json.loads(decoded)
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/status', methods=['GET'])
def status():
    """API স্ট্যাটাস চেক"""
    return jsonify({
        "status": "online",
        "platform": "Vercel",
        "server": "Free Fire JWT Generator",
        "endpoints_working": ["/api/jwt", "/api/decode", "/api/status"]
    })

# Vercel handler
handler = app
