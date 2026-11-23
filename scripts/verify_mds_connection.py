#!/usr/bin/env python3
"""
MDS & Registry API Connection Verification Script
Compatible with Python 3.8+ (Zero external dependencies required)

Tests the live API connection between external Registries (Livestock, Crop, Farmer)
and the Master Data Service (MDS) via Keycloak Authentication.
"""

import sys
import json
import ssl
import argparse
import urllib.request
import urllib.error

# Environment presets
ENV_CONFIGS = {
    "local": {
        "name": "Local Docker Environment",
        "keycloak_url": "http://localhost/realms/staff/protocol/openid-connect/token",
        "keycloak_host": "keycloak.openg2p.localtest.me",
        "mds_api_url": "http://localhost",
        "mds_host": "commons-services-master-data-api.commons.svc.cluster.local",
        "client_id": "commons-services-staff-portal",
        "client_secret": "RzqU5DzHmEufjZIaQVIMqr8X31PWTp0l",
        "grant_type": "client_credentials",
    },
    "staging": {
        "name": "OAN Staging Environment",
        "keycloak_url": "https://keycloak.development.oanstaging.com/realms/staff/protocol/openid-connect/token",
        "keycloak_host": None,
        "mds_api_url": "https://master-data.development.oanstaging.com",
        "mds_host": None,
        "client_id": "admin-cli",
        "client_secret": None,
        "grant_type": "password",
    }
}

def create_ssl_context():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx

def get_token(config, username=None, password=None, token_override=None):
    if token_override:
        print("  [INFO] Using provided Bearer Token override.")
        return token_override

    print(f"  [1/2] Connecting to Keycloak: {config['keycloak_url']}...")
    
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    if config.get("keycloak_host"):
        headers["Host"] = config["keycloak_host"]

    if config["grant_type"] == "client_credentials":
        data = f"grant_type=client_credentials&client_id={config['client_id']}&client_secret={config['client_secret']}"
    else:
        if not username or not password:
            raise ValueError("Staging environment requires --username and --password (or pass existing --token)")
        data = f"grant_type=password&client_id={config['client_id']}&username={username}&password={password}"

    req = urllib.request.Request(config["keycloak_url"], data=data.encode("utf-8"), headers=headers)
    ctx = create_ssl_context()
    
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            token = body.get("access_token")
            if not token:
                raise ValueError("No access_token returned by Keycloak")
            print("  [SUCCESS] Token acquired successfully!")
            return token
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"Keycloak HTTP Error {e.code}: {err_msg}")
    except Exception as e:
        raise RuntimeError(f"Failed to connect to Keycloak: {e}")

def call_mds_rpc(config, token, endpoint, payload, page_size=50):
    url = f"{config['mds_api_url']}{endpoint}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    if config.get("mds_host"):
        headers["Host"] = config["mds_host"]

    envelope = {
        "request_header": {
            "sender_app_mnemonic": "livestock-registry",
            "sender_app_url": "http://livestock-registry.local",
            "request_id": "mds-verify-req",
            "request_timestamp": "2026-11-03T12:00:00Z"
        },
        "request_body": {
            "pagination_request": {
                "current_page": 1,
                "page_size": page_size
            },
            "request_payload": payload
        }
    }

    req = urllib.request.Request(url, data=json.dumps(envelope).encode("utf-8"), headers=headers)
    ctx = create_ssl_context()

    try:
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"MDS HTTP Error {e.code} on {endpoint}: {err_msg}")
    except Exception as e:
        raise RuntimeError(f"Failed to connect to MDS on {url}: {e}")

def run_verification(target="local", username=None, password=None, token_override=None):
    config = ENV_CONFIGS.get(target)
    if not config:
        print(f"Unknown target '{target}'. Use 'local' or 'staging'.")
        sys.exit(1)

    print("=" * 70)
    print(f"  MDS & REGISTRY API CONNECTION VERIFICATION")
    print(f"  Target Environment: {config['name']}")
    print(f"  MDS Endpoint Base : {config['mds_api_url']}")
    print("=" * 70)

    # 1. Acquire Token
    try:
        token = get_token(config, username, password, token_override)
    except Exception as e:
        print(f"\n  [FAILED] Keycloak Authentication Failed:\n    {e}\n")
        return False

    print("\n  [2/2] Testing Core Master Data Endpoints...")

    # Test cases to run
    test_cases = [
        {
            "name": "Livestock Species (LIVESTOCK_SPECIES)",
            "endpoint": "/catalogue/get_list_values",
            "payload": {"list_code": "LIVESTOCK_SPECIES"},
            "result_key": "values",
            "field": "value_id"
        },
        {
            "name": "Livestock Breeds (LIVESTOCK_BREED)",
            "endpoint": "/catalogue/get_list_values",
            "payload": {"list_code": "LIVESTOCK_BREED"},
            "result_key": "values",
            "field": "value_id"
        },
        {
            "name": "Body Condition Scores (LIVESTOCK_BODY_CONDITION)",
            "endpoint": "/catalogue/get_list_values",
            "payload": {"list_code": "LIVESTOCK_BODY_CONDITION"},
            "result_key": "values",
            "field": "value_id"
        },
        {
            "name": "Administrative Geography - Level 1 Regions (/catalogue/get_geo_units)",
            "endpoint": "/catalogue/get_geo_units",
            "payload": {"level": "region"},
            "result_key": "units",
            "field": "name"
        }
    ]

    all_passed = True
    for tc in test_cases:
        try:
            resp = call_mds_rpc(config, token, tc["endpoint"], tc["payload"])
            status = resp.get("response_header", {}).get("response_status", "UNKNOWN")
            payload = resp.get("response_body", {}).get("response_payload", {}) or {}
            items = payload.get(tc["result_key"], [])
            
            if status == "SUCCESS":
                sample = [str(x.get(tc["field"])) for x in items[:5]]
                sample_str = ", ".join(sample) + ("..." if len(items) > 5 else "")
                print(f"  ✓ {tc['name']}: {len(items)} items returned [{sample_str}]")
            else:
                err_code = resp.get("response_header", {}).get("response_error_code")
                err_msg = resp.get("response_header", {}).get("response_error_message")
                print(f"  ✗ {tc['name']} FAILED: {err_code} - {err_msg}")
                all_passed = False
        except Exception as e:
            print(f"  ✗ {tc['name']} ERROR: {e}")
            all_passed = False

    print("\n" + "=" * 70)
    if all_passed:
        print("  RESULT: ALL CONNECTION & CATALOG TESTS PASSED SUCCESSFULLY! (100%)")
        print("  Your registry configuration is fully connected and ready to sync data.")
    else:
        print("  RESULT: SOME ENDPOINTS FAILED. Check list_codes and permissions above.")
    print("=" * 70 + "\n")
    return all_passed

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verify MDS API Connection from local registry")
    parser.add_argument("--target", default="local", choices=["local", "staging"], help="Target environment (local or staging)")
    parser.add_argument("--username", help="Keycloak username (for staging)")
    parser.add_argument("--password", help="Keycloak password (for staging)")
    parser.add_argument("--token", help="Direct Bearer token override")
    args = parser.parse_args()

    success = run_verification(args.target, args.username, args.password, args.token)
    sys.exit(0 if success else 1)
