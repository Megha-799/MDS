import urllib.request
import urllib.parse
import json
import sys

BASE_URL = "https://mds-api-dev.oanstaging.com"
KEYCLOAK_URL = "https://keycloak-dev.oanstaging.com"
REALM = "mds-develop"
CLIENT_ID = "master-data"
CLIENT_SECRET = "lqQVel10DTXO4u0gO76HxILY5kUcBVPt2WcnKEIA"

passed = 0
failed = 0

def log_test(name, success, detail=""):
    global passed, failed
    if success:
        passed += 1
        print(f" [PASS] {name} {detail}")
    else:
        failed += 1
        print(f" [FAIL] {name} - {detail}")

def get_token(grant_type="client_credentials", username=None, password=None):
    url = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/token"
    payload = {
        "grant_type": grant_type,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "openid profile email"
    }
    if username and password:
        payload["username"] = username
        payload["password"] = password
    data = urllib.parse.urlencode(payload).encode()
    req = urllib.request.Request(url, data=data)
    res = json.loads(urllib.request.urlopen(req).read().decode())
    return res["access_token"]

# 1. Test Auth
print("\n--- 1. Testing Authentication Endpoints ---")
try:
    m2m_token = get_token("client_credentials")
    log_test("M2M Client Credentials Token", True, f"(length: {len(m2m_token)})")
except Exception as e:
    log_test("M2M Client Credentials Token", False, str(e))

try:
    maker_token = get_token("password", "moa.maker", "OanEthiopia2026!")
    log_test("User Token: moa.maker", True)
except Exception as e:
    log_test("User Token: moa.maker", False, str(e))

try:
    checker_token = get_token("password", "moa.checker", "OanEthiopia2026!")
    log_test("User Token: moa.checker", True)
except Exception as e:
    log_test("User Token: moa.checker", False, str(e))

try:
    # UserInfo
    req = urllib.request.Request(
        f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/userinfo",
        headers={"Authorization": f"Bearer {maker_token}"}
    )
    uinfo = json.loads(urllib.request.urlopen(req).read().decode())
    log_test("GET /userinfo (moa.maker profile)", uinfo.get("preferred_username") == "moa.maker", f"({uinfo.get('name')})")
except Exception as e:
    log_test("GET /userinfo", False, str(e))

# 2. Test System & Public
print("\n--- 2. Testing System & Public Discovery Endpoints ---")
public_eps = [
    ("GET /ping", f"{BASE_URL}/ping"),
    ("GET /public/catalog", f"{BASE_URL}/public/catalog"),
    ("GET /public/datasets", f"{BASE_URL}/public/datasets"),
    ("GET /public/datasets/CROP_CATALOG", f"{BASE_URL}/public/datasets/CROP_CATALOG"),
    ("GET /public/datasets/CROP_CATALOG/entries", f"{BASE_URL}/public/datasets/CROP_CATALOG/entries"),
    ("GET /public/datasets/CROP_CATALOG/skos", f"{BASE_URL}/public/datasets/CROP_CATALOG/skos"),
    ("GET /public/datasets/CROP_CATALOG/download.csv", f"{BASE_URL}/public/datasets/CROP_CATALOG/download.csv?version=1"),
    ("GET /public/datasets/CROP_CATALOG/download.json", f"{BASE_URL}/public/datasets/CROP_CATALOG/download.json?version=1"),
    ("GET /public/geography", f"{BASE_URL}/public/geography"),
    ("GET /public/geography/levels", f"{BASE_URL}/public/geography/levels"),
    ("GET /public/geography/levels/region/units.csv", f"{BASE_URL}/public/geography/levels/region/units.csv?version=1"),
    ("GET /public/geography/levels/region/boundaries.geojson", f"{BASE_URL}/public/geography/levels/region/boundaries.geojson?version=1"),
    ("GET /public/geography/units", f"{BASE_URL}/public/geography/units"),
    ("GET /public/releases", f"{BASE_URL}/public/releases")
]

for name, url in public_eps:
    try:
        res = urllib.request.urlopen(urllib.request.Request(url))
        log_test(name, res.status == 200, f"({res.status})")
    except Exception as e:
        log_test(name, False, str(e))

# 3. Test Catalogue Query APIs
print("\n--- 3. Testing Core Catalogue Query APIs ---")
def call_mds_api(path, payload, token=m2m_token):
    body = {
        "request_header": {
            "sender_app_mnemonic": "Farmer",
            "sender_app_url": "https://farmer-registry.oanstaging.com",
            "request_id": "test-req-1234",
            "request_timestamp": "2026-10-22T05:50:00Z"
        },
        "request_body": payload
    }
    req = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    )
    return json.loads(urllib.request.urlopen(req).read().decode())

try:
    r = call_mds_api("/catalogue/get_catalogue_config", {"request_payload": {}})
    log_test("POST /catalogue/get_catalogue_config", r["response_header"]["response_status"] == "SUCCESS")
except Exception as e:
    log_test("POST /catalogue/get_catalogue_config", False, str(e))

try:
    r = call_mds_api("/catalogue/get_lists", {"request_payload": {"include_unpublished": True}})
    lists = r["response_body"]["response_payload"]["lists"]
    log_test("POST /catalogue/get_lists", r["response_header"]["response_status"] == "SUCCESS", f"({len(lists)} datasets found)")
except Exception as e:
    log_test("POST /catalogue/get_lists", False, str(e))

try:
    r = call_mds_api("/catalogue/get_list", {"request_payload": {"list_code": "CROP_CATALOG", "version": "latest"}})
    log_test("POST /catalogue/get_list (CROP_CATALOG)", r["response_header"]["response_status"] == "SUCCESS")
except Exception as e:
    log_test("POST /catalogue/get_list", False, str(e))

try:
    r = call_mds_api("/catalogue/get_list_values", {
        "pagination_request": {"current_page": 1, "page_size": 10},
        "request_payload": {"list_code": "CROP_CATALOG", "version": "latest", "include_retired": False}
    })
    vals = r["response_body"]["response_payload"]["values"]
    log_test("POST /catalogue/get_list_values (CROP_CATALOG)", r["response_header"]["response_status"] == "SUCCESS", f"({len(vals)} crops)")
except Exception as e:
    log_test("POST /catalogue/get_list_values (CROP_CATALOG)", False, str(e))

try:
    r = call_mds_api("/catalogue/get_list_values", {
        "pagination_request": {"current_page": 1, "page_size": 10},
        "request_payload": {"list_code": "INPUT_CATALOG", "version": "latest", "include_retired": False}
    })
    vals = r["response_body"]["response_payload"]["values"]
    log_test("POST /catalogue/get_list_values (INPUT_CATALOG)", r["response_header"]["response_status"] == "SUCCESS", f"({len(vals)} fertilizers)")
except Exception as e:
    log_test("POST /catalogue/get_list_values (INPUT_CATALOG)", False, str(e))

try:
    r = call_mds_api("/catalogue/get_geo_settings", {"request_payload": {}})
    log_test("POST /catalogue/get_geo_settings", r["response_header"]["response_status"] == "SUCCESS")
except Exception as e:
    log_test("POST /catalogue/get_geo_settings", False, str(e))

try:
    r = call_mds_api("/catalogue/get_geo_levels", {"request_payload": {}})
    levels = r["response_body"]["response_payload"]["levels"]
    log_test("POST /catalogue/get_geo_levels", r["response_header"]["response_status"] == "SUCCESS", f"({len(levels)} levels: l0..l3)")
except Exception as e:
    log_test("POST /catalogue/get_geo_levels", False, str(e))

try:
    r = call_mds_api("/catalogue/get_geo_units", {
        "pagination_request": {"current_page": 1, "page_size": 10},
        "request_payload": {"level_id": "l1"}
    })
    units = r["response_body"]["response_payload"]["units"]
    log_test("POST /catalogue/get_geo_units (l1 Regions)", r["response_header"]["response_status"] == "SUCCESS", f"({len(units)} units)")
except Exception as e:
    log_test("POST /catalogue/get_geo_units", False, str(e))

try:
    r = call_mds_api("/catalogue/get_geo_unit", {"request_payload": {"unit_id": "ET04"}})
    unit = r["response_body"]["response_payload"]["unit"]
    log_test("POST /catalogue/get_geo_unit (ET04 Oromia)", r["response_header"]["response_status"] == "SUCCESS", f"({unit['name']})")
except Exception as e:
    log_test("POST /catalogue/get_geo_unit", False, str(e))

print(f"\n==========================================")
print(f"Total Tests Passed: {passed} / {passed + failed}")
print(f"Total Tests Failed: {failed}")
print(f"==========================================")
