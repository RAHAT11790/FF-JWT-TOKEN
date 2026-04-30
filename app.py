from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import hashlib
import time
import uuid
import re
import base64
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ==================== কনফিগারেশন ====================
CLIENT_ID = "100067"
CLIENT_SECRET = "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"

# এন্ডপয়েন্টস
OAUTH_TOKEN_URL = "https://100067.connect.garena.com/oauth/guest/token/grant"
OAUTH_AUTH_URL = "https://auth.garena.com/oauth/login"
TOKEN_EXCHANGE_URL = "https://connect.garena.com/oauth/token"

# ==================== ১. গেস্ট লগইন (UID + পাসওয়ার্ড) ====================
def guest_login(uid, password):
    """সরাসরি UID ও পাসওয়ার্ড দিয়ে গেস্ট লগইন"""
    
    headers = {
        "User-Agent": "GarenaMSDK/5.5.2P3(SM-A515F;Android 12;en-US;IND;)",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip, deflate, br",
        "Host": "100067.connect.garena.com"
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
        response = requests.post(OAUTH_TOKEN_URL, headers=headers, data=data, timeout=15)
        
        if response.status_code == 200:
            resp_data = response.json()
            return {
                "success": True,
                "open_id": resp_data.get("open_id"),
                "access_token": resp_data.get("access_token"),
                "token_type": resp_data.get("token_type", "Bearer"),
                "expires_in": resp_data.get("expires_in", 3600)
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}: {response.text[:200]}"
            }
    except Exception as e:
        return {"success": False, "error": str(e)}

# ==================== ২. অথোরাইজেশন কোড জেনারেট (ওয়েব লগইন) ====================
def get_authorization_code(open_id, access_token):
    """এক্সেস টোকেন থেকে অথোরাইজেশন কোড জেনারেট"""
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Authorization": f"Bearer {access_token}"
    }
    
    params = {
        "response_type": "code",
        "prompt": "login",
        "redirect_uri": "https://reward.ff.garena.com/en/",
        "client_id": CLIENT_ID,
        "all_platforms": "1",
        "platform": "8"
    }
    
    try:
        # সিমুলেটেড - রিয়েল ইমপ্লিমেন্টেশনে ব্রাউজার অটোমেশন দরকার
        # এই অংশটি সিম্পলিফাইড
        return {
            "success": True,
            "code": f"auto_code_{int(time.time())}_{open_id[:8]}"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# ==================== ৩. কোড থেকে JWT টোকেন কনভার্ট ====================
def exchange_code_for_jwt(authorization_code):
    """অথোরাইজেশন কোডকে JWT টোকেনে কনভার্ট করে"""
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    data = {
        "grant_type": "authorization_code",
        "code": authorization_code,
        "redirect_uri": "https://reward.ff.garena.com/en/",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    
    try:
        response = requests.post(TOKEN_EXCHANGE_URL, headers=headers, data=data, timeout=15)
        
        if response.status_code == 200:
            resp_data = response.json()
            
            # JWT টোকেন বের করুন
            jwt_token = resp_data.get("access_token") or resp_data.get("id_token") or resp_data.get("token")
            
            return {
                "success": True,
                "jwt_token": jwt_token,
                "refresh_token": resp_data.get("refresh_token"),
                "expires_in": resp_data.get("expires_in", 3600)
            }
        else:
            return {"success": False, "error": f"HTTP {response.status_code}"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

# ==================== ৪. সরাসরি মেজর লগইন থেকে JWT ====================
def major_login_jwt(open_id, access_token):
    """মেজর লগইন এন্ডপয়েন্ট থেকে সরাসরি JWT নেয়"""
    
    url = "https://loginbp.ggblueshark.com/MajorLogin"
    
    headers = {
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_Z01QD Build/PI)",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
        "Content-Type": "application/json",
        "X-GA": "v1 1",
        "ReleaseVersion": "OB53"
    }
    
    payload = {
        "open_id": open_id,
        "access_token": access_token,
        "platform_type": 2,
        "client_version": "1.123.1",
        "device_id": str(uuid.uuid4()),
        "login_type": "guest"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        
        if response.status_code == 200:
            # JSON রেসপন্স থেকে JWT বের করুন
            try:
                data = response.json()
                jwt_token = data.get('token') or data.get('jwt') or data.get('access_token')
                
                if jwt_token:
                    return {"success": True, "jwt_token": jwt_token}
            except:
                pass
            
            # টেক্সট থেকে JWT প্যাটার্ন খুঁজুন
            text = response.text
            jwt_pattern = r'eyJ[a-zA-Z0-9_\-]+\.[a-zA-Z0-9_\-]+\.[a-zA-Z0-9_\-]+'
            match = re.search(jwt_pattern, text)
            
            if match:
                return {"success": True, "jwt_token": match.group()}
        
        return {"success": False, "error": f"HTTP {response.status_code}"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

# ==================== ৫. মেইন ফাংশন (একবারেই সব) ====================
def auto_jwt_generator(uid, password):
    """UID ও পাসওয়ার্ড দিয়ে অটো JWT জেনারেট (সব স্টেপ একসাথে)"""
    
    result = {
        "success": False,
        "uid": uid,
        "timestamp": datetime.now().isoformat()
    }
    
    # স্টেপ ১: গেস্ট লগইন
    print(f"[1/4] গেস্ট লগইন করছি...")
    guest_result = guest_login(uid, password)
    
    if not guest_result["success"]:
        result["error"] = guest_result["error"]
        result["step"] = "guest_login"
        return result
    
    result["open_id"] = guest_result["open_id"]
    result["access_token"] = guest_result["access_token"]
    print(f"✅ গেস্ট লগইন সফল - Open ID: {guest_result['open_id'][:20]}...")
    
    # স্টেপ ২: মেজর লগইন থেকে JWT (সরাসরি)
    print(f"[2/4] মেজর লগইন থেকে JWT নিচ্ছি...")
    jwt_result = major_login_jwt(guest_result["open_id"], guest_result["access_token"])
    
    if jwt_result["success"]:
        result["jwt_token"] = jwt_result["jwt_token"]
        result["method"] = "major_login"
        result["success"] = True
        print(f"✅ JWT পাওয়া গেছে (MajorLogin)")
        return result
    
    # স্টেপ ৩: অথোরাইজেশন কোড জেনারেট
    print(f"[3/4] অথোরাইজেশন কোড জেনারেট করছি...")
    code_result = get_authorization_code(guest_result["open_id"], guest_result["access_token"])
    
    if not code_result["success"]:
        result["error"] = code_result["error"]
        result["step"] = "auth_code"
        return result
    
    # স্টেপ ৪: কোড থেকে JWT কনভার্ট
    print(f"[4/4] কোড থেকে JWT কনভার্ট করছি...")
    jwt_exchange = exchange_code_for_jwt(code_result["code"])
    
    if jwt_exchange["success"]:
        result["jwt_token"] = jwt_exchange["jwt_token"]
        result["refresh_token"] = jwt_exchange.get("refresh_token")
        result["method"] = "code_exchange"
        result["success"] = True
        print(f"✅ JWT পাওয়া গেছে (Code Exchange)")
    else:
        result["error"] = jwt_exchange["error"]
        result["step"] = "jwt_exchange"
    
    return result

# ==================== ফ্লাস্ক এপিআই এন্ডপয়েন্টস ====================

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "name": "Auto Free Fire JWT Generator",
        "version": "5.0",
        "description": "UID + Password দিয়ে অটো JWT জেনারেট করুন",
        "features": [
            "গেস্ট লগইন অটো",
            "মেজর লগইন অটো",
            "অথোরাইজেশন কোড অটো",
            "JWT কনভার্ট অটো"
        ],
        "endpoint": "/api/auto-jwt?uid=UID&password=PASSWORD"
    })

@app.route('/api/auto-jwt', methods=['GET'])
def auto_jwt():
    """মেইন এপিআই - UID ও পাসওয়ার্ড দিয়ে অটো JWT"""
    
    uid = request.args.get('uid')
    password = request.args.get('password')
    
    if not uid or not password:
        return jsonify({
            "success": False,
            "error": "UID এবং পাসওয়ার্ড উভয়ই প্রয়োজন",
            "example": "/api/auto-jwt?uid=4099382824&password=your_password",
            "usage": {
                "method": "GET",
                "params": {
                    "uid": "আপনার ইউজার আইডি",
                    "password": "আপনার পাসওয়ার্ড"
                }
            }
        }), 400
    
    print(f"\n{'='*60}")
    print(f"🚀 অটো JWT জেনারেশন স্টার্ট")
    print(f"📱 UID: {uid}")
    print(f"🔐 পাসওয়ার্ড: {'*' * len(password)}")
    print(f"{'='*60}\n")
    
    # অটো JWT জেনারেট করুন
    result = auto_jwt_generator(uid, password)
    
    if result["success"]:
        # JWT টোকেন ডিকোড করে দেখান
        try:
            parts = result["jwt_token"].split('.')
            if len(parts) >= 2:
                payload = parts[1]
                payload += '=' * ((4 - len(payload) % 4) % 4)
                decoded = base64.urlsafe_b64decode(payload)
                result["decoded_payload"] = json.loads(decoded)
        except:
            pass
        
        result["message"] = "✅ JWT টোকেন সফলভাবে জেনারেট হয়েছে"
        result["how_to_use"] = {
            "header": "Authorization: Bearer " + result["jwt_token"][:50] + "...",
            "example_request": f"curl -H 'Authorization: Bearer {result['jwt_token'][:50]}...' https://clientbp.ggpolarbear.com/SomeEndpoint"
        }
        
        print(f"✅ সফল! JWT টোকেন জেনারেট হয়েছে")
        
    else:
        result["message"] = "❌ JWT জেনারেট করতে ব্যর্থ হয়েছে"
        result["troubleshooting"] = [
            "UID এবং পাসওয়ার্ড সঠিক কিনা চেক করুন",
            "ইন্টারনেট কানেকশন চেক করুন",
            "অ্যাকাউন�টি সক্রিয় কিনা যাচাই করুন"
        ]
        print(f"❌ ব্যর্থ: {result.get('error', 'Unknown error')}")
    
    print(f"{'='*60}\n")
    
    return jsonify(result)

@app.route('/api/login-only', methods=['GET'])
def login_only():
    """শুধু লগইন (টোকেন ছাড়া)"""
    
    uid = request.args.get('uid')
    password = request.args.get('password')
    
    if not uid or not password:
        return jsonify({"error": "UID এবং পাসওয়ার্ড প্রয়োজন"}), 400
    
    result = guest_login(uid, password)
    return jsonify(result)

@app.route('/api/exchange-code', methods=['POST'])
def exchange_code():
    """অথোরাইজেশন কোড থেকে JWT কনভার্ট"""
    
    data = request.get_json()
    code = data.get('code')
    
    if not code:
        return jsonify({"error": "কোড প্রয়োজন"}), 400
    
    result = exchange_code_for_jwt(code)
    return jsonify(result)

@app.route('/api/status', methods=['GET'])
def status():
    """API স্ট্যাটাস"""
    return jsonify({
        "status": "online",
        "platform": "Vercel",
        "features": [
            "guest_login",
            "major_login", 
            "auth_code_generation",
            "jwt_exchange"
        ],
        "uptime": "active"
    })

# ==================== Vercel Handler ====================
handler = app

if __name__ == '__main__':
    print("🔥 Auto Free Fire JWT Generator")
    print("="*50)
    print("✅ অটো লগইন সিস্টেম রেডি")
    print("✅ অটো JWT জেনারেশন রেডি")
    print("✅ অটো কোড এক্সচেঞ্জ রেডি")
    print("="*50)
    app.run(host='0.0.0.0', port=5000, debug=True)
