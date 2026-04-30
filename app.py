import requests
import json
import hashlib
import time
import uuid
from flask import Flask, request, jsonify

app = Flask(__name__)

# Garena সার্ভার এন্ডপয়েন্টস
OAUTH_URL = "https://100067.connect.garena.com/oauth/guest/token/grant"
MAJOR_LOGIN_URL = "https://loginbp.ggblueshark.com/MajorLogin"
CLIENT_ID = "100067"
CLIENT_SECRET = "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"

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
        response = requests.post(OAUTH_URL, headers=headers, data=data, timeout=10)
        if response.status_code == 200:
            resp_data = response.json()
            return resp_data.get("open_id"), resp_data.get("access_token"), None
        else:
            return None, None, f"HTTP {response.status_code}"
    except Exception as e:
        return None, None, str(e)

def get_jwt_token(open_id, access_token):
    """MajorLogin করে JWT টোকেন নেয়"""
    
    url = "https://loginbp.ggblueshark.com/MajorLogin"
    
    headers = {
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_Z01QD Build/PI)",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
        "Content-Type": "application/octet-stream",
        "X-Unity-Version": "2018.4.11f1",
        "ReleaseVersion": "OB53"
    }
    
    # MajorLoginRequest payload (simplified)
    import struct
    
    # Create protobuf-like data for MajorLogin
    payload_data = {
        "open_id": open_id,
        "access_token": access_token,
        "platform_type": 2,
        "client_version": "1.123.1",
        "device_id": "Google|34a7dcdf-a7d5-4cb6-8d7e-3b0e448a0c57"
    }
    
    # Convert to bytes (simplified - real implementation needs full protobuf)
    # Note: Full protobuf implementation needed for real request
    
    try:
        # This is simplified - 실제로는 encrypt করতে হবে
        response = requests.post(url, headers=headers, timeout=10)
        if response.status_code == 200:
            # Parse response to get JWT token
            # Full protobuf parsing required here
            return None
        return None
    except Exception as e:
        return None

@app.route('/get-real-jwt', methods=['GET'])
def get_real_jwt():
    """রিয়েল গেম সার্ভার থেকে JWT টোকেন নেয়"""
    
    uid = request.args.get('uid')
    password = request.args.get('password')
    
    if not uid or not password:
        return jsonify({
            "error": "Missing uid or password",
            "usage": "/get-real-jwt?uid=YOUR_UID&password=YOUR_PASSWORD"
        }), 400
    
    # Step 1: Get access token
    open_id, access_token, error = get_access_token(uid, password)
    
    if error:
        return jsonify({"success": False, "error": error}), 401
    
    # Step 2: Get JWT token from MajorLogin
    # Note: Full implementation requires proper protobuf encryption
    
    return jsonify({
        "success": True,
        "open_id": open_id,
        "access_token": access_token,
        "note": "JWT token requires protobuf encryption - check full implementation in previous code"
    })

@app.route('/simple-jwt', methods=['GET'])
def simple_jwt():
    """লোকাল JWT জেনারেটর (কোনো সার্ভার কানেক্ট করে না)"""
    
    # This is locally generated JWT - গেমে কাজ করবে না
    import jwt
    import datetime
    
    payload = {
        "uid": request.args.get('uid', '12345'),
        "iat": datetime.datetime.utcnow(),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    
    secret = "garena_secret_key"  # লোকাল কী - গেম সার্ভার চিনবে না
    token = jwt.encode(payload, secret, algorithm="HS256")
    
    return jsonify({
        "success": True,
        "token": token,
        "warning": "This is LOCAL JWT - NOT valid for game servers!",
        "note": "Game servers require JWT from Garena's MajorLogin endpoint"
    })

if __name__ == '__main__':
    app.run(port=5000)
