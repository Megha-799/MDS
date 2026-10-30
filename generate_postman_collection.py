import urllib.request
import json
import os
import uuid

print("Fetching OpenAPI schema from mds-api-dev...")
req = urllib.request.urlopen("https://mds-api-dev.oanstaging.com/openapi.json")
spec = json.loads(req.read().decode("utf-8"))

schemas = spec.get("components", {}).get("schemas", {})

def resolve_ref(ref):
    if not ref or not ref.startswith("#/components/schemas/"):
        return {}
    name = ref.replace("#/components/schemas/", "")
    return schemas.get(name, {})

def resolve_schema(s):
    if not s or not isinstance(s, dict):
        return {}
    if "$ref" in s:
        return resolve_schema(resolve_ref(s["$ref"]))
    if "anyOf" in s:
        for opt in s["anyOf"]:
            if opt.get("type") != "null":
                return resolve_schema(opt)
    return s

def build_sample_value(prop_name, prop_schema, depth=0):
    if depth > 4:
        return None
    prop_schema = resolve_schema(prop_schema)
    stype = prop_schema.get("type")
    
    if "example" in prop_schema:
        return prop_schema["example"]
    if "default" in prop_schema and prop_schema["default"] is not None:
        return prop_schema["default"]
        
    pname = prop_name.lower()
    
    if stype == "string":
        if "list_code" in pname or "dataset" in pname:
            return "{{sample_list_code}}"
        if "value_code" in pname or "entry_code" in pname:
            return "{{sample_entry_code}}"
        if "unit_id" in pname or "geo_code" in pname:
            return "{{sample_geo_code}}"
        if "level_id" in pname or "level" in pname:
            return "{{sample_geo_level}}"
        if "release_code" in pname or "release" in pname:
            return "{{sample_release_code}}"
        if "timestamp" in pname or "date" in pname or "effective" in pname:
            return "{{$isoTimestamp}}"
        if "id" in pname or "uuid" in pname:
            return "{{$guid}}"
        if "uri" in pname or "url" in pname:
            return "https://example.org"
        if "note" in pname or "reason" in pname or "decision" in pname:
            return "Automated test change"
        if "owner" in pname or "org" in pname:
            return "Ministry of Agriculture"
        if "domain" in pname:
            return "agriculture"
        if "display" in pname or "name" in pname:
            return "Test Display Name"
        if "enum" in prop_schema and prop_schema["enum"]:
            return prop_schema["enum"][0]
        return "sample_value"
        
    elif stype == "integer":
        if "version" in pname or "version_no" in pname:
            return 1
        if "current_page" in pname or "page" in pname:
            return 1
        if "page_size" in pname or "size" in pname or "limit" in pname:
            return 20
        return 1
        
    elif stype == "number":
        return 1.0
        
    elif stype == "boolean":
        if "retired" in pname:
            return False
        return True
        
    elif stype == "array":
        item_schema = resolve_schema(prop_schema.get("items", {}))
        return [build_sample_value(prop_name + "_item", item_schema, depth + 1)]
        
    elif stype == "object" or "properties" in prop_schema:
        obj = {}
        for k, sub_prop in prop_schema.get("properties", {}).items():
            obj[k] = build_sample_value(k, sub_prop, depth + 1)
        return obj
        
    return None

def build_request_body(path, op):
    rb = op.get("requestBody", {})
    if not rb:
        return None
    content = rb.get("content", {})
    json_content = content.get("application/json", {})
    schema = json_content.get("schema", {})
    if not schema:
        return None
        
    schema = resolve_schema(schema)
    props = schema.get("properties", {})
    
    # Check if standard envelope
    if "request_header" in props and "request_body" in props:
        req_body_schema = resolve_schema(props["request_body"])
        req_body_props = req_body_schema.get("properties", {})
        
        envelope = {
            "request_header": {
                "sender_app_mnemonic": "{{sender_app_mnemonic}}",
                "sender_app_url": "{{sender_app_url}}",
                "request_id": "{{$guid}}",
                "request_timestamp": "{{$isoTimestamp}}"
            },
            "request_body": {}
        }
        
        # Only include pagination for query/listing endpoints
        is_listing = any(term in path for term in ["get_lists", "get_list_values", "get_geo_units", "get_geo_levels", "get_attribute_values", "get_all_geo_levels", "get_geo_level_values", "get_all_attributes", "get_changes", "get_geo_changes", "get_releases"])
        if "pagination_request" in req_body_props and is_listing:
            envelope["request_body"]["pagination_request"] = {
                "current_page": 1,
                "page_size": 20,
                "sort_by": None,
                "filter_by": None,
                "search_text": None
            }
            
        if "request_payload" in req_body_props:
            payload_schema = resolve_schema(req_body_props["request_payload"])
            payload_obj = {}
            for k, sub_prop in payload_schema.get("properties", {}).items():
                val = build_sample_value(k, sub_prop)
                payload_obj[k] = val
            envelope["request_body"]["request_payload"] = payload_obj
        else:
            for k, sub_prop in req_body_props.items():
                if k != "pagination_request":
                    envelope["request_body"][k] = build_sample_value(k, sub_prop)
                    
        return envelope
    else:
        obj = {}
        for k, sub_prop in props.items():
            obj[k] = build_sample_value(k, sub_prop)
        return obj

def format_url(path):
    parts = []
    variables = []
    
    clean_path = path.lstrip("/")
    segments = clean_path.split("/")
    
    for seg in segments:
        if seg.startswith("{") and seg.endswith("}"):
            pname = seg[1:-1]
            parts.append(f":{pname}")
            val = "{{sample_list_code}}"
            if "entry" in pname:
                val = "{{sample_entry_code}}"
            elif "level" in pname:
                val = "{{sample_geo_level}}"
            elif "code" in pname:
                val = "{{sample_list_code}}"
            elif "release" in pname:
                val = "{{sample_release_code}}"
            variables.append({
                "key": pname,
                "value": val,
                "description": f"Path parameter {pname}"
            })
        else:
            parts.append(seg)
            
    url_obj = {
        "raw": "{{base_url}}/" + "/".join(parts),
        "host": ["{{base_url}}"],
        "path": parts
    }
    if variables:
        url_obj["variable"] = variables
    return url_obj

def get_folder_name(path, op):
    if path == "/ping":
        return "01. System & Health (Public)"
    if path.startswith("/public"):
        return "02. Open Catalogue (Anonymous / DCAT 3 / Public)"
    if path.startswith("/attributes"):
        return "09. Legacy Attributes API"
    if path.startswith("/geo"):
        return "10. Legacy Geography API"
    if path.startswith("/samples"):
        return "11. Samples API (Demo / Test)"
    if "awe" in path:
        return "12. Workflow Integration (AWE)"
    if "geo" in path:
        if any(w in path for w in ["draft", "change", "upload", "upsert", "retire", "boundary", "record", "delete_geo"]):
            return "07. Catalogue - Geography Drafts Workflow"
        else:
            return "06. Catalogue - Geography (Published)"
    if "release" in path:
        return "08. Catalogue - Releases Management"
    if path in ["/catalogue/get_list_values", "/catalogue/get_list_value", "/catalogue/upsert_draft_values", "/catalogue/retire_draft_values", "/catalogue/get_list_versions"]:
        return "05. Catalogue - Dataset Values / Entries"
    if any(w in path for w in ["_draft", "changes", "diff", "submit", "approve", "reject", "discard"]):
        return "04. Catalogue - Drafts & Four-Eyes Governance (Maker-Checker)"
    if path.startswith("/catalogue"):
        return "03. Catalogue - Datasets & Metadata"
    return "13. Other Endpoints"

collection = {
    "info": {
        "_postman_id": str(uuid.uuid4()),
        "name": "OpenG2P Master Data Service (MDS) Complete API Suite",
        "description": "Comprehensive Postman Collection covering 100% of the OpenG2P Master Data Service (MDS) APIs:\n\n1. **Authentication & Tokens**: Keycloak M2M Client Credentials and User Password Grants for Maker/Checker organizational hierarchy.\n2. **Public Open Catalogue**: DCAT-3 JSON-LD discovery, public datasets, SKOS concepts, CSV/GeoJSON exports, geography boundaries.\n3. **Catalogue Datasets & Metadata**: List registry, schemas, domains, ownership.\n4. **Maker-Checker Governance**: Four-eyes approval workflows (draft creation, submission, review, approval/rejection, change tracking).\n5. **Dataset Values & Entries**: Querying, versioning, batch upserts, retirement.\n6. **Administrative Geography**: Hierarchy from National (l0) down to Woreda (l3), polygon boundaries, crosswalks.\n7. **Catalogue Releases**: Version pinning and release packaging for agricultural data.\n8. **Legacy & Extension APIs**: Backward compatible Attributes and Geo endpoints.",
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
    },
    "auth": {
        "type": "bearer",
        "bearer": [
            {
                "key": "token",
                "value": "{{access_token}}",
                "type": "string"
            }
        ]
    },
    "event": [
        {
            "listen": "prerequest",
            "script": {
                "type": "text/javascript",
                "exec": [
                    "// OpenG2P Master Data Service Collection Pre-request Script"
                ]
            }
        },
        {
            "listen": "test",
            "script": {
                "type": "text/javascript",
                "exec": [
                    "// Check HTTP status code",
                    "pm.test(\"HTTP Status code is successful (200, 201)\", function () {",
                    "    pm.expect(pm.response.code).to.be.oneOf([200, 201]);",
                    "});",
                    "",
                    "// Check OpenG2P Envelope Response Status if returned",
                    "try {",
                    "    var res = pm.response.json();",
                    "    if (res.response_header && res.response_header.response_status) {",
                    "        pm.test(\"OpenG2P Response Status is SUCCESS\", function () {",
                    "            pm.expect(res.response_header.response_status).to.eql(\"SUCCESS\");",
                    "        });",
                    "    }",
                    "} catch (e) {}"
                ]
            }
        }
    ],
    "item": []
}

# 1. Folder: 00. Authentication & Tokens
auth_folder = {
    "name": "00. Authentication & Tokens",
    "description": "Keycloak Token endpoints for Machine-to-Machine (M2M) and User-based Maker/Checker access.",
    "item": [
        {
            "name": "01. M2M Token (Client Credentials - master-data)",
            "event": [
                {
                    "listen": "test",
                    "script": {
                        "type": "text/javascript",
                        "exec": [
                            "pm.test(\"M2M Token acquired successfully\", function () {",
                            "    pm.response.to.have.status(200);",
                            "    var json = pm.response.json();",
                            "    pm.expect(json.access_token).to.be.a('string');",
                            "    pm.environment.set(\"access_token\", json.access_token);",
                            "    console.log(\"Saved M2M access_token to environment!\");",
                            "});"
                        ]
                    }
                }
            ],
            "request": {
                "auth": {"type": "noauth"},
                "method": "POST",
                "header": [
                    {"key": "Content-Type", "value": "application/x-www-form-urlencoded"}
                ],
                "body": {
                    "mode": "urlencoded",
                    "urlencoded": [
                        {"key": "grant_type", "value": "client_credentials", "type": "text"},
                        {"key": "client_id", "value": "{{client_id}}", "type": "text"},
                        {"key": "client_secret", "value": "{{client_secret}}", "type": "text"},
                        {"key": "scope", "value": "openid profile email", "type": "text"}
                    ]
                },
                "url": {
                    "raw": "{{keycloak_url}}/realms/{{realm}}/protocol/openid-connect/token",
                    "host": ["{{keycloak_url}}"],
                    "path": ["realms", "{{realm}}", "protocol", "openid-connect", "token"]
                },
                "description": "Acquire M2M token for Registry-to-Registry / Partner Manager integration using master-data client."
            }
        },
        {
            "name": "02. User Token - MoA Maker (moa.maker)",
            "event": [
                {
                    "listen": "test",
                    "script": {
                        "type": "text/javascript",
                        "exec": [
                            "pm.test(\"MoA Maker token acquired\", function () {",
                            "    pm.response.to.have.status(200);",
                            "    var json = pm.response.json();",
                            "    pm.expect(json.access_token).to.be.a('string');",
                            "    pm.environment.set(\"access_token\", json.access_token);",
                            "    console.log(\"Saved moa.maker access_token!\");",
                            "});"
                        ]
                    }
                }
            ],
            "request": {
                "auth": {"type": "noauth"},
                "method": "POST",
                "header": [
                    {"key": "Content-Type", "value": "application/x-www-form-urlencoded"}
                ],
                "body": {
                    "mode": "urlencoded",
                    "urlencoded": [
                        {"key": "grant_type", "value": "password", "type": "text"},
                        {"key": "client_id", "value": "{{client_id}}", "type": "text"},
                        {"key": "client_secret", "value": "{{client_secret}}", "type": "text"},
                        {"key": "scope", "value": "openid profile email", "type": "text"},
                        {"key": "username", "value": "moa.maker", "type": "text"},
                        {"key": "password", "value": "{{user_password}}", "type": "text"}
                    ]
                },
                "url": {
                    "raw": "{{keycloak_url}}/realms/{{realm}}/protocol/openid-connect/token",
                    "host": ["{{keycloak_url}}"],
                    "path": ["realms", "{{realm}}", "protocol", "openid-connect", "token"]
                },
                "description": "Authenticate as Ministry of Agriculture (MoA) Maker to create and edit Crops, Seeds, and Fertilizer drafts."
            }
        },
        {
            "name": "03. User Token - MoA Checker (moa.checker)",
            "event": [
                {
                    "listen": "test",
                    "script": {
                        "type": "text/javascript",
                        "exec": [
                            "pm.test(\"MoA Checker token acquired\", function () {",
                            "    pm.response.to.have.status(200);",
                            "    var json = pm.response.json();",
                            "    pm.expect(json.access_token).to.be.a('string');",
                            "    pm.environment.set(\"access_token\", json.access_token);",
                            "    console.log(\"Saved moa.checker access_token!\");",
                            "});"
                        ]
                    }
                }
            ],
            "request": {
                "auth": {"type": "noauth"},
                "method": "POST",
                "header": [
                    {"key": "Content-Type", "value": "application/x-www-form-urlencoded"}
                ],
                "body": {
                    "mode": "urlencoded",
                    "urlencoded": [
                        {"key": "grant_type", "value": "password", "type": "text"},
                        {"key": "client_id", "value": "{{client_id}}", "type": "text"},
                        {"key": "client_secret", "value": "{{client_secret}}", "type": "text"},
                        {"key": "scope", "value": "openid profile email", "type": "text"},
                        {"key": "username", "value": "moa.checker", "type": "text"},
                        {"key": "password", "value": "{{user_password}}", "type": "text"}
                    ]
                },
                "url": {
                    "raw": "{{keycloak_url}}/realms/{{realm}}/protocol/openid-connect/token",
                    "host": ["{{keycloak_url}}"],
                    "path": ["realms", "{{realm}}", "protocol", "openid-connect", "token"]
                },
                "description": "Authenticate as MoA Checker to review, approve, or reject MoA catalog drafts."
            }
        },
        {
            "name": "04. User Token - LDI Specialist (ldi.specialist)",
            "event": [
                {
                    "listen": "test",
                    "script": {
                        "type": "text/javascript",
                        "exec": [
                            "pm.test(\"LDI Specialist token acquired\", function () {",
                            "    pm.response.to.have.status(200);",
                            "    var json = pm.response.json();",
                            "    pm.expect(json.access_token).to.be.a('string');",
                            "    pm.environment.set(\"access_token\", json.access_token);",
                            "});"
                        ]
                    }
                }
            ],
            "request": {
                "auth": {"type": "noauth"},
                "method": "POST",
                "header": [
                    {"key": "Content-Type", "value": "application/x-www-form-urlencoded"}
                ],
                "body": {
                    "mode": "urlencoded",
                    "urlencoded": [
                        {"key": "grant_type", "value": "password", "type": "text"},
                        {"key": "client_id", "value": "{{client_id}}", "type": "text"},
                        {"key": "client_secret", "value": "{{client_secret}}", "type": "text"},
                        {"key": "scope", "value": "openid profile email", "type": "text"},
                        {"key": "username", "value": "ldi.specialist", "type": "text"},
                        {"key": "password", "value": "{{user_password}}", "type": "text"}
                    ]
                },
                "url": {
                    "raw": "{{keycloak_url}}/realms/{{realm}}/protocol/openid-connect/token",
                    "host": ["{{keycloak_url}}"],
                    "path": ["realms", "{{realm}}", "protocol", "openid-connect", "token"]
                },
                "description": "Authenticate as Livestock Development Institute (LDI) Specialist."
            }
        },
        {
            "name": "05. User Token - CSA Admin (csa.admin)",
            "event": [
                {
                    "listen": "test",
                    "script": {
                        "type": "text/javascript",
                        "exec": [
                            "pm.test(\"CSA Admin token acquired\", function () {",
                            "    pm.response.to.have.status(200);",
                            "    var json = pm.response.json();",
                            "    pm.expect(json.access_token).to.be.a('string');",
                            "    pm.environment.set(\"access_token\", json.access_token);",
                            "});"
                        ]
                    }
                }
            ],
            "request": {
                "auth": {"type": "noauth"},
                "method": "POST",
                "header": [
                    {"key": "Content-Type", "value": "application/x-www-form-urlencoded"}
                ],
                "body": {
                    "mode": "urlencoded",
                    "urlencoded": [
                        {"key": "grant_type", "value": "password", "type": "text"},
                        {"key": "client_id", "value": "{{client_id}}", "type": "text"},
                        {"key": "client_secret", "value": "{{client_secret}}", "type": "text"},
                        {"key": "scope", "value": "openid profile email", "type": "text"},
                        {"key": "username", "value": "csa.admin", "type": "text"},
                        {"key": "password", "value": "{{user_password}}", "type": "text"}
                    ]
                },
                "url": {
                    "raw": "{{keycloak_url}}/realms/{{realm}}/protocol/openid-connect/token",
                    "host": ["{{keycloak_url}}"],
                    "path": ["realms", "{{realm}}", "protocol", "openid-connect", "token"]
                },
                "description": "Authenticate as Central Statistical Agency (CSA) Admin to manage administrative geography and boundaries."
            }
        },
        {
            "name": "06. Get Current User Info",
            "request": {
                "method": "GET",
                "header": [],
                "url": {
                    "raw": "{{keycloak_url}}/realms/{{realm}}/protocol/openid-connect/userinfo",
                    "host": ["{{keycloak_url}}"],
                    "path": ["realms", "{{realm}}", "protocol", "openid-connect", "userinfo"]
                },
                "description": "Inspect currently authenticated user profile and roles."
            }
        }
    ]
}

collection["item"].append(auth_folder)

# Map for organizing endpoints into folders
folder_map = {}

# Sort paths
all_paths = sorted(spec.get("paths", {}).keys())

for path in all_paths:
    path_item = spec["paths"][path]
    for method in ["get", "post", "put", "delete", "patch"]:
        if method not in path_item:
            continue
        op = path_item[method]
        summary = op.get("summary") or f"{method.upper()} {path}"
        description = op.get("description", "")
        folder_name = get_folder_name(path, op)
        
        if folder_name not in folder_map:
            folder_map[folder_name] = []
            
        req_item = {
            "name": f"{method.upper()} {path} - {summary}",
            "request": {
                "method": method.upper(),
                "header": [],
                "url": format_url(path),
                "description": description
            }
        }
        
        # Public or ping doesn't require auth
        if path == "/ping" or path.startswith("/public"):
            req_item["request"]["auth"] = {"type": "noauth"}
        
        # Handle body for POST/PUT
        if method in ["post", "put", "patch"]:
            body_obj = build_request_body(path, op)
            if body_obj is not None:
                req_item["request"]["header"].append({
                    "key": "Content-Type",
                    "value": "application/json"
                })
                req_item["request"]["body"] = {
                    "mode": "raw",
                    "raw": json.dumps(body_obj, indent=2),
                    "options": {
                        "raw": {
                            "language": "json"
                        }
                    }
                }
                
        folder_map[folder_name].append(req_item)

# Add folders in sorted order to collection
for folder_name in sorted(folder_map.keys()):
    collection["item"].append({
        "name": folder_name,
        "description": f"Endpoints in group {folder_name}",
        "item": folder_map[folder_name]
    })

collection_file = "/home/user/master-data-standalone/MDS_Postman_Collection.json"
with open(collection_file, "w", encoding="utf-8") as f:
    json.dump(collection, f, indent=2)

print(f"Collection generated: {collection_file}")
print(f"Total folders: {len(collection['item'])}")
total_reqs = sum(len(f.get("item", [])) for f in collection["item"])
print(f"Total requests in collection: {total_reqs}")

# Generate Environment files
dev_env = {
    "id": str(uuid.uuid4()),
    "name": "MDS - Develop Environment (oanstaging.com)",
    "values": [
        {"key": "base_url", "value": "https://mds-api-dev.oanstaging.com", "enabled": True},
        {"key": "keycloak_url", "value": "https://keycloak-dev.oanstaging.com", "enabled": True},
        {"key": "realm", "value": "mds-develop", "enabled": True},
        {"key": "client_id", "value": "master-data", "enabled": True},
        {"key": "client_secret", "value": "lqQVel10DTXO4u0gO76HxILY5kUcBVPt2WcnKEIA", "enabled": True},
        {"key": "username", "value": "moa.maker", "enabled": True},
        {"key": "user_password", "value": "OanEthiopia2026!", "enabled": True},
        {"key": "access_token", "value": "", "enabled": True},
        {"key": "sender_app_mnemonic", "value": "Farmer", "enabled": True},
        {"key": "sender_app_url", "value": "https://farmer-registry.oanstaging.com", "enabled": True},
        {"key": "sample_list_code", "value": "CROP_CATALOG", "enabled": True},
        {"key": "sample_entry_code", "value": "CROP_1", "enabled": True},
        {"key": "sample_geo_level", "value": "l1", "enabled": True},
        {"key": "sample_geo_code", "value": "ET04", "enabled": True},
        {"key": "sample_release_code", "value": "ETH-2026-Q1", "enabled": True}
    ],
    "_postman_variable_scope": "environment"
}

staging_env = {
    "id": str(uuid.uuid4()),
    "name": "MDS - Staging Environment (oanstaging.com)",
    "values": [
        {"key": "base_url", "value": "https://mds-api-staging.oanstaging.com", "enabled": True},
        {"key": "keycloak_url", "value": "https://keycloak-staging.oanstaging.com", "enabled": True},
        {"key": "realm", "value": "mds-staging", "enabled": True},
        {"key": "client_id", "value": "master-data", "enabled": True},
        {"key": "client_secret", "value": "lqQVel10DTXO4u0gO76HxILY5kUcBVPt2WcnKEIA", "enabled": True},
        {"key": "username", "value": "moa.maker", "enabled": True},
        {"key": "user_password", "value": "OanEthiopia2026!", "enabled": True},
        {"key": "access_token", "value": "", "enabled": True},
        {"key": "sender_app_mnemonic", "value": "Farmer", "enabled": True},
        {"key": "sender_app_url", "value": "https://farmer-registry.oanstaging.com", "enabled": True},
        {"key": "sample_list_code", "value": "CROP_CATALOG", "enabled": True},
        {"key": "sample_entry_code", "value": "CROP_1", "enabled": True},
        {"key": "sample_geo_level", "value": "l1", "enabled": True},
        {"key": "sample_geo_code", "value": "ET04", "enabled": True},
        {"key": "sample_release_code", "value": "ETH-2026-Q1", "enabled": True}
    ],
    "_postman_variable_scope": "environment"
}

with open("/home/user/master-data-standalone/MDS_Dev_Environment.postman_environment.json", "w", encoding="utf-8") as f:
    json.dump(dev_env, f, indent=2)

with open("/home/user/master-data-standalone/MDS_Staging_Environment.postman_environment.json", "w", encoding="utf-8") as f:
    json.dump(staging_env, f, indent=2)

print("Collection & Environment files successfully written!")
