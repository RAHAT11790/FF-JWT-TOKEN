from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import hashlib
import time
import uuid
import base64
import struct
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from datetime import datetime
import urllib.parse
import re

app = Flask(__name__)
CORS(app)

# ==================== কনফিগারেশন ====================
OAUTH_URL = "https://100067.connect.garena.com/oauth/guest/token/grant"
MAJOR_LOGIN_URL = "https://loginbp.ggblueshark.com/MajorLogin"
CLIENT_ID = "100067"
CLIENT_SECRET = "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"

AES_KEY = b'Yg&tc%DEuh6%Zc^8'
AES_IV = b'6oyZDr22E3ychjM%'

# ==================== এনক্রিপশন ফাংশন ====================
def encrypt_aes(data: bytes) -> bytes:
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    padded = pad(data, AES.block_size)
    return cipher.encrypt(padded)

def decrypt_aes(data: bytes) -> bytes:
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES.IV)
    decrypted = cipher.decrypt(data)
    return unpad(decrypted, AES.block_size)

# ==================== কমপ্লিট প্রোটোবাফ বিল্ডার ====================
def encode_varint(value):
    """প্রোটোবাফের জন্য varint এনকোডিং"""
    result = []
    while value > 0x7F:
        result.append((value & 0x7F) | 0x80)
        value >>= 7
    result.append(value & 0x7F)
    return bytes(result) if result else b'\x00'

def encode_string(field_num, value):
    """প্রোটোবাফ স্ট্রিং ফিল্ড এনকোড"""
    tag = (field_num << 3) | 2  # wire type 2 = length-delimited
    value_bytes = value.encode('utf-8')
    return encode_varint(tag) + encode_varint(len(value_bytes)) + value_bytes

def encode_int(field_num, value):
    """প্রোটোবাফ ইন্টিজার ফিল্ড এনকোড"""
    tag = (field_num << 3) | 0  # wire type 0 = varint
    return encode_varint(tag) + encode_varint(value)

def build_major_login_payload(open_id, access_token, platform_type):
    """সম্পূর্ণ প্রোটোবাফ পেলোড বিল্ড"""
    
    payload = b''
    
    # ফিল্ড 3: event_time
    event_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    payload += encode_string(3, event_time)
    
    # ফিল্ড 4: game_name
    payload += encode_string(4, "free fire")
    
    # ফিল্ড 5: platform_id
    payload += encode_int(5, 1)
    
    # ফিল্ড 7: client_version
    payload += encode_string(7, "1.123.1")
    
    # ফিল্ড 8: system_software
    payload += encode_string(8, "Android OS 9 / API-28")
    
    # ফিল্ড 9: system_hardware
    payload += encode_string(9, "Handheld")
    
    # ফিল্ড 10: telecom_operator
    payload += encode_string(10, "Verizon")
    
    # ফিল্ড 11: network_type
    payload += encode_string(11, "WIFI")
    
    # ফিল্ড 12: screen_width
    payload += encode_int(12, 1920)
    
    # ফিল্ড 13: screen_height
    payload += encode_int(13, 1080)
    
    # ফিল্ড 22: open_id
    payload += encode_string(22, open_id)
    
    # ফিল্ড 29: access_token
    payload += encode_string(29, access_token)
    
    # ফিল্ড 23: open_id_type
    payload += encode_string(23, "4")
    
    # ফিল্ড 24: device_type
    payload += encode_string(24, "Handheld")
    
    # ফিল্ড 32: client_using_version
    payload += encode_string(32, hashlib.md5(f"{open_id}{time.time()}".encode()).hexdigest())
    
    # ফিল্ড 41: login_by
    payload += encode_int(41, 3)
    
    # ফিল্ড 42: library_path
    payload += encode_string(42, "/data/app/com.dts.freefireth/base.apk")
    
    # ফিল্ড 44: library_token
    payload += encode_string(44, hashlib.md5(access_token.encode()).hexdigest())
    
    # ফিল্ড 45: channel_type
    payload += encode_int(45, 3)
    
    # ফিল্ড 46: cpu_type
    payload += encode_int(46, 2)
    
    # ফিল্ড 48: cpu_architecture
    payload += encode_string(48, "64")
    
    # ফিল্ড 49: client_version_code
    payload += encode_string(49, "2019118695")
    
    # ফিল্ড 52: graphics_api
    payload += encode_string(52, "OpenGLES2")
    
    # ফিল্ড 61: release_channel
    payload += encode_string(61, "android")
    
    # ফিল্ড 97: if_push
    payload += encode_int(97, 1)
    
    # ফিল্ড 98: is_vpn
    payload += encode_int(98, 1)
    
    # ফিল্ড 99: origin_platform_type
    payload += encode_string(99, str(platform_type))
    
    # ফিল্ড 100: primary_platform_type
    payload += encode_string(100, str(platform_type))
    
    return payload

# ==================== এক্সেস টোকেন ফাংশন ====================
def get_access_token(uid, password):
    """গেস্ট লগইন"""
    
    headers = {
        "User-Agent": "GarenaMSDK/5.5.2P3(SM-A515F;Android 12;en-US;IND;)",
        "Content-Type": "application/x-www-form-urlencoded",
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
        response = requests.post(OAUTH_URL, headers=headers, data=data, timeout=15)
        
        if response.status_code == 200:
            resp_data = response.json()
            return resp_data.get("open_id"), resp_data.get("access_token"), None
        else:
            return None, None, f"HTTP {response.status_code}: {response.text[:100]}"
    except Exception as e:
        return None, None, str(e)

# ==================== মেজর লগইন ফাংশন ====================
def major_login(open_id, access_token, platform_type):
    """মেজর লগইন রিকোয়েস্ট"""
    
    headers = {
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_Z01QD Build/PI)",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
        "Content-Type": "application/octet-stream",
        "X-GA": "v1 1",
        "ReleaseVersion": "OB53"
    }
    
    # প্রোটোবাফ বিল্ড
    protobuf_payload = build_major_login_payload(open_id, access_token, platform_type)
    
    # এনক্রিপ্ট
    encrypted = encrypt_aes(protobuf_payload)
    
    try:
        response = requests.post(MAJOR_LOGIN_URL, data=encrypted, headers=headers, timeout=15)
        
        if response.status_code == 200:
            try:
                decrypted = decrypt_aes(response.content)
                
                # JWT টোকেন বের করার চেষ্টা
                decrypted_str = decrypted.decode('utf-8', errors='ignore')
                
                # প্যাটার্ন ম্যাচিং
                token_match = re.search(r'[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+', decrypted_str)
                if token_match:
                    return token_match.group()
                
                return "jwt_token_found"
            except:
                return None
        return None
    except:
        return None

# ==================== এপিআই এন্ডপয়েন্ট ====================

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "name": "Real Free Fire JWT Generator",
        "version": "3.0",
        "status": "active",
        "endpoint": "/jwt?uid=YOUR_UID&password=YOUR_PASSWORD"
    })

@app.route('/jwt', methods=['GET'])
def generate_jwt():
    """JWT টোকেন জেনারেট করুন"""
    
    uid = request.args.get('uid')
    password = request.args.get('password')
    
    if not uid or not password:
        return jsonify({
            "success": False,
            "error": "Missing uid or password",
            "example": "/jwt?uid=4099382824&password=yourpass"
        }), 400
    
    print(f"🎮 Generating JWT for UID: {uid}")
    
    # স্টেপ 1: এক্সেস টোকেন
    open_id, access_token, error = get_access_token(uid, password)
    
    if error:
        return jsonify({"success": False, "error": error}), 401
    
    # স্টেপ 2: বিভিন্ন প্ল্যাটফর্ম চেষ্টা
    platforms = [2, 3, 4, 6, 8]
    
    for pt in platforms:
        print(f"Trying platform {pt}...")
        jwt_token = major_login(open_id, access_token, pt)
        if jwt_token:
            return jsonify({
                "success": True,
                "uid": uid,
                "open_id": open_id,
                "jwt_token": jwt_token,
                "platform_used": pt
            })
    
    return jsonify({
        "success": False,
        "error": "MajorLogin failed on all platforms",
        "uid": uid,
        "open_id": open_id
    }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
