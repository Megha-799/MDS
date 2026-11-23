# OpenG2P Master Data Service (MDS) — API & Catalog Integration Architecture
**Ethiopia National Agricultural Data Stack: Enterprise Integration Guide for Consuming Registries**

---

## 1. Executive Summary & Purpose

The **Master Data Service (MDS)** functions as the core Digital Public Infrastructure (DPI) for the Ethiopian agricultural ecosystem. It establishes a single canonical source of truth for all foundational reference data across ministries, directorates, and partner systems.

This document serves as the master architectural reference for connecting external registries and services to MDS. Specifically, it standardizes reference data consumption for:
1. **Farmer Registry**: Farmer identity, agricultural holdings, land preparation methods, and administrative cascading geolocation.
2. **Crop Sown Registry**: Seasonal crop declarations, certified varieties, seed demand classifications, inputs (fertilizers, pesticides, inoculants), and agro-ecological conditions.
3. **Livestock Registry (ET-LITS / LIS)**: Livestock species, registered breeds, animal sex/gender, body condition scores (BCS), production purposes, agro-ecological holding zones, and ear tag lineages.

---

## 2. Integration Architecture: Core OpenG2P RPC & Security

All external registries consume reference data through the secure **Core OpenG2P Enterprise RPC API**. MDS enforces strict Keycloak token authentication to ensure transaction tracking, audit logging, and data governance.

```
+----------------------------------------------------------------------------------------------------+
|                                    EXTERNAL REGISTRIES & APPS                                      |
|                                                                                                    |
|      [ Farmer Registry ]         [ Crop Sown Registry ]         [ Livestock Registry ET-LITS ]     |
+---------------------------------+-------------------------------+----------------------------------+
                                  |                               |
                                  |  (Keycloak Bearer JWT Token)  |
                                  v                               v
+----------------------------------------------------------------------------------------------------+
|                                 MASTER DATA SERVICE (Port 8044)                                     |
|                                 Base: /catalogue/...                                               |
|                                                                                                    |
|   ┌────────────────────────────────────────────────────────────────────────────────────────────┐  |
|   │ Secure Core OpenG2P Envelope RPC Engine                                                   │  |
|   │ - Enforces Keycloak Authentication (Bearer JWT)                                            │  |
|   │ - Standard JSON Envelope: request_header + request_body                                    │  |
|   │ - Granular Server-Side Filtering, Pagination, and Parent-Child Cascading                   │  |
|   │ - Endpoints: /catalogue/get_lists, /catalogue/get_list_values, /catalogue/get_geo_units...  │  |
|   └────────────────────────────────────────────────────────────────────────────────────────────┘  |
+----------------------------------------------------------------------------------------------------+
                                                  |
                                                  v
+----------------------------------------------------------------------------------------------------+
|                                      POSTGRESQL 16 / MINIO S3                                      |
|   - 5 Base Reference Domains: Crops, Seeds, Livestock, Agricultural Inputs, Administrative Geo     |
|   - Immutable Versioning & Maker-Checker Four-Eyes Audit Log                                       |
+----------------------------------------------------------------------------------------------------+
```

### 2.1 Backend Connection Details
* **Develop Server Base URL**: `https://master-data.development.oanstaging.com`
* **Local Standalone Base URL**: `http://localhost:8044`
* **API Protocol**: Standard HTTP `POST` with JSON Envelope
* **Headers Required**:
  * `Content-Type: application/json`
  * `Authorization: Bearer <ACCESS_TOKEN>`

---

## 3. Authentication & Authorization (Keycloak M2M)

Every request to `/catalogue/...` must carry a valid Bearer JWT issued by Keycloak.

### 3.1 Keycloak Configuration for Development & Staging
* **Keycloak URL**: `https://keycloak.development.oanstaging.com`
* **Realm**: `staff`
* **Client ID**: `admin-cli` (or registered client `farmer-registry-staff-portal`)
* **Grant Type**: `password` (for user workflows) or `client_credentials` (for service daemons)

### 3.2 Obtaining an Access Token (cURL Sample)
```bash
curl -X POST "https://keycloak.development.oanstaging.com/realms/staff/protocol/openid-connect/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=admin-cli" \
  -d "username=moa.maker" \
  -d "password=YOUR_PASSWORD" \
  -d "grant_type=password"
```

#### Token Response:
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI...",
  "expires_in": 3600,
  "refresh_expires_in": 1800,
  "token_type": "Bearer",
  "scope": "openid profile email"
}
```

---

## 4. Standard OpenG2P Request & Response Envelope

All interactions with MDS require the OpenG2P standard transaction envelope.

### 4.1 Standard Request Envelope
```json
{
  "request_header": {
    "sender_app_mnemonic": "farmer-registry-staff-portal",
    "sender_app_url": "https://farmer-registry.oanstaging.com",
    "request_id": "c1f7a4b2-4d56-43b9-a9a7-8ef0c2394c8e",
    "request_timestamp": "2026-11-03T12:00:00Z"
  },
  "request_body": {
    "pagination_request": {
      "current_page": 1,
      "page_size": 50,
      "sort_by": "display"
    },
    "request_payload": {
      "list_code": "CROP_CATALOG",
      "version": "latest",
      "include_retired": false
    }
  }
}
```

### 4.2 Standard Response Envelope
```json
{
  "response_header": {
    "sender_app_mnemonic": "master-data-api",
    "sender_app_url": "http://localhost:8000",
    "request_id": "c1f7a4b2-4d56-43b9-a9a7-8ef0c2394c8e",
    "request_timestamp": "2026-11-03T12:00:00Z",
    "response_timestamp": "2026-11-03T12:00:00.104231Z",
    "response_status": "SUCCESS"
  },
  "response_body": {
    "pagination_response": {
      "current_page": 1,
      "page_size": 50,
      "total_records": 129,
      "total_pages": 3
    },
    "response_payload": {
      "list_code": "CROP_CATALOG",
      "version_no": 1,
      "values": [ ... ]
    }
  }
}
```

---

## 5. Master Inventory of Available MDS Reference Catalogs

| # | Catalog Identifier (`list_code`) | Domain | Responsible Authority | Purpose in Registries |
|---|---|---|---|---|
| **1** | `ADMIN_REGIONS_CATALOG` | Geography | Central Statistical Agency (CSA) | Level 1: 14 National Regional States & Chartered Cities |
| **2** | `ADMIN_ZONES_CATALOG` | Geography | Central Statistical Agency (CSA) | Level 2: 125 Administrative Zones (linked to parent Region) |
| **3** | `ADMIN_WOREDAS_CATALOG` | Geography | Central Statistical Agency (CSA) | Level 3: 1,359 Administrative Woredas (linked to parent Zone) |
| **4** | `ECOLOGICAL_ZONE_CATALOG` | Agriculture | Ministry of Agriculture (MoA) | Traditional agro-ecological altitude zones (Kolla, Weyna Dega, Dega) |
| **5** | `CROP_CATEGORY_CATALOG` | Crop | Ministry of Agriculture (MoA) | Crop classifications (Cereals, Pulses, Oilseeds, Vegetables, Fruits) |
| **6** | `CROP_CATALOG` | Crop | Ministry of Agriculture (MoA) | Canonical crop commodities (129 crops with isolation distance, etc.) |
| **7** | `CROP_VARIETY_CATALOG` | Crop | Ministry of Agriculture (MoA) | 902 registered seed varieties with breeder, maintainer & release year |
| **8** | `SEED_CATALOG` | Seed | Ministry of Agriculture (MoA) | Official Ethio-Seed catalog entries (129 certified seed commodities) |
| **9** | `SEED_DEMAND_TREND_CATALOG` | Seed | Ministry of Agriculture (MoA) | Demand trends across seed classes (Breeder, Basic, Certified C1/C2) |
| **10** | `SEED_DEMAND_BY_CROP_CATALOG`| Seed | Ministry of Agriculture (MoA) | Crop-segmented seed demand metrics |
| **11** | `INPUT_CATALOG` | Inputs | Ministry of Agriculture (MoA) | Approved fertilizers (NPSB, Urea, DAP), bio-inoculants, soil lime |
| **12** | `LIVESTOCK_CATALOG` | Livestock | Livestock Development Institute (LDI) | Canonical livestock species (Bovine, Ovine, Caprine, Equine, Camel) |
| **13** | `LIVESTOCK_BREED_CATALOG` | Livestock | Livestock Development Institute (LDI) | 94 registered breeds (Boran, Fogera, Horro, Barka, Somali sheep, etc.) |
| **14** | `LIVESTOCK_GENDER_CATALOG` | Livestock | Livestock Development Institute (LDI) | Animal sex & reproductive status (Female, Male, Neutered) |
| **15** | `LIVESTOCK_BODY_CONDITION_CATALOG` | Livestock | Livestock Development Institute (LDI) | Standard Body Condition Scores (BCS 1: Emaciated to BCS 5: Obese) |
| **16** | `LIVESTOCK_PRODUCTION_TYPE_CATALOG` | Livestock | Livestock Development Institute (LDI) | Production purposes (Dairy, Meat, Breeding, Traction, Wool, Honey) |
| **17** | `LIVESTOCK_LOCATION_TYPE_CATALOG` | Livestock | Livestock Development Institute (LDI) | Animal ecological zones (High Land, Low Land, Mid Land) |
| **18** | `LIVESTOCK_RECORD_STATUS_CATALOG` | Livestock | Livestock Development Institute (LDI) | Animal registry lifecycle states (Pending, Active, Approved, Deceased) |
| **19** | `LIVESTOCK_POPULATION_CATALOG` | Livestock | Livestock Development Institute (LDI) | National census baseline metrics by species and year |
| **20** | `LAND_PREPARATION_METHOD_CATALOG` | Agriculture | Ministry of Agriculture (MoA) | Tillage practices (Oxen plough, Tractor, Manual hoe, Zero tillage) |

---

## 6. Core Matrix of Registry API Endpoints

All data fetching is performed via the four primary authenticated runtime endpoints:

| Endpoint | Method | Key Request Payload Parameters | Consuming Registries |
|---|---|---|---|
| `POST /catalogue/get_lists` | `POST` | `{ "include_unpublished": false }` | All (Catalog discovery) |
| `POST /catalogue/get_list_values` | `POST` | `list_code`, `parent_code`, `attribute_filters`, `search`, `version` | All (Dropdown options & values) |
| `POST /catalogue/get_list_value` | `POST` | `list_code`, `value_code`, `version` | All (Single code validation) |
| `POST /catalogue/get_geo_units` | `POST` | `level_id` (`l1`, `l2`, `l3`), `parent_unit_id` (P-code) | All (Cascading Region/Zone/Woreda) |
| `POST /catalogue/get_geo_unit` | `POST` | `unit_id` (P-code, e.g. `ET040103`) | All (Single P-code resolution & ancestors) |

---

## 7. Registry Integration Documents in this Suite

1. [Farmer Registry MDS Integration Guide](file:///home/user/master-data-standalone/docs/01_FARMER_REGISTRY_MDS_INTEGRATION_GUIDE.md)
   * Cascading Geolocation dropdowns: Region (`l1`) $\rightarrow$ Zone (`l2`) $\rightarrow$ Woreda (`l3`).
   * P-code resolution (`POST /catalogue/get_geo_unit`).
   * Land preparation and agro-ecological catalogs via `POST /catalogue/get_list_values`.
   * Frontend React cascading integration code snippet.

2. [Crop Sown Registry MDS Integration Guide](file:///home/user/master-data-standalone/docs/02_CROP_SOWN_REGISTRY_MDS_INTEGRATION_GUIDE.md)
   * Cascading Crop $\rightarrow$ Variety selection via `POST /catalogue/get_list_values` (`parent_code`).
   * Certified seed catalog and class demand filters.
   * Approved fertilizer blends, application dosages, and chemical inputs (`INPUT_CATALOG`).

3. [Livestock Registry MDS Integration Guide](file:///home/user/master-data-standalone/docs/03_LIVESTOCK_REGISTRY_MDS_INTEGRATION_GUIDE.md)
   * Cascading Species $\rightarrow$ Breed selection (`parent_code: "BOVINE"`).
   * Body Condition Scoring (`BCS_1` to `BCS_5`) integration.
   * Reproductive gender and multi-species production purpose mappings.
   * National ear tag series validation.
