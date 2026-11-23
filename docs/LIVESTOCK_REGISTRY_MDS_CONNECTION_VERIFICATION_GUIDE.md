# Livestock Registry & MDS API Connection Verification Guide

**Document Version:** 1.0.0  
**Target Audience:** Registry Developers (Livestock, Farmer, Crop Sown, DA), QA Engineers, DevOps  
**Environments Supported:** Local Docker Development (`localhost`) & Staging (`oanstaging.com`)

---

## 1. Overview & Architecture

Every OpenG2P registry (Livestock, Crop Sown, Farmer, DA) integrates with the Master Data Service (MDS) via the **OpenG2P RPC & Keycloak Token Protocol**.

```mermaid
flowchart LR
    subgraph Registry_Container["Livestock Registry Service"]
        EXT["livestock-extension\n(master_data_lists.py)"]
        CLIENT["MasterDataClient\n(openg2p_registry_core)"]
    end

    subgraph IAM["Keycloak IAM"]
        KC["OAuth2 Token Endpoint\n(/realms/staff/.../token)"]
    end

    subgraph MDS["Master Data Service (MDS)"]
        API["Catalogue API\n(/catalogue/get_list_values)"]
        GEO["Geography API\n(/catalogue/get_geo_units)"]
    end

    EXT -->|1. Request Token| CLIENT
    CLIENT -->|2. client_credentials / password| KC
    KC -->|3. Bearer JWT Access Token| CLIENT
    CLIENT -->|4. POST with OpenG2P Envelope| API
    CLIENT -->|4b. POST with OpenG2P Envelope| GEO
    API -->|5. Catalogs: LIVESTOCK_SPECIES, LIVESTOCK_BREED| CLIENT
    GEO -->|5b. Administrative Units: Regions, Zones| CLIENT
    CLIENT -->|6. Cache (TTL)| EXT
```

---

## 2. Configuration & Environment Variables

To establish the connection, each registry requires the following environment variables (defined in `.env`, `docker-compose.yml`, or Helm `values.yaml`):

| Variable Name | Local Docker Value | Staging Value (`oanstaging.com`) | Description |
|---|---|---|---|
| `REGISTRY_STAFF_PORTAL_API_MASTER_DATA_API_URL` | `http://commons-services-master-data-api.commons.svc.cluster.local` | `https://master-data.development.oanstaging.com` | Base URL of Master Data Service backend |
| `REGISTRY_STAFF_PORTAL_API_MASTER_DATA_TOKEN_URL` | `http://keycloak.openg2p.localtest.me/realms/staff/protocol/openid-connect/token` | `https://keycloak.development.oanstaging.com/realms/staff/protocol/openid-connect/token` | Keycloak OpenID token endpoint |
| `REGISTRY_STAFF_PORTAL_API_MASTER_DATA_CLIENT_ID` | `commons-services-staff-portal` | `admin-cli` or `livestock-registry-staff-portal` | Keycloak Client ID |
| `REGISTRY_STAFF_PORTAL_API_MASTER_DATA_CLIENT_SECRET` | `RzqU5DzHmEufjZIaQVIMqr8X31PWTp0l` | Provided by Keycloak Realm Admin | Client Secret for Service Account |
| `REGISTRY_STAFF_PORTAL_API_MASTER_DATA_CACHE_SECONDS` | `300` | `300` (5 minutes) | In-memory cache TTL for catalog lists |

---

## 3. Step-by-Step Instructions to Verify Connection

You have **two verified methods** to test the connection immediately on your local machine:

### Method A: Run the Standalone Verification Script (Fastest - 5 Seconds)

We have created an automated zero-dependency verification script in your repository at:  
`scripts/verify_mds_connection.py`.

#### 1. Test Local Environment:
Run the script directly from your terminal:
```bash
python3 /home/user/master-data-standalone/scripts/verify_mds_connection.py --target local
```

**Expected Successful Output:**
```text
======================================================================
  MDS & REGISTRY API CONNECTION VERIFICATION
  Target Environment: Local Docker Environment
  MDS Endpoint Base : http://localhost
======================================================================
  [1/2] Connecting to Keycloak: http://localhost/realms/staff/protocol/openid-connect/token...
  [SUCCESS] Token acquired successfully!

  [2/2] Testing Core Master Data Endpoints...
  ✓ Livestock Species (LIVESTOCK_SPECIES): 7 items returned [CATTLE, GOATS, SHEEP, POULTRY, CAMELS...]
  ✓ Livestock Breeds (LIVESTOCK_BREED): 3 items returned [BREED_IMPROVED, BREED_LOCAL, BREED_HYBRID]
  ✓ Body Condition Scores (LIVESTOCK_BODY_CONDITION): 5 items returned [LBCOND_POOR, LBCOND_FAIR, LBCOND_GOOD, LBCOND_VERY_GOOD, LBCOND_EXCELLENT]
  ✓ Administrative Geography - Level 1 Regions (/catalogue/get_geo_units): 14 items returned [Tigray, Afar, Amhara, Oromia, Somali...]

======================================================================
  RESULT: ALL CONNECTION & CATALOG TESTS PASSED SUCCESSFULLY! (100%)
  Your registry configuration is fully connected and ready to sync data.
======================================================================
```

#### 2. Test Staging Environment (`oanstaging.com`):
When testing against the staging server, pass your Bearer Token from Postman:
```bash
python3 /home/user/master-data-standalone/scripts/verify_mds_connection.py --target staging --token "eyJhbGciOi..."
```

---

### Method B: Test Directly Inside the Running Livestock Registry Docker Container

This tests the exact live networking and environment variables inside the running `livestock-registry-staff-portal-api` container.

Run this one-liner command in your terminal:
```bash
docker exec livestock-registry-staff-portal-api--pod python3 -c "
import urllib.request, json, os

token_url = os.environ.get('REGISTRY_STAFF_PORTAL_API_MASTER_DATA_TOKEN_URL')
api_url = os.environ.get('REGISTRY_STAFF_PORTAL_API_MASTER_DATA_API_URL')
client_id = os.environ.get('REGISTRY_STAFF_PORTAL_API_MASTER_DATA_CLIENT_ID')
client_secret = os.environ.get('REGISTRY_STAFF_PORTAL_API_MASTER_DATA_CLIENT_SECRET')

# 1. Fetch Keycloak Token
data = f'grant_type=client_credentials&client_id={client_id}&client_secret={client_secret}'.encode()
req = urllib.request.Request(token_url, data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
with urllib.request.urlopen(req) as resp:
    token = json.loads(resp.read())['access_token']
print('✓ Keycloak Token acquired successfully from inside container!')

# 2. Call Master Data RPC
body = json.dumps({
    'request_header': {
        'sender_app_mnemonic': 'livestock-registry',
        'sender_app_url': 'http://livestock-registry',
        'request_id': 'conn-test-01',
        'request_timestamp': '2026-11-03T10:00:00Z'
    },
    'request_body': {
        'pagination_request': {'current_page': 1, 'page_size': 10},
        'request_payload': {'list_code': 'LIVESTOCK_SPECIES'}
    }
}).encode()

req2 = urllib.request.Request(f'{api_url}/catalogue/get_list_values', data=body,
    headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'})
with urllib.request.urlopen(req2) as resp:
    res = json.loads(resp.read())
    values = res.get('response_body', {}).get('response_payload', {}).get('values', [])
    print(f'✓ SUCCESS! Fetched {len(values)} Livestock Species from MDS:')
    for val in values:
        print(f'  - {val.get(\"value_id\")}: {val.get(\"display\")}')
"
```

**Expected Successful Output:**
```text
✓ Keycloak Token acquired successfully from inside container!
✓ SUCCESS! Fetched 7 Livestock Species from MDS:
  - CATTLE: Cattle
  - GOATS: Goats
  - SHEEP: Sheep
  - POULTRY: Poultry
  - CAMELS: Camels
  - EQUINES: Equines
  - OTHER: Other
```

---

## 4. How to Explain This to Other Registry Developers

When handing this over to developers working on **Farmer Registry**, **Crop Sown Registry**, or **DA Registry**, share this 4-point checklist:

### 1. Required Envelope Structure (Mandatory)
MDS uses OpenG2P RPC validation. All requests to `POST /catalogue/get_list_values` and `POST /catalogue/get_geo_units` **must** include the 4 mandatory header and pagination fields:
```json
{
  "request_header": {
    "sender_app_mnemonic": "farmer-registry",     // (Required) App identifier
    "sender_app_url": "https://farmer-registry",   // (Required) Source URL
    "request_id": "uuid-or-unique-string",         // (Required) Unique request ID
    "request_timestamp": "2026-11-03T12:00:00Z"    // (Required) ISO 8601 UTC timestamp
  },
  "request_body": {
    "pagination_request": {
      "current_page": 1,                           // (Required) Page number
      "page_size": 50                              // (Required) Number of records
    },
    "request_payload": {
      "list_code": "ADMIN_REGIONS_CATALOG"         // Your target catalog code
    }
  }
}
```
> [!WARNING]
> Omitting `sender_app_url`, `request_id`, `request_timestamp`, or `current_page` will cause MDS to return `400 Bad Request: Invalid Input. Field required (G2P-REQ-102)`.

### 2. Catalog Mapping by Registry
Provide each team with the list codes relevant to their registry:

| Registry | Target Catalogs in MDS |
|---|---|
| **Livestock Registry** | `LIVESTOCK_SPECIES`, `LIVESTOCK_BREED`, `LIVESTOCK_BODY_CONDITION`, `LIVESTOCK_PRODUCTION_TYPE`, `LIVESTOCK_SYSTEM` |
| **Crop Sown Registry** | `CROP_CATEGORY`, `CROP_COMMODITY`, `CROP_SEASON`, `CROPPING_SYSTEM`, `SOWING_METHOD`, `WATER_SOURCE` |
| **Farmer Registry** | `GENDER_CATALOG`, `ID_TYPE_CATALOG`, `EDUCATION_LEVEL_CATALOG`, `MARITAL_STATUS_CATALOG`, `DISABILITY_CATALOG` |
| **All Registries (Geography)** | Call `POST /catalogue/get_geo_units` with `{"level": "region"}` (cascading down to `zone`, `woreda`, `kebele` via `parent_id`) |

### 3. Keycloak IAM Authentication Rule
- All MDS endpoints require an **authenticated Bearer Token**.
- Registries must not attempt to use `/public/...` endpoints anonymously. Production and staging environments enforce `visibility: private` on geography and catalogs.
- The registry background client uses `grant_type=client_credentials` with its own Keycloak Client ID & Secret to automatically refresh its token.

### 4. Caching & Resilience Rule
- Master Data catalogs change infrequently.
- Registries should cache results in memory using `REGISTRY_STAFF_PORTAL_API_MASTER_DATA_CACHE_SECONDS=300` (5 minutes) so that every form load or validator does not create unnecessary HTTP round-trips.

---

## 5. Troubleshooting Common Errors

| Error Code / Message | Root Cause | Solution |
|---|---|---|
| `G2P-REQ-102: Field required` | Missing mandatory fields in `request_header` or `pagination_request`. | Ensure `request_id`, `request_timestamp`, `sender_app_url`, and `current_page` are present. |
| `G2P-CAT-404: list not found: ...` | Typo in `list_code` or using an unpublished catalog name. | Call `POST /catalogue/get_lists` to see exact list codes in that environment (e.g. `LIVESTOCK_SPECIES` vs `LIVESTOCK_CATALOG`). |
| `HTTP 401 Unauthorized` | Keycloak token expired or missing `Authorization: Bearer <token>` header. | Re-fetch token from Keycloak using client credentials. |
| `{"detail": "geography not found"}` | Attempting to hit `/public/geography/units`. | Switch to the authenticated OpenG2P endpoint: `POST /catalogue/get_geo_units`. |
| `Connection refused / Name resolution failure` | Container cannot resolve `master-data-api` hostname. | Check Docker network bridge or ensure DNS / Host headers are configured properly. |
