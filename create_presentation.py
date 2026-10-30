import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

# Color Palette
DARK_NAVY = RGBColor(15, 23, 42)      # #0F172A
CARD_BG = RGBColor(30, 41, 59)        # #1E293B
ACCENT_BLUE = RGBColor(56, 189, 248)  # #38BDF8
ACCENT_GREEN = RGBColor(52, 211, 153) # #34D399
ACCENT_AMBER = RGBColor(251, 191, 36) # #FBBF24
TEXT_WHITE = RGBColor(248, 250, 252)  # #F8FAFC
TEXT_MUTED = RGBColor(148, 163, 184)  # #94A3B8
BORDER_COLOR = RGBColor(51, 65, 85)   # #334155

def add_speaker_notes(slide, notes_text):
    notes_slide = slide.notes_slide
    tf = notes_slide.notes_text_frame
    tf.text = notes_text

def create_base_slide(title_text, subtitle_text=None):
    slide = prs.slides.add_slide(prs.slide_layouts[6]) # blank layout
    
    # Background
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = DARK_NAVY
    bg.line.fill.background()
    
    # Top banner / Title box
    tb = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(1.0))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    
    p = tf.paragraphs[0]
    p.text = title_text
    p.font.name = "Calibri"
    p.font.size = Pt(24)
    p.font.bold = True
    p.font.color.rgb = TEXT_WHITE
    
    if subtitle_text:
        p2 = tf.add_paragraph()
        p2.text = subtitle_text
        p2.font.name = "Calibri"
        p2.font.size = Pt(13)
        p2.font.color.rgb = ACCENT_BLUE
        p2.space_before = Pt(4)
        
    return slide

def add_card(slide, left, top, width, height, title, body_bullets, accent_color=ACCENT_BLUE):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = CARD_BG
    card.line.color.rgb = BORDER_COLOR
    card.line.width = Pt(1.5)
    
    # Header box inside card
    tb = slide.shapes.add_textbox(left + Inches(0.25), top + Inches(0.2), width - Inches(0.5), height - Inches(0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    
    p = tf.paragraphs[0]
    p.text = title
    p.font.name = "Calibri"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = accent_color
    p.space_after = Pt(8)
    
    for bullet in body_bullets:
        bp = tf.add_paragraph()
        bp.text = f"• {bullet}"
        bp.font.name = "Calibri"
        bp.font.size = Pt(11.5)
        bp.font.color.rgb = TEXT_MUTED
        bp.space_after = Pt(4)

# ==========================================
# SLIDE 1: Title Slide
# ==========================================
s1 = prs.slides.add_slide(prs.slide_layouts[6])
bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
bg1.fill.solid()
bg1.fill.fore_color.rgb = DARK_NAVY
bg1.line.fill.background()

tb1 = s1.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(11.3), Inches(3.5))
tf1 = tb1.text_frame
tf1.word_wrap = True

p = tf1.paragraphs[0]
p.text = "OpenG2P Master Data Service (MDS)"
p.font.name = "Calibri"
p.font.size = Pt(36)
p.font.bold = True
p.font.color.rgb = TEXT_WHITE

p_sub = tf1.add_paragraph()
p_sub.text = "Ethiopia Agri-Stack: Reference Data Architecture, Registry Integration & Live Demonstration"
p_sub.font.name = "Calibri"
p_sub.font.size = Pt(20)
p_sub.font.color.rgb = ACCENT_BLUE
p_sub.space_before = Pt(10)
p_sub.space_after = Pt(24)

p_meta = tf1.add_paragraph()
p_meta.text = "Presenter: Megha Gireesh | Client & Technical Stakeholder Demo | October 2026"
p_meta.font.name = "Calibri"
p_meta.font.size = Pt(13)
p_meta.font.color.rgb = TEXT_MUTED

add_speaker_notes(s1, """[SLIDE 1 SPEAKER NOTES]
Welcome everyone. Good morning/afternoon Malcolm, Faiz, Pavan, and esteemed colleagues.
My name is Megha Gireesh, and I am the Core Master Data Service engineer for the Ethiopia Agri-Stack.
Today, I am pleased to present the Master Data Service (MDS), which serves as the foundational Digital Public Infrastructure for the entire Ethiopian agricultural ecosystem.
Over the next 30 minutes, I will walk you through the architectural design, the 5 live national catalogs we have seeded and published, our Keycloak multi-ministry governance, registry interoperability, and conclude with a live demonstration of the APIs running on our develop environment.
Please feel free to hold questions until the end or stop me if you need immediate clarification on any architectural component.""")

# ==========================================
# SLIDE 2: Executive Overview
# ==========================================
s2 = create_base_slide(
    "1. Executive Overview & Purpose of Master Data Service",
    "The authoritative single source of truth for national reference taxonomies across the Ethiopian agricultural ecosystem."
)
add_card(s2, Inches(0.8), Inches(1.6), Inches(3.6), Inches(5.2), "Single Source of Truth", [
    "Eliminates data fragmentation across fragmented ministry databases.",
    "Centralizes official crop, variety, seed, livestock, and fertilizer catalogs.",
    "Ensures all registries share standard, canonical identifiers.",
    "Supports multi-language labels (English, Amharic, Afaan Oromoo)."
], ACCENT_BLUE)

add_card(s2, Inches(4.8), Inches(1.6), Inches(3.6), Inches(5.2), "Interoperability & DPI", [
    "Serves as core Digital Public Infrastructure (DPI) common service.",
    "Enables seamless M2M integration for Farmer, Land, and Subsidy registries.",
    "Powers mobile ODK data collection via pre-packaged offline itemsets.",
    "DCAT-3 compliant catalog feed for cross-ministerial data syndication."
], ACCENT_GREEN)

add_card(s2, Inches(8.8), Inches(1.6), Inches(3.6), Inches(5.2), "Governance & Security", [
    "Enforces strict Four-Eyes Maker-Checker approval workflows.",
    "Live published versions are immutable in PostgreSQL.",
    "Multi-ministry role segregation via Keycloak (MoA, LDI, CSA).",
    "Complete immutable change audit logging on all catalog updates."
], ACCENT_AMBER)

add_speaker_notes(s2, """[SLIDE 2 SPEAKER NOTES]
Why does Ethiopia need a Master Data Service?
Historically, different agricultural initiatives operated in silos. The Ministry of Agriculture had one list of crops, the Livestock Development Institute had separate breed records, and regional bureaus used inconsistent spelling and administrative codes. When enumerators collected farmer surveys in the field, reconciling this data at the national level was extremely difficult.
The Master Data Service solves this at the root. It provides:
1. Canonical Identifiers: When a farmer registers 'Teff - Magna variety' in Oromia or Amhara, it resolves to the exact same standard P-code and commodity ID.
2. True Interoperability: Consuming systems like the Farmer Registry and Land Registry query MDS over secure REST APIs rather than maintaining duplicate local tables.
3. Institutional Governance: Data cannot be altered casually. Any change requires a structured Maker-Checker workflow adhering to national administrative mandates.""")

# ==========================================
# SLIDE 3: The 5 Base Catalogs (Live Data)
# ==========================================
s3 = create_base_slide(
    "2. The Five Base Reference Catalogs (Live on Platform)",
    "Comprehensive national datasets curated, validated, and published in Master Data Service."
)
add_card(s3, Inches(0.8), Inches(1.6), Inches(2.2), Inches(5.2), "1. Crops", [
    "150 crop commodities.",
    "902 registered varieties (Ethio-Seed list).",
    "7 production categories (Cereals, Pulses, Oilseeds).",
    "3 ecological zones."
], ACCENT_BLUE)

add_card(s3, Inches(3.2), Inches(1.6), Inches(2.2), Inches(5.2), "2. Seeds", [
    "130 seed varieties (SEED_CATALOG).",
    "129 certified seed varieties.",
    "Demand trends by crop and budget year.",
    "Basic, Breeder & Certified seed classes."
], ACCENT_GREEN)

add_card(s3, Inches(5.6), Inches(1.6), Inches(2.2), Inches(5.2), "3. Livestock", [
    "6 major livestock species.",
    "94 national breeds (Boran, Horro, Fogera, etc.).",
    "National livestock census population statistics.",
    "Production types (Dairy, Meat, Draft power)."
], ACCENT_AMBER)

add_card(s3, Inches(8.0), Inches(1.6), Inches(2.2), Inches(5.2), "4. Inputs", [
    "11 certified fertilizer blends & amendments.",
    "Inorganic blends: NPSB, Urea 46-0-0, DAP 18-46-0.",
    "Organic: Bio-Green Vermicompost.",
    "Recommended crops and dosages."
], ACCENT_BLUE)

add_card(s3, Inches(10.4), Inches(1.6), Inches(2.2), Inches(5.2), "5. Geography", [
    "1,271 total administrative units.",
    "Country (l0): 1 (Ethiopia).",
    "Regions (l1): 15 regions.",
    "Zones (l2): 107 zones.",
    "Woredas (l3): 1,148 woredas with GeoJSON polygons."
], ACCENT_GREEN)

add_speaker_notes(s3, """[SLIDE 3 SPEAKER NOTES]
I am thrilled to announce that all five mandatory base catalogs are fully curated, seeded, validated, and published in our development environment.
Let me highlight the scope of what is active right now:
- Crops: We have 150 official commodities and 902 certified crop varieties spanning cereals, pulses, oilseeds, fruits, vegetables, fibers, and stimulants.
- Seeds: 130 standardized seed records, with complete classifications from Breeder, Pre-Basic, Basic, to Certified Seed 1 and 2, including certified seed demand data.
- Livestock: 6 species, 94 indigenous and exotic breeds (such as Boran, Fogera, Horro cattle, and Blackhead Somali sheep), complete with national census figures.
- Inputs: 11 certified fertilizer blends and soil amendments approved by the Ministry of Agriculture, including NPSB, Urea, DAP, and certified bio-fertilizers.
- Administrative Geography: 1,271 standardized units down to level 3 Woredas, all keyed to standard P-codes with valid GeoJSON boundary polygons.""")

# ==========================================
# SLIDE 4: Keycloak Multi-Org RBAC Hierarchy
# ==========================================
s4 = create_base_slide(
    "3. Keycloak Organization Hierarchy & Access Control",
    "Strict separation of duties aligned with national institutional mandates."
)
add_card(s4, Inches(0.8), Inches(1.6), Inches(3.6), Inches(5.2), "Ministry of Agriculture", [
    "Ownership: Crops, Seeds & Agricultural Inputs.",
    "Groups Configured: 'Ministry of Agriculture (MoA)'.",
    "Maker User: moa.maker (Abebe Tadesse).",
    "Checker User: moa.checker (Chaltu Gemechu).",
    "Permission Scope: referenceData:edit, referenceData:approve."
], ACCENT_BLUE)

add_card(s4, Inches(4.8), Inches(1.6), Inches(3.6), Inches(5.2), "Livestock Institute", [
    "Ownership: Livestock species, breeds & census.",
    "Groups Configured: 'Livestock Development Institute (LDI)'.",
    "Maker User: ldi.specialist (Dr. Getachew Bekele).",
    "Checker User: mds-checker.",
    "Permission Scope: Dedicated domain catalog curation."
], ACCENT_AMBER)

add_card(s4, Inches(8.8), Inches(1.6), Inches(3.6), Inches(5.2), "Central Statistical Agency", [
    "Ownership: National Administrative Geography.",
    "Groups Configured: 'Central Statistical Agency (CSA)'.",
    "Admin User: csa.admin (Almaz Wolde).",
    "Checker User: mds-checker.",
    "Permission Scope: geo:edit, boundary uploads & crosswalk maintenance."
], ACCENT_GREEN)

add_speaker_notes(s4, """[SLIDE 4 SPEAKER NOTES]
Security and institutional sovereignty are paramount. In our Keycloak identity provider under the 'mds-develop' realm, we have structured an organizational hierarchy that mirrors the Ethiopian government structure:
- The Ministry of Agriculture controls the Crop, Seed, and Input catalogs. We have provisioned dedicated Maker and Checker accounts: Abebe Tadesse as moa.maker, and Chaltu Gemechu as moa.checker.
- The Livestock Development Institute (LDI) has Dr. Getachew Bekele as domain specialist.
- The Central Statistical Agency (CSA) oversees the geographic boundaries and P-codes.
This role-based access control prevents cross-ministry modification. An officer in Livestock cannot alter agricultural fertilizer standards, and vice versa.""")

# ==========================================
# SLIDE 5: Maker-Checker Governance Flow
# ==========================================
s5 = create_base_slide(
    "4. Four-Eyes Governance Workflow (Maker-Checker)",
    "Ensuring data integrity: Published catalog versions are immutable and require independent verification."
)
add_card(s5, Inches(0.8), Inches(1.6), Inches(2.7), Inches(5.2), "Step 1: Open Draft", [
    "Role: Authorized Maker (e.g., moa.maker).",
    "Action: Calls POST /catalogue/create_list_draft.",
    "Behavior: Opens Draft based on highest published version.",
    "Live Version: Remains live, active, and completely untouched."
], ACCENT_BLUE)

add_card(s5, Inches(3.8), Inches(1.6), Inches(2.7), Inches(5.2), "Step 2: Edit & Diff", [
    "Action: Calls POST /catalogue/upsert_draft_values.",
    "Features: Batch value insertion, attribute schemas, and retirements.",
    "Audit: POST /catalogue/get_list_diff shows exact delta between draft and published version."
], ACCENT_AMBER)

add_card(s5, Inches(6.8), Inches(1.6), Inches(2.7), Inches(5.2), "Step 3: Submit Draft", [
    "Role: Maker submits draft for review.",
    "Action: Calls POST /catalogue/submit_draft.",
    "Status: Changes from DRAFT -> SUBMITTED.",
    "Locking: Draft is locked against further direct edits."
], ACCENT_BLUE)

add_card(s5, Inches(9.8), Inches(1.6), Inches(2.7), Inches(5.2), "Step 4: Approve / Reject", [
    "Role: Authorized Checker (e.g., moa.checker).",
    "Action: Calls POST /catalogue/approve_draft.",
    "Publication: Draft becomes new published version (e.g. v2).",
    "Rejection: Checker can reject with comments for rework."
], ACCENT_GREEN)

add_speaker_notes(s5, """[SLIDE 5 SPEAKER NOTES]
Here we see the Four-Eyes principle in action.
In critical national databases, no single individual should be able to alter reference standards directly in production.
The lifecycle works in four distinct stages:
1. The Maker initiates a draft. This creates a working copy without disrupting the live published version currently serving queries to the Farmer Registry.
2. The Maker performs edits, additions, or retirements. The system can compute an exact visual diff showing modified rows.
3. Once complete, the Maker submits the draft. At this point, the draft is frozen.
4. An independent Checker logs in, reviews the submission and audit trail, and either Approves or Rejects with feedback. Upon approval, the draft instantly becomes the new immutable published version.
During our live demo today, I will execute this complete sequence live.""")

# ==========================================
# SLIDE 6: Registry Integration Architecture
# ==========================================
s6 = create_base_slide(
    "5. Interoperability & Integration with External Registries",
    "How the Farmer Registry, Livestock Registry, and Land Systems consume master data."
)
add_card(s6, Inches(0.8), Inches(1.6), Inches(3.6), Inches(5.2), "1. M2M Handshake", [
    "Consuming services authenticate via OAuth2 Client Credentials grant.",
    "Keycloak Client: master-data.",
    "Secret-backed service-to-service token exchange.",
    "Supports in-cluster DNS routing (http://commons-services-master-data-api:8000) or public HTTPS."
], ACCENT_BLUE)

add_card(s6, Inches(4.8), Inches(1.6), Inches(3.6), Inches(5.2), "2. OpenG2P Envelope", [
    "Standard JSON request/response envelope across all endpoints.",
    "request_header: sender_app_mnemonic (e.g. Farmer), request_id ($guid), request_timestamp.",
    "request_body: pagination_request + request_payload.",
    "Strict schema validation on payload parameters."
], ACCENT_GREEN)

add_card(s6, Inches(8.8), Inches(1.6), Inches(3.6), Inches(5.2), "3. Partner Manager", [
    "Partner Manager validates inter-registry traffic.",
    "Registered in master_data.g2p_partners table.",
    "Guarantees traceable, auditable API requests across all national registry nodes.",
    "Prevents unauthorized external tampering."
], ACCENT_AMBER)

add_speaker_notes(s6, """[SLIDE 6 SPEAKER NOTES]
Turning to interoperability: How do consuming registries connect to Master Data Service?
- Communication occurs via machine-to-machine (M2M) OAuth2 client credentials authentication using our Keycloak identity provider.
- Consuming microservices, such as the Farmer Registry, acquire a scoped JWT and call MDS either across the Kubernetes service mesh via internal DNS or through public HTTPS.
- Every API request adheres to the standard OpenG2P JSON envelope containing a request header with unique tracking IDs, timestamp, and sender app mnemonic.
- This guarantees full auditability: every single lookup can be traced back to the calling system and transaction.""")

# ==========================================
# SLIDE 7: Runtime APIs for Registries
# ==========================================
s7 = create_base_slide(
    "6. Core Runtime APIs Utilized by Consuming Registries",
    "High-performance endpoints powering registration portals, validation pipelines, and form dropdowns."
)
add_card(s7, Inches(0.8), Inches(1.6), Inches(5.6), Inches(2.4), "POST /catalogue/get_list_values (Primary Query)", [
    "Populates dropdowns and selection choices on farmer registration forms.",
    "Returns code, multilingual labels, sort order, and domain attribute schemas.",
    "Targets: CROP_CATALOG, CROP_VARIETY, SEED_CATALOG, INPUT_CATALOG, LIVESTOCK_CATALOG."
], ACCENT_BLUE)

add_card(s7, Inches(6.8), Inches(1.6), Inches(5.6), Inches(2.4), "POST /catalogue/get_list_value (Single Validation)", [
    "Single-item verification during farmer record ingestion.",
    "Validates if submitted code (e.g. CROP_1 or FERT-UREA) is active and valid.",
    "Retrieves full scientific properties and regulatory license numbers."
], ACCENT_GREEN)

add_card(s7, Inches(0.8), Inches(4.3), Inches(5.6), Inches(2.5), "POST /catalogue/get_geo_units (Cascading Geography)", [
    "Powers cascading location dropdowns (Region -> Zone -> Woreda).",
    "Accepts level_id (l1, l2, l3) and parent_code to fetch immediate children.",
    "Essential for farm plot boundary registration and farmer residency."
], ACCENT_AMBER)

add_card(s7, Inches(6.8), Inches(4.3), Inches(5.6), Inches(2.5), "POST /catalogue/get_geo_unit (Unit Resolution)", [
    "Resolves a specific administrative P-code (e.g. ET04 for Oromia) to official metadata.",
    "Returns official English & Amharic names, parent codes, and administrative level.",
    "Verifies field surveyor location accuracy."
], ACCENT_BLUE)

add_speaker_notes(s7, """[SLIDE 7 SPEAKER NOTES]
Consuming registries primarily interact with four core endpoints:
1. POST /catalogue/get_list_values: Used when loading a form. When an enumerator or web user selects a crop, this endpoint returns the active list of crops along with localized labels and agronomic metadata.
2. POST /catalogue/get_list_value: Used during data validation. If a record comes in claiming crop code 'CROP_1', this validates that it is currently active, valid, and returns its botanical details.
3. POST /catalogue/get_geo_units: Powers cascading geographic drop-downs. If Region 'ET04' (Oromia) is selected, passing parent_code='ET04' instantly returns all 21 Zones under Oromia. Passing a Zone code returns all Woredas under that Zone.
4. POST /catalogue/get_geo_unit: Resolves an individual P-code to verify coordinates and boundary names.""")

# ==========================================
# SLIDE 8: Offline Field Collection & ODK
# ==========================================
s8 = create_base_slide(
    "7. Bulk Synchronization & Offline Field Collection (ODK Collect)",
    "Ensuring agricultural enumerators in remote rural areas can collect data without active internet."
)
add_card(s8, Inches(0.8), Inches(1.6), Inches(3.6), Inches(5.2), "Offline Itemsets (CSV)", [
    "Endpoint: GET /public/datasets/{code}/download.csv.",
    "Generates itemsets.csv bundled directly into mobile ODK forms.",
    "Enables instant offline cascading search for crops, varieties, and fertilizers on field tablets.",
    "Zero network dependency during rural farmer registration."
], ACCENT_BLUE)

add_card(s8, Inches(4.8), Inches(1.6), Inches(3.6), Inches(5.2), "Administrative Lists (CSV)", [
    "Endpoint: GET /public/geography/levels/{level}/units.csv.",
    "Downloads full lists of 1,148 Woredas or 15 Regions as lightweight CSVs.",
    "Powers mobile enumerator location pickers.",
    "Guarantees that GPS points tie to official administrative P-codes."
], ACCENT_GREEN)

add_card(s8, Inches(8.8), Inches(1.6), Inches(3.6), Inches(5.2), "GIS & Open Standards", [
    "GeoJSON Boundaries: GET /public/geography/.../boundaries.geojson.",
    "Streams polygon boundaries for national and regional mapping dashboards.",
    "DCAT-3 Syndication: GET /public/catalog provides standard JSON-LD catalog feeds.",
    "Interoperable with international open data standards."
], ACCENT_AMBER)

add_speaker_notes(s8, """[SLIDE 8 SPEAKER NOTES]
A major real-world challenge in Ethiopia is rural connectivity. In many woredas and kebeles, mobile enumerators have zero 3G/4G connectivity.
MDS solves this natively through its bulk export endpoints:
- ODK Collect supports external CSV itemsets. Our GET /public/datasets/{code}/download.csv endpoint provides the exact CSV files needed to bundle into ODK forms.
- Enumerators can perform fast, responsive cascading searches on their Android tablets completely offline.
- When enumerators return to an area with connectivity, their submissions seamlessly match the canonical P-codes and catalog IDs in MDS without data reconciliation headaches.
- Furthermore, we offer GeoJSON streaming for GIS boundary mapping and DCAT-3 compliant metadata syndication.""")

# ==========================================
# SLIDE 9: Centralized Seeding Architecture
# ==========================================
s9 = create_base_slide(
    "8. Centralized Deployment & Automated Data Seeding",
    "Config-driven architecture aligned with Faiz, Shibu, and DevOps deployment standards."
)
add_card(s9, Inches(0.8), Inches(1.6), Inches(3.6), Inches(5.2), "Vanilla Platform Code", [
    "The core Master Data Service repository remains 100% generic and unforked.",
    "Runs official openg2p/master-data-api:develop image.",
    "All domain-specific agricultural catalogs are treated strictly as reference data packs.",
    "Guarantees easy upstream platform upgrades without breaking changes."
], ACCENT_BLUE)

add_card(s9, Inches(4.8), Inches(1.6), Inches(3.6), Inches(5.2), "Centralized openg2p-data", [
    "Seeding scripts consolidated into Centre-for-Open-Societal-Systems/openg2p-data.",
    "PR branch: feature/mds-catalogs-eth.",
    "Packaged under scripts/mds/ and packs/ETH/domains/agriculture/.",
    "Single source of truth used to build the unified data-seeding Docker image."
], ACCENT_AMBER)

add_card(s9, Inches(8.8), Inches(1.6), Inches(3.6), Inches(5.2), "Kubernetes Helm Deployment", [
    "Pavan's oan-helm deployment triggers data seeding via an in-cluster Kubernetes Job.",
    "All SQL scripts hardened with IF NOT EXISTS guards (zero destructive drops).",
    "Connects securely to cluster PostgreSQL (commons-postgresql:5432).",
    "Fully automated, repeatable, and idempotent across environment deployments."
], ACCENT_GREEN)

add_speaker_notes(s9, """[SLIDE 9 SPEAKER NOTES]
I want to highlight a key architectural decision made in close collaboration with Faiz Mohammed and Pavan NS:
We have strictly preserved the purity of the core OpenG2P platform repository. The master-data-api remains 100% generic, vanilla, and unforked.
All country-specific, domain-specific reference data—such as Ethiopian crops, seeds, livestock, and fertilizers—is managed entirely as reference data packs in the centralized 'openg2p-data' repository.
We have packaged all seeding automation scripts into a dedicated feature branch, 'feature/mds-catalogs-eth', and submitted a clean pull request.
When DevOps deploys the platform via Helm, an automated Kubernetes Job pulls this unified data-seeding image, executing idempotent SQL scripts that safely populate the database without any manual intervention.""")

# ==========================================
# SLIDE 10: Live Demonstration Flow
# ==========================================
s10 = create_base_slide(
    "9. Live Demonstration Sequence (Postman Test Suite)",
    "Structured, high-impact demonstration flow proving all platform capabilities with 100% pass rate."
)
add_card(s10, Inches(0.8), Inches(1.6), Inches(2.7), Inches(5.2), "Phase 1: Security", [
    "Step 1: M2M Authentication (POST /token with master-data client).",
    "Step 2: User Login & Profile (POST /token as moa.maker -> GET /userinfo).",
    "Result: Verifies multi-ministry group assignment (MoA Maker)."
], ACCENT_BLUE)

add_card(s10, Inches(3.8), Inches(1.6), Inches(2.7), Inches(5.2), "Phase 2: Catalogs", [
    "Step 3: Discover Datasets (POST /catalogue/get_lists shows 80 datasets).",
    "Step 4: Query Ethiopian Crops & Fertilizers (POST /catalogue/get_list_values).",
    "Result: Proves real national agricultural data is live and active."
], ACCENT_GREEN)

add_card(s10, Inches(6.8), Inches(1.6), Inches(2.7), Inches(5.2), "Phase 3: Geography", [
    "Step 5: National Hierarchy (POST /catalogue/get_geo_levels for l0..l3).",
    "Step 6: Regional Units (POST /catalogue/get_geo_units for l1 Regions).",
    "Result: Proves 1,271 P-code units (e.g. ET04 Oromia) are accessible."
], ACCENT_AMBER)

add_card(s10, Inches(9.8), Inches(1.6), Inches(2.7), Inches(5.2), "Phase 4: Governance", [
    "Step 7: Maker Draft Creation (POST /catalogue/create_list_draft).",
    "Step 8: Checker Approval (POST /catalogue/approve_draft as moa.checker).",
    "Result: Live demonstration of immutable 4-eyes approval workflow."
], ACCENT_BLUE)

add_speaker_notes(s10, """[SLIDE 10 SPEAKER NOTES]
We will now transition to the live interactive demonstration.
I will switch over to Postman, running against our live develop server at https://mds-api-dev.oanstaging.com.
We will execute our 4-phase demonstration:
Phase 1: Security & Identity - Acquiring M2M machine tokens and inspecting the Keycloak userinfo payload for our MoA Maker.
Phase 2: Catalog Data - Querying live Ethiopian crop and fertilizer records, inspecting multilingual labels in Amharic and English.
Phase 3: Administrative Geography - Fetching administrative levels and querying the 15 regions and child zones.
Phase 4: Maker-Checker Governance - Opening a live draft, modifying attributes, submitting, and approving it under the Checker role.
Our automated test suite covering all these steps runs with a 100% pass rate.""")

# ==========================================
# SLIDE 11: Summary & Next Steps
# ==========================================
s11 = create_base_slide(
    "10. Project Summary & Next Steps",
    "Delivering robust Digital Public Infrastructure for the Ethiopia Agricultural Transformation Institute (ATI)."
)
add_card(s11, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.2), "Key Deliverables Completed", [
    "All 5 required base agricultural catalogs fully seeded, validated, and published.",
    "1,271 Administrative Geography units (Country down to Woredas) with GeoJSON boundaries.",
    "Keycloak Multi-Organization Access Hierarchy configured (MoA, LDI, CSA).",
    "Maker-Checker four-eyes governance verified live in production environment.",
    "Automated data-seeding PR raised in openg2p-data repository for CI/CD.",
    "Complete 86-request Postman Collection delivered with 100% automated test pass rate."
], ACCENT_GREEN)

add_card(s11, Inches(6.8), Inches(1.6), Inches(5.6), Inches(5.2), "Immediate Next Steps", [
    "PR Review & Merge: Faiz & Pavan review PR in openg2p-data (feature/mds-catalogs-eth).",
    "Helm Pipeline: Pavan triggers unified data-seeding image build in oan-helm pipeline.",
    "Registry Sync: Connect Farmer Registry and mobile ODK forms to live MDS endpoints.",
    "Training & Onboarding: Conduct Maker/Checker workflow training for Ministry of Agriculture staff.",
    "Q&A Session: Open discussion with client and stakeholders."
], ACCENT_BLUE)

add_speaker_notes(s11, """[SLIDE 11 SPEAKER NOTES]
To summarize:
We have successfully implemented and validated the complete Master Data Service foundation for the Ethiopia Agri-Stack.
- 5 comprehensive agricultural reference catalogs are live.
- 1,271 administrative units are mapped with GeoJSON.
- Keycloak role segregation and four-eyes Maker-Checker workflows are active and proven.
- All code and seeding automation are neatly isolated in our pull request on the openg2p-data repository.

Immediate Next Steps:
1. Complete review and merge of PR #feature/mds-catalogs-eth into develop.
2. Build and tag the unified data-seeding container for Pavan's Helm deployment.
3. Assist the Farmer Registry team in binding their frontend dropdowns to MDS APIs.
Thank you for your time and support. I now open the floor to Malcolm, Faiz, and the team for any questions or feedback.""")

out_pptx = "/home/user/master-data-standalone/MDS_Client_Demo_Presentation.pptx"
prs.save(out_pptx)
print(f"Presentation saved successfully with full speaker notes to: {out_pptx}")
