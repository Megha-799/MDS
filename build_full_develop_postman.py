#!/usr/bin/env python3
"""
Generates the Complete Master Data Service (MDS) Postman Collection
Targeting the Develop Server:
  - Backend API: https://master-data.development.oanstaging.com
  - Keycloak IAM: https://keycloak.development.oanstaging.com (staff realm)
"""

import urllib.request
import json
import uuid
import sys

print("1. Fetching OpenAPI specification from develop server...")
req = urllib.request.Request("https://master-data.development.oanstaging.com/openapi.json")
with urllib.request.urlopen(req) as resp:
    spec = json.loads(resp.read().decode("utf-8"))

schemas = spec.get("components", {}).get("schemas", {})

def resolve_schema(s):
    if not s or not isinstance(s, dict):
        return {}
    if "$ref" in s:
        ref_name = s["$ref"].split("/")[-1]
        return resolve_schema(schemas.get(ref_name, {}))
    if "anyOf" in s:
        for opt in s["anyOf"]:
            if opt.get("type") != "null":
                return resolve_schema(opt)
    return s

def get_sample_value(name, prop_schema):
    name_lower = name.lower()
    schema = resolve_schema(prop_schema)
    stype = schema.get("type", "string")

    if "list_code" in name_lower:
        return "{{sample_list_code}}"
    if "value_code" in name_lower:
        return "{{sample_value_code}}"
    if "parent_unit_id" in name_lower:
        return "{{sample_geo_code}}"
    if "unit_id" in name_lower:
        return "{{sample_geo_code}}"
    if name_lower == "level" or "level_id" in name_lower:
        return "{{sample_geo_level}}"
    if "release" in name_lower and "code" in name_lower:
        return "ETH-2026-Q1"
    if "version_no" in name_lower or "version" in name_lower:
        return 1
    if "page_size" in name_lower:
        return 20
    if "current_page" in name_lower:
        return 1
    if "request_id" in name_lower:
        return "req-{{$randomUUID}}"
    if "request_timestamp" in name_lower:
        return "2026-11-03T10:00:00Z"
    if "sender_app_mnemonic" in name_lower:
        return "postman-qa"
    if "sender_app_url" in name_lower:
        return "https://postman.local"
    if "licence_label" in name_lower:
        return "CC BY 4.0"
    if "licence_uri" in name_lower:
        return "https://creativecommons.org/licenses/by/4.0/"
    if "approval_ref" in name_lower:
        return "MOA-REF-2026-001"
    if "decision_note" in name_lower:
        return "Approved by Ministry of Agriculture for staging deployment"
    if "change_note" in name_lower:
        return "Reference data update for testing"
    if "owner_org" in name_lower:
        return "Ministry of Agriculture"
    if "domain" in name_lower:
        return "agriculture"
    if "visibility" in name_lower:
        return "private"
    if "display" in name_lower or "title" in name_lower:
        return "Sample Test Catalog"
    if "description" in name_lower or "note" in name_lower:
        return "Sample dataset description for develop environment verification"
    if "is_hierarchical" in name_lower:
        return False
    if "include_retired" in name_lower:
        return False
    if "search" in name_lower:
        return None
    if "as_of" in name_lower:
        return None
    if name_lower == "values" and stype == "array":
        return [{"value_code": "SAMPLE_VAL_01", "display": "Sample Value 1", "status": "ACTIVE"}]
    if name_lower == "units" and stype == "array":
        return [{"unit_id": "ET04", "name": "Oromia", "level": "region"}]
    if name_lower == "levels" and stype == "array":
        return [{"level_id": "region", "level_name": "Region", "level_order": 1}]
    if name_lower == "attribute_schema":
        return {"type": "object", "properties": {"description": {"type": "string"}}}
    if name_lower == "attribute_filters":
        return None

    if stype == "string":
        return f"sample_{name}"
    if stype == "integer" or stype == "number":
        return 1
    if stype == "boolean":
        return True
    if stype == "array":
        return []
    if stype == "object":
        return {}
    return None

def build_envelope_for_endpoint(path, post_info):
    req_body_info = post_info.get("requestBody", {})
    json_content = req_body_info.get("content", {}).get("application/json", {})
    schema_ref = json_content.get("schema", {})
    resolved_schema = resolve_schema(schema_ref)
    
    props = resolved_schema.get("properties", {})
    
    # Check if OpenG2P envelope wrapper exists
    if "request_header" in props and "request_body" in props:
        rb_schema = resolve_schema(props["request_body"])
        rb_props = rb_schema.get("properties", {})
        payload_schema = resolve_schema(rb_props.get("request_payload", {}))
        
        inner_props = payload_schema.get("properties", {})
        payload_dict = {}
        for p_name, p_sch in inner_props.items():
            val = get_sample_value(p_name, p_sch)
            if val is not None:
                payload_dict[p_name] = val
                
        return {
            "request_header": {
                "sender_app_mnemonic": "postman-qa",
                "sender_app_url": "https://postman.local",
                "request_id": "req-{{$randomUUID}}",
                "request_timestamp": "2026-11-03T10:00:00Z"
            },
            "request_body": {
                "pagination_request": {
                    "current_page": 1,
                    "page_size": 20
                },
                "request_payload": payload_dict
            }
        }
    else:
        # Direct payload
        body_dict = {}
        for p_name, p_sch in props.items():
            val = get_sample_value(p_name, p_sch)
            if val is not None:
                body_dict[p_name] = val
        return body_dict

def categorize_endpoint(path):
    p = path.lower()
    if p == "/ping":
        return "7. System Health & Samples"
    if p.startswith("/samples"):
        return "7. System Health & Samples"
    if p.startswith("/attributes"):
        return "6. Legacy Attributes APIs"
    if p.startswith("/geo/"):
        return "6. Legacy Geo APIs"
    if "geo_draft" in p or "upload_draft_boundary" in p or "draft_levels" in p or "draft_units" in p or "geo_change" in p:
        return "4. Catalogue - Geography Lifecycle & Boundaries"
    if "get_geo_" in p:
        return "2. Catalogue - Geography Read & Cascading"
    if "release" in p:
        return "5. Catalogue - Releases & Snapshots"
    if any(k in p for k in ["create_list", "create_list_draft", "update_list", "submit_draft", "approve_draft", "reject_draft", "discard_draft", "upsert_draft_values", "retire_draft_values"]):
        return "3. Catalogue - Maker-Checker Lifecycle & Drafts"
    if p.startswith("/catalogue"):
        return "1. Catalogue - Core Read & Query"
    return "8. Other APIs"

collection = {
    "info": {
        "_postman_id": str(uuid.uuid4()),
        "name": "MDS Develop - Complete API Suite (All Endpoints)",
        "description": "Complete Postman testing suite containing ALL 65 APIs of the Master Data Service (MDS) targeting:\n- Backend API: https://master-data.development.oanstaging.com\n- Keycloak: https://keycloak.development.oanstaging.com\n- Realm: staff, Client: admin-cli, User: alex.carter\n\nAll requests include pre-filled parameter values, proper OpenG2P envelopes, and automated token handling.",
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
    },
    "variable": [
        {"key": "api_url", "value": "https://master-data.development.oanstaging.com", "type": "string"},
        {"key": "keycloak_url", "value": "https://keycloak.development.oanstaging.com", "type": "string"},
        {"key": "realm", "value": "staff", "type": "string"},
        {"key": "client_id", "value": "admin-cli", "type": "string"},
        {"key": "username", "value": "alex.carter", "type": "string"},
        {"key": "password", "value": "pass", "type": "string"},
        {"key": "admin_token", "value": "", "type": "string"},
        {"key": "sample_list_code", "value": "LIVESTOCK_SPECIES", "type": "string"},
        {"key": "sample_value_code", "value": "CATTLE", "type": "string"},
        {"key": "sample_geo_code", "value": "ET04", "type": "string"},
        {"key": "sample_geo_level", "value": "region", "type": "string"}
    ],
    "item": []
}

# 1. Auth folder
auth_folder = {
    "name": "0. Authentication & Tokens",
    "description": "Acquires Bearer token from Keycloak and automatically updates collection variables.",
    "item": [
        {
            "name": "0.1 Get Admin Access Token (alex.carter)",
            "event": [{
                "listen": "test",
                "script": {
                    "exec": [
                        "var jsonData = pm.response.json();",
                        "pm.test('Status is 200 OK', function () { pm.response.to.have.status(200); });",
                        "pm.test('Access token returned', function () { pm.expect(jsonData.access_token).to.be.a('string'); });",
                        "if (jsonData.access_token) {",
                        "    pm.collectionVariables.set('admin_token', jsonData.access_token);",
                        "    console.log('Stored admin_token successfully!');",
                        "}"
                    ],
                    "type": "text/javascript"
                }
            }],
            "request": {
                "method": "POST",
                "header": [{"key": "Content-Type", "value": "application/x-www-form-urlencoded"}],
                "body": {
                    "mode": "urlencoded",
                    "urlencoded": [
                        {"key": "grant_type", "value": "password", "type": "text"},
                        {"key": "client_id", "value": "{{client_id}}", "type": "text"},
                        {"key": "username", "value": "{{username}}", "type": "text"},
                        {"key": "password", "value": "{{password}}", "type": "text"}
                    ]
                },
                "url": {
                    "raw": "{{keycloak_url}}/realms/{{realm}}/protocol/openid-connect/token",
                    "host": ["{{keycloak_url}}"],
                    "path": ["realms", "{{realm}}", "protocol", "openid-connect", "token"]
                }
            }
        }
    ]
}

folder_buckets = {}

# Process all endpoints from OpenAPI
for path in sorted(spec.get("paths", {}).keys()):
    path_item = spec["paths"][path]
    cat = categorize_endpoint(path)
    if cat not in folder_buckets:
        folder_buckets[cat] = []
        
    for method in ["post", "get", "put", "delete"]:
        if method not in path_item:
            continue
        op = path_item[method]
        summary = op.get("summary") or path
        op_id = op.get("operationId") or path.replace("/", "_")
        req_name = f"{method.upper()} {path} - {summary}"
        
        path_segments = [seg for seg in path.split("/") if seg]
        url_raw = "{{api_url}}" + path
        
        headers = [
            {"key": "Authorization", "value": "Bearer {{admin_token}}"},
            {"key": "Content-Type", "value": "application/json"}
        ]
        
        req_obj = {
            "name": req_name,
            "event": [{
                "listen": "test",
                "script": {
                    "exec": [
                        "pm.test('Status code is 200', function () { pm.response.to.have.status(200); });",
                        "var jsonData = pm.response.json();",
                        "if (jsonData.response_header) {",
                        "    pm.test('Response status is SUCCESS', function () {",
                        "        pm.expect(jsonData.response_header.response_status).to.eql('SUCCESS');",
                        "    });",
                        "}"
                    ],
                    "type": "text/javascript"
                }
            }],
            "request": {
                "method": method.upper(),
                "header": headers,
                "url": {
                    "raw": url_raw,
                    "host": ["{{api_url}}"],
                    "path": path_segments
                },
                "description": op.get("description", "")
            }
        }
        
        if method.upper() == "POST":
            body_dict = build_envelope_for_endpoint(path, op)
            req_obj["request"]["body"] = {
                "mode": "raw",
                "raw": json.dumps(body_dict, indent=2)
            }
            
        folder_buckets[cat].append(req_obj)

# Assemble collection
collection["item"].append(auth_folder)

for cat_name in sorted(folder_buckets.keys()):
    collection["item"].append({
        "name": cat_name,
        "item": folder_buckets[cat_name]
    })

out_path = "/home/user/master-data-standalone/MDS_Complete_Develop_API_Collection.postman_collection.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(collection, f, indent=2)

print(f"Master Postman Collection successfully written to: {out_path}")
total_endpoints = sum(len(f["item"]) for f in collection["item"])
print(f"Total Folders: {len(collection['item'])}")
print(f"Total Requests configured: {total_endpoints}")
