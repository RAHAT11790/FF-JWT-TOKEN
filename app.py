#RIZER EMOTE EQUIP
#EQUIPS HI EMOTE FOR GUEST IDS
# MADE BY RIZER
# FUCK YOU IF YOU TAKE MY CREDIT
# LEAK_OB53
import base64
import json
import requests
import struct
from datetime import datetime
from flask import Flask, request, jsonify
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

EMOTE_DATA_HEX = "CA F6 83 22 2A 25 C7 BE FE B5 1F 59 54 4D B3 13"
EMOTE_DATA = bytes.fromhex(EMOTE_DATA_HEX.replace(" ", ""))

REGION_SERVER_MAP = {
    "BD": "https://clientbp.ggpolarbear.com",
    "IND": "https://client.ind.freefiremobile.com",
    "PK": "https://clientbp.ggpolarbear.com",
    "ME": "https://clientbp.ggpolarbear.com",
    "VN": "https://clientbp.ggpolarbear.com",
    "SG": "https://clientbp.ggpolarbear.com",
    "ID": "https://clientbp.ggpolarbear.com",
    "TH": "https://clientbp.ggpolarbear.com",
    "BR": "https://client.us.freefiremobile.com",
    "NA": "https://client.us.freefiremobile.com",
    "US": "https://client.us.freefiremobile.com",
    "RU": "https://clientbp.ggpolarbear.com",
}

BASE_HEADERS = {
    "Accept-Encoding": "gzip",
    "Connection": "Keep-Alive",
    "Content-Type": "application/x-www-form-urlencoded",
    "Expect": "100-continue",
    "ReleaseVersion": "OB53",
    "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; G011A Build/PI)",
    "X-GA": "v1 1",
    "X-Unity-Version": "2018.4.11f1",
}

OWNER_SIGNATURE = " made by RIZERx64✅"
MADE_BY_SIGNATURE = "RIZER🌃🆗"

OAUTH_URL = "https://100067.connect.garena.com/oauth/guest/token/grant"
MAJOR_LOGIN_URL = "https://loginbp.ggblueshark.com/MajorLogin"
CLIENT_ID = "100067"
CLIENT_SECRET = "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"

AES_KEY = b'Yg&tc%DEuh6%Zc^8'
AES_IV = b'6oyZDr22E3ychjM%'

_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x13MajorLoginReq.proto\"\xfa\n\n\nMajorLogin\x12\x12\n\nevent_time\x18\x03 \x01(\t\x12\x11\n\tgame_name\x18\x04 \x01(\t\x12\x13\n\x0bplatform_id\x18\x05 \x01(\x05\x12\x16\n\x0e\x63lient_version\x18\x07 \x01(\t\x12\x17\n\x0fsystem_software\x18\x08 \x01(\t\x12\x17\n\x0fsystem_hardware\x18\t \x01(\t\x12\x18\n\x10telecom_operator\x18\n \x01(\t\x12\x14\n\x0cnetwork_type\x18\x0b \x01(\t\x12\x14\n\x0cscreen_width\x18\x0c \x01(\r\x12\x15\n\rscreen_height\x18\r \x01(\r\x12\x12\n\nscreen_dpi\x18\x0e \x01(\t\x12\x19\n\x11processor_details\x18\x0f \x01(\t\x12\x0e\n\x06memory\x18\x10 \x01(\r\x12\x14\n\x0cgpu_renderer\x18\x11 \x01(\t\x12\x13\n\x0bgpu_version\x18\x12 \x01(\t\x12\x18\n\x10unique_device_id\x18\x13 \x01(\t\x12\x11\n\tclient_ip\x18\x14 \x01(\t\x12\x10\n\x08language\x18\x15 \x01(\t\x12\x0f\n\x07open_id\x18\x16 \x01(\t\x12\x14\n\x0copen_id_type\x18\x17 \x01(\t\x12\x13\n\x0b\x64\x65vice_type\x18\x18 \x01(\t\x12\'\n\x10memory_available\x18\x19 \x01(\x0b\x32\r.GameSecurity\x12\x14\n\x0c\x61\x63\x63\x65ss_token\x18\x1d \x01(\t\x12\x17\n\x0fplatform_sdk_id\x18\x1e \x01(\x05\x12\x1a\n\x12network_operator_a\x18) \x01(\t\x12\x16\n\x0enetwork_type_a\x18* \x01(\t\x12\x1c\n\x14\x63lient_using_version\x18\x39 \x01(\t\x12\x1e\n\x16\x65xternal_storage_total\x18< \x01(\x05\x12\"\n\x1a\x65xternal_storage_available\x18= \x01(\x05\x12\x1e\n\x16internal_storage_total\x18> \x01(\x05\x12\"\n\x1ainternal_storage_available\x18? \x01(\x05\x12#\n\x1bgame_disk_storage_available\x18@ \x01(\x05\x12\x1f\n\x17game_disk_storage_total\x18\x41 \x01(\x05\x12%\n\x1d\x65xternal_sdcard_avail_storage\x18\x42 \x01(\x05\x12%\n\x1d\x65xternal_sdcard_total_storage\x18\x43 \x01(\x05\x12\x10\n\x08login_by\x18I \x01(\x05\x12\x14\n\x0clibrary_path\x18J \x01(\t\x12\x12\n\nreg_avatar\x18L \x01(\x05\x12\x15\n\rlibrary_token\x18M \x01(\t\x12\x14\n\x0c\x63hannel_type\x18N \x01(\x05\x12\x10\n\x08\x63pu_type\x18O \x01(\x05\x12\x18\n\x10\x63pu_architecture\x18Q \x01(\t\x12\x1b\n\x13\x63lient_version_code\x18S \x01(\t\x12\x14\n\x0cgraphics_api\x18V \x01(\t\x12\x1d\n\x15supported_astc_bitset\x18W \x01(\r\x12\x1a\n\x12login_open_id_type\x18X \x01(\x05\x12\x18\n\x10\x61nalytics_detail\x18Y \x01(\x0c\x12\x14\n\x0cloading_time\x18\\ \x01(\r\x12\x17\n\x0frelease_channel\x18] \x01(\t\x12\x12\n\nextra_info\x18^ \x01(\t\x12 \n\x18\x61ndroid_engine_init_flag\x18_ \x01(\r\x12\x0f\n\x07if_push\x18\x61 \x01(\x05\x12\x0e\n\x06is_vpn\x18\x62 \x01(\x05\x12\x1c\n\x14origin_platform_type\x18\x63 \x01(\t\x12\x1d\n\x15primary_platform_type\x18\x64 \x01(\t\"5\n\x0cGameSecurity\x12\x0f\n\x07version\x18\x06 \x01(\x05\x12\x14\n\x0chidden_value\x18\x08 \x01(\x04\x62\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'MajorLoginReq_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_MAJORLOGIN']._serialized_start = 24
  _globals['_MAJORLOGIN']._serialized_end = 1426
  _globals['_GAMESECURITY']._serialized_start = 1428
  _globals['_GAMESECURITY']._serialized_end = 1481
MajorLogin = _globals['MajorLogin']
GameSecurity = _globals['GameSecurity']

DESCRIPTOR2 = _descriptor_pool.Default().AddSerializedFile(b'\n\x13MajorLoginRes.proto\"|\n\rMajorLoginRes\x12\x13\n\x0b\x61\x63\x63ount_uid\x18\x01 \x01(\x04\x12\x0e\n\x06region\x18\x02 \x01(\t\x12\r\n\x05token\x18\x08 \x01(\t\x12\x0b\n\x03url\x18\n \x01(\t\x12\x11\n\ttimestamp\x18\x15 \x01(\x03\x12\x0b\n\x03key\x18\x16 \x01(\x0c\x12\n\n\x02iv\x18\x17 \x01(\x0c\x62\x06proto3')
_globals2 = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR2, _globals2)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR2, 'MajorLoginRes_pb2', _globals2)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR2._loaded_options = None
  _globals2['_MAJORLOGINRES']._serialized_start = 23
  _globals2['_MAJORLOGINRES']._serialized_end = 147
MajorLoginRes = _globals2['MajorLoginRes']

def encrypt_aes(data: bytes) -> bytes:
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    return cipher.encrypt(pad(data, AES.block_size))

def decrypt_aes(data: bytes) -> bytes:
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    return unpad(cipher.decrypt(data), AES.block_size)

def try_decrypt_body(body: bytes) -> bytes:
    if len(body) % 16 == 0:
        try:
            return decrypt_aes(body)
        except Exception:
            pass
    return body

def parse_protobuf_to_dict(data: bytes) -> any:
    def decode_varint(buf, pos):
        result = 0
        shift = 0
        while pos < len(buf):
            byte = buf[pos]
            result |= (byte & 0x7F) << shift
            pos += 1
            if not (byte & 0x80):
                break
            shift += 7
        return result, pos

    def parse_value(wire_type, buf, pos):
        if wire_type == 0:  
            val, new_pos = decode_varint(buf, pos)
            return val, new_pos
        elif wire_type == 1:  
            val = struct.unpack('<d', buf[pos:pos+8])[0]
            return val, pos + 8
        elif wire_type == 2:  
            length, new_pos = decode_varint(buf, pos)
            value_bytes = buf[new_pos:new_pos+length]
            new_pos += length
            try:
                sub_dict = parse_protobuf_to_dict(value_bytes)
                if sub_dict:
                    return sub_dict, new_pos
            except:
                pass
            return value_bytes.hex(), new_pos
        elif wire_type == 5:  
            val = struct.unpack('<f', buf[pos:pos+4])[0]
            return val, pos + 4
        return None, pos

    result = {}
    pos = 0
    while pos < len(data):
        if pos >= len(data):
            break
        tag, pos = decode_varint(data, pos)
        if pos >= len(data):
            break
        field_number = tag >> 3
        wire_type = tag & 0x07
        val, pos = parse_value(wire_type, data, pos)
        if field_number in result:
            if not isinstance(result[field_number], list):
                result[field_number] = [result[field_number]]
            result[field_number].append(val)
        else:
            result[field_number] = val
    return result

def format_body_preview(body: bytes) -> str:
    if not body:
        return ""
    decrypted = try_decrypt_body(body)
    if decrypted != body:
        try:
            parsed = parse_protobuf_to_dict(decrypted)
            if parsed:
                return json.dumps(parsed, indent=2)
        except:
            pass
        try:
            return decrypted.decode('utf-8')
        except:
            return decrypted.hex()
    try:
        parsed = parse_protobuf_to_dict(body)
        if parsed:
            return json.dumps(parsed, indent=2)
    except:
        pass
    try:
        text = body.decode('utf-8')
        if all(32 <= c < 127 or c in (9, 10, 13) for c in text):
            return text
        return text
    except:
        return body.hex()

def build_major_login_payload(open_id: str, access_token: str, platform_type: int) -> bytes:
    major = MajorLogin()
    major.event_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    major.game_name = "free fire"
    major.platform_id = 1
    major.client_version = "1.123.1"
    major.system_software = "Android OS 9 / API-28 (PQ3B.190801.10101846/G9650ZHU2ARC6)"
    major.system_hardware = "Handheld"
    major.telecom_operator = "Verizon"
    major.network_type = "WIFI"
    major.screen_width = 1920
    major.screen_height = 1080
    major.screen_dpi = "280"
    major.processor_details = "ARM64 FP ASIMD AES VMH | 2865 | 4"
    major.memory = 3003
    major.gpu_renderer = "Adreno (TM) 640"
    major.gpu_version = "OpenGL ES 3.1 v1.46"
    major.unique_device_id = "Google|34a7dcdf-a7d5-4cb6-8d7e-3b0e448a0c57"
    major.client_ip = "223.191.51.89"
    major.language = "en"
    major.open_id = open_id
    major.open_id_type = "4"
    major.device_type = "Handheld"
    major.memory_available.version = 55
    major.memory_available.hidden_value = 81
    major.access_token = access_token
    major.platform_sdk_id = 1
    major.network_operator_a = "Verizon"
    major.network_type_a = "WIFI"
    major.client_using_version = "7428b253defc164018c604a1ebbfebdf"
    major.external_storage_total = 36235
    major.external_storage_available = 31335
    major.internal_storage_total = 2519
    major.internal_storage_available = 703
    major.game_disk_storage_available = 25010
    major.game_disk_storage_total = 26628
    major.external_sdcard_avail_storage = 32992
    major.external_sdcard_total_storage = 36235
    major.login_by = 3
    major.library_path = "/data/app/com.dts.freefireth-YPKM8jHEwAJlhpmhDhv5MQ==/lib/arm64"
    major.reg_avatar = 1
    major.library_token = "5b892aaabd688e571f688053118a162b|/data/app/com.dts.freefireth-YPKM8jHEwAJlhpmhDhv5MQ==/base.apk"
    major.channel_type = 3
    major.cpu_type = 2
    major.cpu_architecture = "64"
    major.client_version_code = "2019118695"
    major.graphics_api = "OpenGLES2"
    major.supported_astc_bitset = 16383
    major.login_open_id_type = 4
    major.analytics_detail = b"FwQVTgUPX1UaUllDDwcWCRBpWA0FUgsvA1snWlBaO1kFYg=="
    major.loading_time = 13564
    major.release_channel = "android"
    major.extra_info = "KqsHTymw5/5GB23YGniUYN2/q47GATrq7eFeRatf0NkwLKEMQ0PK5BKEk72dPflAxUlEBir6Vtey83XqF593qsl8hwY="
    major.android_engine_init_flag = 110009
    major.if_push = 1
    major.is_vpn = 1
    major.origin_platform_type = str(platform_type)
    major.primary_platform_type = str(platform_type)
    return major.SerializeToString()

def perform_major_login(open_id: str, access_token: str, platform_type: int):
    payload = build_major_login_payload(open_id, access_token, platform_type)
    encrypted_payload = encrypt_aes(payload)
    try:
        resp = requests.post(MAJOR_LOGIN_URL, data=encrypted_payload, headers=BASE_HEADERS, timeout=15, verify=False)
        if resp.status_code != 200:
            return None
        data = resp.content
        if len(data) % 16 == 0:
            try:
                decrypted = decrypt_aes(data)
                res = MajorLoginRes()
                res.ParseFromString(decrypted)
                if res.token:
                    return {
                        "account_uid": str(res.account_uid),
                        "region": res.region,
                        "token": res.token,
                        "url": res.url,
                        "timestamp": res.timestamp,
                        "key": res.key.hex() if res.key else None,
                        "iv": res.iv.hex() if res.iv else None
                    }
            except:
                pass
        try:
            res = MajorLoginRes()
            res.ParseFromString(data)
            if res.token:
                return {
                    "account_uid": str(res.account_uid),
                    "region": res.region,
                    "token": res.token,
                    "url": res.url,
                    "timestamp": res.timestamp,
                    "key": res.key.hex() if res.key else None,
                    "iv": res.iv.hex() if res.iv else None
                }
        except:
            pass
        return None
    except Exception as e:
        return None

def major_login_with_retry(open_id: str, access_token: str):
    for pt in [2, 3, 4, 6, 8]:
        result = perform_major_login(open_id, access_token, pt)
        if result:
            result["platform_type_used"] = pt
            return result
    return None

def generate_access_token(uid: str, password: str):
    headers = {
        "Host": "100067.connect.garena.com",
        "User-Agent": "GarenaMSDK/5.5.2P3(SM-A515F;Android 12;en-US;IND;)",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "close"
    }
    data = {
        "uid": uid, "password": password, "response_type": "token",
        "client_type": "2", "client_secret": CLIENT_SECRET, "client_id": CLIENT_ID
    }
    try:
        resp = requests.post(OAUTH_URL, headers=headers, data=data, timeout=15, verify=False)
        if resp.status_code == 200:
            resp_data = resp.json()
            return resp_data.get("open_id"), resp_data.get("access_token"), None
        else:
            try:
                error_data = resp.json()
                return None, None, f"HTTP {resp.status_code}: {error_data}"
            except:
                return None, None, f"HTTP {resp.status_code}: {resp.text[:200]}"
    except Exception as e:
        return None, None, str(e)

def inspect_token(access_token: str):
    url = f"https://100067.connect.garena.com/oauth/token/inspect?token={access_token}"
    try:
        resp = requests.get(url, timeout=10, verify=False)
        if resp.status_code == 200:
            return resp.json().get("open_id"), None
        return None, f"Inspect failed HTTP {resp.status_code}"
    except Exception as e:
        return None, str(e)

def decode_jwt_payload(token):
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None
        payload_b64 = parts[1]
        payload_b64 += '=' * ((4 - len(payload_b64) % 4) % 4)
        payload_bytes = base64.urlsafe_b64decode(payload_b64)
        return json.loads(payload_bytes)
    except Exception:
        return None

def get_region_from_payload(payload):
    return payload.get("noti_region") or payload.get("lock_region")

def select_server_url(region):
    return REGION_SERVER_MAP.get(region)

def send_emote_request(jwt, base_url):
    url = f"{base_url}/ChooseEmote"
    headers = BASE_HEADERS.copy()
    headers["Authorization"] = f"Bearer {jwt}"
    return requests.post(url, headers=headers, data=EMOTE_DATA)

def build_response(success, region, status_code, body, error_msg=None):
    body_preview = format_body_preview(body)
    response_data = {
        "success": success,
        "region": region,
        "status_code": status_code,
        "body_preview": body_preview,
        "owner": OWNER_SIGNATURE,
        "made_by": MADE_BY_SIGNATURE,
    }
    if error_msg:
        response_data["error"] = error_msg
    if "BR_INVENTORY_NOT_ENOUGH_ITEMS" in body_preview:
        response_data["hint"] = "EMOTE Not in the vault please buy it✅🤝"
    return jsonify(response_data)

def perform_emote_flow(jwt_token):
    payload = decode_jwt_payload(jwt_token)
    if not payload:
        return build_response(False, "unknown", 400, b"", "Invalid JWT token")
    region = get_region_from_payload(payload)
    if not region:
        return build_response(False, "unknown", 400, b"", "Region not found in JWT")
    server_url = select_server_url(region)
    if not server_url:
        return build_response(False, region, 400, b"", f"No server configured for region {region}")
    try:
        resp = send_emote_request(jwt_token, server_url)
    except requests.exceptions.RequestException as e:
        return build_response(False, region, 500, b"", f"Request failed: {str(e)}")
    success = resp.status_code == 200
    return build_response(success, region, resp.status_code, resp.content)

@app.route('/rizer', methods=['GET'])
def rizer_endpoint():
    if request.args.get('emote_enquip') is None:
        return jsonify({
            "error": "Missing 'emote_enquip' parameter",
            "owner": OWNER_SIGNATURE,
            "made_by": MADE_BY_SIGNATURE
        }), 400

    jwt_token = request.args.get('jwt_token')
    if jwt_token:
        return perform_emote_flow(jwt_token)

    uid = request.args.get('uid')
    password = request.args.get('password')
    if uid and password:
        open_id, access_token, error = generate_access_token(uid, password)
        if error:
            return jsonify({
                "success": False,
                "error": f"Authentication failed: {error}",
                "owner": OWNER_SIGNATURE,
                "made_by": MADE_BY_SIGNATURE
            }), 401
        login_result = major_login_with_retry(open_id, access_token)
        if not login_result:
            return jsonify({
                "success": False,
                "error": "MajorLogin failed after all platform attempts",
                "owner": OWNER_SIGNATURE,
                "made_by": MADE_BY_SIGNATURE
            }), 500
        jwt = login_result["token"]
        emote_response = perform_emote_flow(jwt)
        data = emote_response.get_json()
        data["jwt_token"] = jwt
        data["account_uid"] = login_result["account_uid"]
        data["login_region"] = login_result["region"]
        data["platform_type_used"] = login_result.get("platform_type_used")
        return jsonify(data)

    access_token = request.args.get('access_token')
    if access_token:
        open_id, inspect_error = inspect_token(access_token)
        if inspect_error:
            return jsonify({
                "success": False,
                "error": f"Token inspect failed: {inspect_error}",
                "owner": OWNER_SIGNATURE,
                "made_by": MADE_BY_SIGNATURE
            }), 400
        login_result = major_login_with_retry(open_id, access_token)
        if not login_result:
            return jsonify({
                "success": False,
                "error": "MajorLogin failed after all platform attempts",
                "owner": OWNER_SIGNATURE,
                "made_by": MADE_BY_SIGNATURE
            }), 500
        jwt = login_result["token"]
        emote_response = perform_emote_flow(jwt)
        data = emote_response.get_json()
        data["jwt_token"] = jwt
        data["account_uid"] = login_result["account_uid"]
        data["login_region"] = login_result["region"]
        data["platform_type_used"] = login_result.get("platform_type_used")
        return jsonify(data)

    return jsonify({
        "error": "Missing parameters. Provide jwt_token, uid+password, or access_token.",
        "owner": OWNER_SIGNATURE,
        "made_by": MADE_BY_SIGNATURE
    }), 400

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "message": "RIZER Emote equip API is and Fuhx FF Gay",
        "endpoints": {
            "/rizer?emote_enquip&jwt_token=<JWT>": "Direct emote request",
            "/rizer?emote_enquip&uid=<UID>&password=<PASS>": "Guest login + emote",
            "/rizer?emote_enquip&access_token=<TOKEN>": "Access token login + emote"
        },
        "owner": OWNER_SIGNATURE,
        "made_by": MADE_BY_SIGNATURE
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=False)