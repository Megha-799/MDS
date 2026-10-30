import json

collection = {
    "info": {
        "_postman_id": "a1b2c3d4-e5f6-47a8-9b0c-1d2e3f4a5b6c",
        "name": "MDS QA & Registry API Testing Suite",
        "description": "Standard Postman collection for QA Testers and Registry Developers to test Master Data Service (MDS) APIs:\n\n1. Authentication (Maker / Checker / Admin tokens)\n2. Public Read-Only APIs for Registries (Farmer, Crop, Livestock)\n3. End-to-End Approval Workflow (Draft creation, Entry upsert, Submission, Approval)\n4. Negative & Governance Tests (Segregation of Duties enforcement)",
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
    },
    "variable": [
        {"key": "base_url", "value": "https://master-data-ui.development.oanstaging.com", "type": "string"},
        {"key": "api_url", "value": "http://localhost:8044", "type": "string"},
        {"key": "keycloak_url", "value": "https://keycloak.development.oanstaging.com", "type": "string"},
        {"key": "realm", "value": "staff", "type": "string"},
        {"key": "client_id", "value": "farmer-registry-staff-portal", "type": "string"},
        {"key": "list_code", "value": "CROP_CATALOG", "type": "string"},
        {"key": "test_value_code", "value": "TEST_CROP_QA_01", "type": "string"},
        {"key": "maker_token", "value": "", "type": "string"},
        {"key": "checker_token", "value": "", "type": "string"},
        {"key": "admin_token", "value": "", "type": "string"}
    ],
    "item": [
        {
            "name": "1. Authentication & Tokens",
            "item": [
                {
                    "name": "1.1 Get Maker Token (moa.maker)",
                    "event": [{
                        "listen": "test",
                        "script": {
                            "exec": [
                                "var jsonData = pm.response.json();",
                                "if (jsonData.access_token) {",
                                "    pm.collectionVariables.set('maker_token', jsonData.access_token);",
                                "    pm.test('Maker Token acquired successfully', function () {",
                                "        pm.expect(jsonData.access_token).to.be.a('string');",
                                "    });",
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
                                {"key": "client_id", "value": "{{client_id}}", "type": "text"},
                                {"key": "username", "value": "moa.maker", "type": "text"},
                                {"key": "password", "value": "admin1", "type": "text"},
                                {"key": "grant_type", "value": "password", "type": "text"}
                            ]
                        },
                        "url": {
                            "raw": "{{keycloak_url}}/realms/{{realm}}/protocol/openid-connect/token",
                            "host": ["{{keycloak_url}}"],
                            "path": ["realms", "{{realm}}", "protocol", "openid-connect", "token"]
                        }
                    }
                },
                {
                    "name": "1.2 Get Checker Token (moa.checker)",
                    "event": [{
                        "listen": "test",
                        "script": {
                            "exec": [
                                "var jsonData = pm.response.json();",
                                "if (jsonData.access_token) {",
                                "    pm.collectionVariables.set('checker_token', jsonData.access_token);",
                                "    pm.test('Checker Token acquired successfully', function () {",
                                "        pm.expect(jsonData.access_token).to.be.a('string');",
                                "    });",
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
                                {"key": "client_id", "value": "{{client_id}}", "type": "text"},
                                {"key": "username", "value": "moa.checker", "type": "text"},
                                {"key": "password", "value": "admin1", "type": "text"},
                                {"key": "grant_type", "value": "password", "type": "text"}
                            ]
                        },
                        "url": {
                            "raw": "{{keycloak_url}}/realms/{{realm}}/protocol/openid-connect/token",
                            "host": ["{{keycloak_url}}"],
                            "path": ["realms", "{{realm}}", "protocol", "openid-connect", "token"]
                        }
                    }
                },
                {
                    "name": "1.3 Get Admin Token (alex.carter)",
                    "event": [{
                        "listen": "test",
                        "script": {
                            "exec": [
                                "var jsonData = pm.response.json();",
                                "if (jsonData.access_token) {",
                                "    pm.collectionVariables.set('admin_token', jsonData.access_token);",
                                "    pm.test('Admin Token acquired successfully', function () {",
                                "        pm.expect(jsonData.access_token).to.be.a('string');",
                                "    });",
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
                                {"key": "client_id", "value": "{{client_id}}", "type": "text"},
                                {"key": "username", "value": "alex.carter", "type": "text"},
                                {"key": "password", "value": "admin1", "type": "text"},
                                {"key": "grant_type", "value": "password", "type": "text"}
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
        },
        {
            "name": "2. Public Registry APIs (Read-Only)",
            "item": [
                {
                    "name": "2.1 List All Published Catalogs",
                    "request": {
                        "method": "GET",
                        "header": [],
                        "url": {"raw": "{{api_url}}/public/datasets", "host": ["{{api_url}}"], "path": ["public", "datasets"]}
                    }
                },
                {
                    "name": "2.2 Get Entries for a Catalog",
                    "request": {
                        "method": "GET",
                        "header": [],
                        "url": {
                            "raw": "{{api_url}}/public/datasets/{{list_code}}/entries?page=1&limit=50",
                            "host": ["{{api_url}}"],
                            "path": ["public", "datasets", "{{list_code}}", "entries"],
                            "query": [
                                {"key": "page", "value": "1"},
                                {"key": "limit", "value": "50"}
                            ]
                        }
                    }
                },
                {
                    "name": "2.3 Download Catalog Dataset (JSON)",
                    "request": {
                        "method": "GET",
                        "header": [],
                        "url": {"raw": "{{api_url}}/public/datasets/{{list_code}}/download.json", "host": ["{{api_url}}"], "path": ["public", "datasets", "{{list_code}}", "download.json"]}
                    }
                },
                {
                    "name": "2.4 Download Catalog Dataset (CSV)",
                    "request": {
                        "method": "GET",
                        "header": [],
                        "url": {"raw": "{{api_url}}/public/datasets/{{list_code}}/download.csv", "host": ["{{api_url}}"], "path": ["public", "datasets", "{{list_code}}", "download.csv"]}
                    }
                },
                {
                    "name": "2.5 Get Administrative Geography Levels",
                    "request": {
                        "method": "GET",
                        "header": [],
                        "url": {"raw": "{{api_url}}/public/geography/levels", "host": ["{{api_url}}"], "path": ["public", "geography", "levels"]}
                    }
                },
                {
                    "name": "2.6 Get Administrative Geography Units",
                    "request": {
                        "method": "GET",
                        "header": [],
                        "url": {"raw": "{{api_url}}/public/geography/units", "host": ["{{api_url}}"], "path": ["public", "geography", "units"]}
                    }
                }
            ]
        },
        {
            "name": "3. Approval Workflow (Maker-Checker Lifecycle)",
            "item": [
                {
                    "name": "3.1 [All] Query Catalogs & Open Drafts",
                    "request": {
                        "method": "POST",
                        "header": [
                            {"key": "Authorization", "value": "Bearer {{maker_token}}"},
                            {"key": "Content-Type", "value": "application/json"}
                        ],
                        "body": {
                            "mode": "raw",
                            "raw": json.dumps({
                                "request_header": {
                                    "sender_app_mnemonic": "farmer-registry-staff-portal",
                                    "sender_app_url": "http://localhost:3005",
                                    "request_id": "{{$guid}}",
                                    "request_timestamp": "{{$isoTimestamp}}"
                                },
                                "request_body": {
                                    "request_payload": {}
                                }
                            }, indent=2)
                        },
                        "url": {"raw": "{{api_url}}/catalogue/get_lists", "host": ["{{api_url}}"], "path": ["catalogue", "get_lists"]}
                    }
                },
                {
                    "name": "3.2 [Maker] Create Draft Version",
                    "request": {
                        "method": "POST",
                        "header": [
                            {"key": "Authorization", "value": "Bearer {{maker_token}}"},
                            {"key": "Content-Type", "value": "application/json"}
                        ],
                        "body": {
                            "mode": "raw",
                            "raw": json.dumps({
                                "request_header": {
                                    "sender_app_mnemonic": "farmer-registry-staff-portal",
                                    "sender_app_url": "http://localhost:3005",
                                    "request_id": "{{$guid}}",
                                    "request_timestamp": "{{$isoTimestamp}}"
                                },
                                "request_body": {
                                    "request_payload": {
                                        "list_code": "{{list_code}}",
                                        "change_note": "Draft created by QA Maker"
                                    }
                                }
                            }, indent=2)
                        },
                        "url": {"raw": "{{api_url}}/catalogue/create_list_draft", "host": ["{{api_url}}"], "path": ["catalogue", "create_list_draft"]}
                    }
                },
                {
                    "name": "3.3 [Maker] Upsert New Entry into Draft",
                    "request": {
                        "method": "POST",
                        "header": [
                            {"key": "Authorization", "value": "Bearer {{maker_token}}"},
                            {"key": "Content-Type", "value": "application/json"}
                        ],
                        "body": {
                            "mode": "raw",
                            "raw": json.dumps({
                                "request_header": {
                                    "sender_app_mnemonic": "farmer-registry-staff-portal",
                                    "sender_app_url": "http://localhost:3005",
                                    "request_id": "{{$guid}}",
                                    "request_timestamp": "{{$isoTimestamp}}"
                                },
                                "request_body": {
                                    "request_payload": {
                                        "list_code": "{{list_code}}",
                                        "values": [
                                            {
                                                "value_code": "{{test_value_code}}",
                                                "display": "QA Verification Test Entry",
                                                "display_i18n": {"am": "የሙከራ ግቤት"},
                                                "sort_order": 9999,
                                                "status": "ACTIVE",
                                                "attributes": {
                                                    "qa_tested": True,
                                                    "budget_year": 2026
                                                }
                                            }
                                        ]
                                    }
                                }
                            }, indent=2)
                        },
                        "url": {"raw": "{{api_url}}/catalogue/upsert_draft_values", "host": ["{{api_url}}"], "path": ["catalogue", "upsert_draft_values"]}
                    }
                },
                {
                    "name": "3.4 [Maker] View Draft Values",
                    "request": {
                        "method": "POST",
                        "header": [
                            {"key": "Authorization", "value": "Bearer {{maker_token}}"},
                            {"key": "Content-Type", "value": "application/json"}
                        ],
                        "body": {
                            "mode": "raw",
                            "raw": json.dumps({
                                "request_header": {
                                    "sender_app_mnemonic": "farmer-registry-staff-portal",
                                    "sender_app_url": "http://localhost:3005",
                                    "request_id": "{{$guid}}",
                                    "request_timestamp": "{{$isoTimestamp}}"
                                },
                                "request_body": {
                                    "request_payload": {
                                        "list_code": "{{list_code}}"
                                    }
                                }
                            }, indent=2)
                        },
                        "url": {"raw": "{{api_url}}/catalogue/get_list_values", "host": ["{{api_url}}"], "path": ["catalogue", "get_list_values"]}
                    }
                },
                {
                    "name": "3.5 [Maker] Submit Draft for Approval",
                    "request": {
                        "method": "POST",
                        "header": [
                            {"key": "Authorization", "value": "Bearer {{maker_token}}"},
                            {"key": "Content-Type", "value": "application/json"}
                        ],
                        "body": {
                            "mode": "raw",
                            "raw": json.dumps({
                                "request_header": {
                                    "sender_app_mnemonic": "farmer-registry-staff-portal",
                                    "sender_app_url": "http://localhost:3005",
                                    "request_id": "{{$guid}}",
                                    "request_timestamp": "{{$isoTimestamp}}"
                                },
                                "request_body": {
                                    "request_payload": {
                                        "list_code": "{{list_code}}",
                                        "change_note": "QA test batch submitted for checker review"
                                    }
                                }
                            }, indent=2)
                        },
                        "url": {"raw": "{{api_url}}/catalogue/submit_draft", "host": ["{{api_url}}"], "path": ["catalogue", "submit_draft"]}
                    }
                },
                {
                    "name": "3.6 [Checker] Approve & Publish Draft",
                    "request": {
                        "method": "POST",
                        "header": [
                            {"key": "Authorization", "value": "Bearer {{checker_token}}"},
                            {"key": "Content-Type", "value": "application/json"}
                        ],
                        "body": {
                            "mode": "raw",
                            "raw": json.dumps({
                                "request_header": {
                                    "sender_app_mnemonic": "farmer-registry-staff-portal",
                                    "sender_app_url": "http://localhost:3005",
                                    "request_id": "{{$guid}}",
                                    "request_timestamp": "{{$isoTimestamp}}"
                                },
                                "request_body": {
                                    "request_payload": {
                                        "list_code": "{{list_code}}",
                                        "decision_note": "Verified by QA Checker. Approved for production."
                                    }
                                }
                            }, indent=2)
                        },
                        "url": {"raw": "{{api_url}}/catalogue/approve_draft", "host": ["{{api_url}}"], "path": ["catalogue", "approve_draft"]}
                    }
                }
            ]
        },
        {
            "name": "4. Negative & Governance Tests",
            "item": [
                {
                    "name": "4.1 [Security] Maker Self-Approval Attempt (Expect 403 Forbidden)",
                    "event": [{
                        "listen": "test",
                        "script": {
                            "exec": [
                                "pm.test('System rejects self-approval with 403 or error', function () {",
                                "    pm.expect(pm.response.code).to.be.oneOf([400, 403]);",
                                "});"
                            ],
                            "type": "text/javascript"
                        }
                    }],
                    "request": {
                        "method": "POST",
                        "header": [
                            {"key": "Authorization", "value": "Bearer {{maker_token}}"},
                            {"key": "Content-Type", "value": "application/json"}
                        ],
                        "body": {
                            "mode": "raw",
                            "raw": json.dumps({
                                "request_header": {
                                    "sender_app_mnemonic": "farmer-registry-staff-portal",
                                    "sender_app_url": "http://localhost:3005",
                                    "request_id": "{{$guid}}",
                                    "request_timestamp": "{{$isoTimestamp}}"
                                },
                                "request_body": {
                                    "request_payload": {
                                        "list_code": "{{list_code}}",
                                        "decision_note": "Attempting unauthorized self approval"
                                    }
                                }
                            }, indent=2)
                        },
                        "url": {"raw": "{{api_url}}/catalogue/approve_draft", "host": ["{{api_url}}"], "path": ["catalogue", "approve_draft"]}
                    }
                },
                {
                    "name": "4.2 [Checker] Reject Draft with Mandatory Reason",
                    "request": {
                        "method": "POST",
                        "header": [
                            {"key": "Authorization", "value": "Bearer {{checker_token}}"},
                            {"key": "Content-Type", "value": "application/json"}
                        ],
                        "body": {
                            "mode": "raw",
                            "raw": json.dumps({
                                "request_header": {
                                    "sender_app_mnemonic": "farmer-registry-staff-portal",
                                    "sender_app_url": "http://localhost:3005",
                                    "request_id": "{{$guid}}",
                                    "request_timestamp": "{{$isoTimestamp}}"
                                },
                                "request_body": {
                                    "request_payload": {
                                        "list_code": "{{list_code}}",
                                        "decision_note": "Rejected due to invalid botanical category code"
                                    }
                                }
                            }, indent=2)
                        },
                        "url": {"raw": "{{api_url}}/catalogue/reject_draft", "host": ["{{api_url}}"], "path": ["catalogue", "reject_draft"]}
                    }
                },
                {
                    "name": "4.3 [Maker] Discard Unsubmitted Draft",
                    "request": {
                        "method": "POST",
                        "header": [
                            {"key": "Authorization", "value": "Bearer {{maker_token}}"},
                            {"key": "Content-Type", "value": "application/json"}
                        ],
                        "body": {
                            "mode": "raw",
                            "raw": json.dumps({
                                "request_header": {
                                    "sender_app_mnemonic": "farmer-registry-staff-portal",
                                    "sender_app_url": "http://localhost:3005",
                                    "request_id": "{{$guid}}",
                                    "request_timestamp": "{{$isoTimestamp}}"
                                },
                                "request_body": {
                                    "request_payload": {
                                        "list_code": "{{list_code}}"
                                    }
                                }
                            }, indent=2)
                        },
                        "url": {"raw": "{{api_url}}/catalogue/discard_draft", "host": ["{{api_url}}"], "path": ["catalogue", "discard_draft"]}
                    }
                }
            ]
        }
    ]
}

output_path = "/home/user/master-data-standalone/MDS_QA_Testing_Collection.postman_collection.json"
with open(output_path, "w") as f:
    json.dump(collection, f, indent=2)

print(f"Postman collection generated successfully at: {output_path}")
