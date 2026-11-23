import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # Professional Theme Color Palette
    DARK_NAVY = RGBColor(15, 23, 42)       # #0F172A - Main slide background
    CARD_BG = RGBColor(30, 41, 59)         # #1E293B - Container card background
    BORDER_COLOR = RGBColor(51, 65, 85)    # #334155 - Subtle border
    ACCENT_CYAN = RGBColor(56, 189, 248)   # #38BDF8 - Highlights & Title accents
    ACCENT_GREEN = RGBColor(52, 211, 153)  # #34D399 - Approvals / Success / Active
    ACCENT_AMBER = RGBColor(251, 191, 36)  # #FBBF24 - Warnings / Governance / Workflow
    ACCENT_PURPLE = RGBColor(168, 85, 247) # #A855F7 - Integration / Registries
    TEXT_WHITE = RGBColor(248, 250, 252)   # #F8FAFC - Main text
    TEXT_MUTED = RGBColor(148, 163, 184)   # #94A3B8 - Secondary text

    def add_speaker_notes(slide, notes_text):
        notes_slide = slide.notes_slide
        tf = notes_slide.notes_text_frame
        tf.text = notes_text

    def create_base_slide(title_text, subtitle_text=None, category_badge="MASTER DATA SERVICE"):
        slide = prs.slides.add_slide(prs.slide_layouts[6]) # blank layout

        # Background
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = DARK_NAVY
        bg.line.fill.background()

        # Category Badge
        badge = slide.shapes.add_textbox(Inches(0.8), Inches(0.35), Inches(11.7), Inches(0.3))
        btf = badge.text_frame
        btf.word_wrap = True
        btf.margin_left = btf.margin_top = btf.margin_right = btf.margin_bottom = 0
        bp = btf.paragraphs[0]
        bp.text = category_badge.upper()
        bp.font.name = "Calibri"
        bp.font.size = Pt(10)
        bp.font.bold = True
        bp.font.color.rgb = ACCENT_AMBER

        # Title Box
        tb = slide.shapes.add_textbox(Inches(0.8), Inches(0.65), Inches(11.7), Inches(1.0))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p = tf.paragraphs[0]
        p.text = title_text
        p.font.name = "Calibri"
        p.font.size = Pt(22)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE

        if subtitle_text:
            p2 = tf.add_paragraph()
            p2.text = subtitle_text
            p2.font.name = "Calibri"
            p2.font.size = Pt(13)
            p2.font.color.rgb = ACCENT_CYAN
            p2.space_before = Pt(3)

        return slide

    def add_card(slide, left, top, width, height, title, body_bullets, accent_color=ACCENT_CYAN, badge_text=None):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = BORDER_COLOR
        card.line.width = Pt(1.2)

        # Header accent bar inside card
        header_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, Inches(0.08))
        header_bar.fill.solid()
        header_bar.fill.fore_color.rgb = accent_color
        header_bar.line.fill.background()

        tb = slide.shapes.add_textbox(left + Inches(0.2), top + Inches(0.18), width - Inches(0.4), height - Inches(0.3))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        # Title
        p = tf.paragraphs[0]
        p.text = title
        p.font.name = "Calibri"
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE

        if badge_text:
            p.text = f"{title} [{badge_text}]"

        # Bullets
        for bullet in body_bullets:
            bp = tf.add_paragraph()
            bp.text = f"•  {bullet}"
            bp.font.name = "Calibri"
            bp.font.size = Pt(11.5)
            bp.font.color.rgb = TEXT_MUTED
            bp.space_before = Pt(5)

    # ==========================================
    # SLIDE 1: TITLE SLIDE
    # ==========================================
    s1 = prs.slides.add_slide(prs.slide_layouts[6])
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = DARK_NAVY
    bg1.line.fill.background()

    # Title box
    tb1 = s1.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.3), Inches(4.0))
    tf1 = tb1.text_frame
    tf1.word_wrap = True

    p = tf1.paragraphs[0]
    p.text = "OpenG2P Master Data Service (MDS)"
    p.font.name = "Calibri"
    p.font.size = Pt(38)
    p.font.bold = True
    p.font.color.rgb = TEXT_WHITE

    p2 = tf1.add_paragraph()
    p2.text = "Digital Public Infrastructure for the Ethiopia Agri-Stack Ecosystem"
    p2.font.name = "Calibri"
    p2.font.size = Pt(20)
    p2.font.bold = True
    p2.font.color.rgb = ACCENT_CYAN
    p2.space_before = Pt(8)

    p3 = tf1.add_paragraph()
    p3.text = "Comprehensive Architecture, Governance & Live Registry Integration Demo"
    p3.font.name = "Calibri"
    p3.font.size = Pt(14)
    p3.font.color.rgb = TEXT_MUTED
    p3.space_before = Pt(6)

    # Info card on title slide
    tb_meta = s1.shapes.add_textbox(Inches(1.0), Inches(4.8), Inches(11.3), Inches(1.8))
    tf_meta = tb_meta.text_frame
    m1 = tf_meta.paragraphs[0]
    m1.text = "Presenter: Megha A P | Core Master Data Service Engineer"
    m1.font.name = "Calibri"
    m1.font.size = Pt(13)
    m1.font.bold = True
    m1.font.color.rgb = ACCENT_AMBER

    m2 = tf_meta.add_paragraph()
    m2.text = "Environment: https://master-data-ui.development.oanstaging.com  |  API: https://master-data.development.oanstaging.com"
    m2.font.name = "Calibri"
    m2.font.size = Pt(12)
    m2.font.color.rgb = TEXT_MUTED
    m2.space_before = Pt(4)

    m3 = tf_meta.add_paragraph()
    m3.text = "Target Scope: 1. Available Catalogues  •  2. User Login & CRUD  •  3. Maker-Checker Workflow  •  4. Registry Integration (FR, CSR, LR)"
    m3.font.name = "Calibri"
    m3.font.size = Pt(12)
    m3.font.color.rgb = ACCENT_GREEN
    m3.space_before = Pt(4)

    add_speaker_notes(s1, """[WELCOME & INTRODUCTION]
Good morning/afternoon everyone. My name is Megha, and I lead the Master Data Service engineering for the Ethiopia Agri-Stack.
Today, I am pleased to present the Master Data Service (MDS), which serves as the foundational Digital Public Infrastructure (DPI) for the entire Ethiopian agricultural ecosystem.
Over this session, we will demonstrate the four core pillars agreed upon:
1. Our 125 Available Datasets & National Reference Catalogues.
2. Authorized Login & CRUD operations in sandbox drafts.
3. Our Four-Eyes Maker-Checker approval and rejection workflow.
4. Live Integration Workflow showing how updates in MDS immediately reflect across the Farmer Registry (FR), Civil/Social Registry (CSR), and Livestock Registry (LR).""")

    # ==========================================
    # SLIDE 2: AGENDA
    # ==========================================
    s2 = create_base_slide(
        "Executive Demo Agenda: The 4 Key Demonstration Pillars",
        "Structured walkthrough demonstrating foundational DPI capabilities from curation to registry syndication."
    )
    add_card(s2, Inches(0.8), Inches(1.8), Inches(2.7), Inches(5.0), "1. Available Catalogues", [
        "125 live reference datasets on develop.",
        "Crops, Seeds, Livestock, Inputs & Geography.",
        "Canonical standard codes (e.g. TEFF, BORAN).",
        "Multilingual labels in English & Amharic.",
        "Centralized DPI taxonomy."
    ], ACCENT_CYAN, "Pillar 1")

    add_card(s2, Inches(3.8), Inches(1.8), Inches(2.7), Inches(5.0), "2. Login & CRUD Ops", [
        "Keycloak RBAC authentication.",
        "Maker User: alex.carter (MoA).",
        "Sandbox Draft Isolation: zero risk to prod.",
        "Create new entries & attribute schemas.",
        "Update metadata & soft-retire obsolete codes."
    ], ACCENT_GREEN, "Pillar 2")

    add_card(s2, Inches(6.8), Inches(1.8), Inches(2.7), Inches(5.0), "3. Maker-Checker", [
        "Strict Four-Eyes Governance principle.",
        "Maker submits draft with Change Notes.",
        "Checker (admin) inspects visual Diff tab.",
        "Approve / Reject decision with audit trail.",
        "Atomic publication & materialization."
    ], ACCENT_AMBER, "Pillar 3")

    add_card(s2, Inches(9.8), Inches(1.8), Inches(2.7), Inches(5.0), "4. Registry Integration", [
        "Farmer Registry (FR) live dropdowns.",
        "Civil & Social Registry (CSR) lookups.",
        "Livestock Registry (LR) breed validation.",
        "Dynamic REST APIs (/get_list_values).",
        "Zero-downtime, instant data syndication."
    ], ACCENT_PURPLE, "Pillar 4")

    add_speaker_notes(s2, """[AGENDA OVERVIEW]
Here is our execution roadmap for today's session:
First, we review our Available Datasets in MDS—the 125 live catalogs that establish the canonical vocabulary for the national Agri-Stack.
Second, we demonstrate how an Authorized Maker logs in and performs CRUD operations in an isolated draft, ensuring production data is never corrupted.
Third, we walk through Four-Eyes Maker-Checker Governance: the Maker submits, the Checker reviews the exact side-by-side visual Diff, and approves it.
Fourth, we show the end-to-end Integration Workflow: how this change immediately propagates to the Farmer Registry, Civil/Social Registry, and Livestock Registry without code changes or restarts.""")

    # ==========================================
    # SLIDE 3: PILLAR 1 - AVAILABLE DATASETS
    # ==========================================
    s3 = create_base_slide(
        "Pillar 1: 125 Available Reference Datasets in MDS",
        "Standardized national reference catalogs curated, validated, and published in the development environment.",
        "PILLAR 1: DATASETS & CATALOGUES"
    )
    add_card(s3, Inches(0.8), Inches(1.8), Inches(3.6), Inches(5.0), "Agriculture & Crops", [
        "CROP_COMMODITY: 121 official crops (Teff, Barley, Wheat, Enset, Maize).",
        "SEED_VARIETY: 902 certified varieties (Ethio-Seed list registered).",
        "CROP_CATEGORY: 9 production groups (Cereals, Pulses, Oilseeds).",
        "FERTILIZER_TYPE & AGRO_CHEMICAL: Certified blends (NPSB, Urea, DAP)."
    ], ACCENT_CYAN)

    add_card(s3, Inches(4.8), Inches(1.8), Inches(3.6), Inches(5.0), "Livestock Registry", [
        "LIVESTOCK_SPECIES: 6 major species (Cattle, Camel, Sheep, Goat...).",
        "LIVESTOCK_BREED: 94 indigenous & exotic breeds (Boran, Horro, Fogera).",
        "LIVESTOCK_HEALTH_STATUS & DISEASE: Canonical animal health codes.",
        "LIVESTOCK_PRODUCTION_TYPE: Dairy, Meat, Draft power categories."
    ], ACCENT_GREEN)

    add_card(s3, Inches(8.8), Inches(1.8), Inches(3.6), Inches(5.0), "Social, Civil & Financial", [
        "CITIZENSHIP_CATEGORY & IDENTIFICATION_TYPE: National ID standards.",
        "ASSET_TYPE & COOKING_FUEL_TYPE: CSR socio-economic indicators.",
        "BANK_DOCUMENT_TYPE: Financial account verification lists.",
        "APPROVAL_STATUS & CONSENT_PURPOSE: Legal & privacy taxonomies."
    ], ACCENT_AMBER)

    add_speaker_notes(s3, """[PILLAR 1: AVAILABLE DATASETS]
MDS currently hosts 125 active reference datasets on our develop platform.
Let's highlight the primary domains:
- In Agriculture: We maintain 121 standardized crop commodities and 902 registered seed varieties directly aligned with the Ministry of Agriculture's Ethio-Seed catalog. We also cover certified fertilizer blends like NPSB, Urea 46-0-0, and DAP.
- In Livestock: We cover 6 major animal species, 94 indigenous breeds such as Boran, Fogera, and Horro cattle, and Blackhead Somali sheep, along with health and disease codes.
- In Social & Civil Registry: We provide canonical lists for citizen identification, socio-economic assets, cooking fuel types, and financial KYC documents.
Every entry features a permanent canonical code and multilingual display names in English and Amharic.""")

    # ==========================================
    # SLIDE 4: GEOGRAPHY ARCHITECTURE
    # ==========================================
    s4 = create_base_slide(
        "Pillar 1 (Contd): Administrative Geography Hierarchy & P-Codes",
        "Dedicated spatial hierarchy engine powering location dropdowns and GIS maps across all registries.",
        "PILLAR 1: GEOGRAPHY DPI"
    )
    add_card(s4, Inches(0.8), Inches(1.8), Inches(3.6), Inches(5.0), "4-Level Spatial Hierarchy", [
        "Country (l0): Ethiopia (ET).",
        "Region (l1): 14 Administrative Regions (Tigray, Afar, Amhara, Oromia...).",
        "Zone (l2): 107 Sub-regional Zones.",
        "Woreda (l3): 1,148 Woredas with GeoJSON boundary polygons.",
        "Kebele (l4): 21,037 total local units."
    ], ACCENT_CYAN)

    add_card(s4, Inches(4.8), Inches(1.8), Inches(3.6), Inches(5.0), "Standardized P-Codes & GIS", [
        "Every location has a unique P-code: e.g. ET04 for Oromia, ET0401 for Jimma Zone.",
        "Parent-Child Linking: Cascading dropdowns (Region -> Zone -> Woreda).",
        "GeoJSON Streaming: Real-time boundary rendering for dashboard maps.",
        "Offline ODK Support: Bundled into mobile survey forms."
    ], ACCENT_GREEN)

    add_card(s4, Inches(8.8), Inches(1.8), Inches(3.6), Inches(5.0), "Geography vs Codelists", [
        "Specialized Geography Engine: Stored in g2p_geo_version_units table.",
        "Queried via: POST /catalogue/get_geo_units.",
        "Consuming Registries: FR, LR, and CSR all query get_geo_units.",
        "Legacy flat 'REGION' dataset: Retained only for legacy backward compatibility."
    ], ACCENT_AMBER)

    add_speaker_notes(s4, """[GEOGRAPHY DPI & CLARIFICATION]
Geography is one of the most critical components of Master Data Service.
Unlike flat code lists, our Geography module is a true spatial hierarchy:
- It spans 4 administrative tiers: 14 Regions, 107 Zones, 1,148 Woredas, down to 21,037 Kebeles.
- Every unit is identified by an official P-code (such as ET04 for Oromia Region, and ET0401 for Jimma Zone).
- Consuming registries like Farmer Registry and Livestock Registry use POST /catalogue/get_geo_units to drive cascading dropdowns.
- Important clarification: In the UI, the 'Geography' tab hosts this spatial hierarchy with GIS polygons. The flat 'REGION' dataset in Datasets is a legacy backward-compatibility codelist. All registry integrations use the Geography module.""")

    # ==========================================
    # SLIDE 5: PILLAR 2 - AUTHORIZED CRUD
    # ==========================================
    s5 = create_base_slide(
        "Pillar 2: Authorized User Access & CRUD Lifecycle in Drafts",
        "Role-based access control protecting live production data while enabling flexible draft curation.",
        "PILLAR 2: LOGIN & CRUD"
    )
    add_card(s5, Inches(0.8), Inches(1.8), Inches(3.6), Inches(5.0), "Keycloak Authentication", [
        "Centralized IAM in Keycloak staff realm.",
        "Role Separation: Distinct Maker vs Checker user accounts.",
        "Maker Account: alex.carter (Ministry of Agriculture Maker).",
        "Checker Account: admin / moa.checker.",
        "Audited Sessions: Every action stamps user ID & timestamp."
    ], ACCENT_CYAN)

    add_card(s5, Inches(4.8), Inches(1.8), Inches(3.6), Inches(5.0), "Sandbox Draft Isolation", [
        "Zero-Risk Editing: Live published version (v6) remains untouched.",
        "Calling applications continue querying live version without interruption.",
        "Action: Maker clicks 'Open Draft' -> creates working version (v7 DRAFT).",
        "Supports change notes and rationale logging."
    ], ACCENT_GREEN)

    add_card(s5, Inches(8.8), Inches(1.8), Inches(3.6), Inches(5.0), "Draft CRUD Operations", [
        "CREATE: '+ Add entry' allows creating new codes (e.g. BORAN_CROSS_2026).",
        "UPDATE: Edit existing labels, localized translations, and properties.",
        "RETIRE (Delete): Soft-retire obsolete codes (preserves historical registry records).",
        "Schema Definition: Add dynamic JSON-schema validation fields."
    ], ACCENT_AMBER)

    add_speaker_notes(s5, """[PILLAR 2: LOGIN & CRUD]
Moving to our second pillar: User Access and CRUD operations.
- Security and governance are central to MDS. All authentication is managed via Keycloak with role-based access control (RBAC).
- An authorized Maker—such as alex.carter—cannot directly mutate published production data.
- Instead, the Maker opens a sandbox Draft. This creates an isolated working copy (for example, v7 Draft) based on the latest published version.
- Inside this draft, the Maker has full CRUD capabilities: they can add a new crop variety or livestock breed, update translations, or retire obsolete codes.
- Notice that we use soft-retirement rather than hard deletion. This ensures that past farmer registrations that reference retired codes remain 100% valid in the audit trail.""")

    # ==========================================
    # SLIDE 6: PILLAR 3 - MAKER-CHECKER GOVERNANCE
    # ==========================================
    s6 = create_base_slide(
        "Pillar 3: Four-Eyes Governance — Maker-Checker Workflow",
        "Ensuring data sovereignty and integrity: No single person can unilaterally change production reference data.",
        "PILLAR 3: MAKER-CHECKER"
    )
    add_card(s6, Inches(0.8), Inches(1.8), Inches(2.7), Inches(5.0), "1. Draft Creation", [
        "Role: Maker (alex.carter).",
        "Action: Opens Draft on dataset (e.g. LIVESTOCK_BREED).",
        "Adds / updates codes.",
        "Production version v6 remains active for registries."
    ], ACCENT_CYAN, "Step 1")

    add_card(s6, Inches(3.8), Inches(1.8), Inches(2.7), Inches(5.0), "2. Submit for Review", [
        "Action: Maker clicks 'Submit for approval'.",
        "Enters Change Note explaining business rationale.",
        "Status: Changes from DRAFT -> SUBMITTED.",
        "Lock: Draft is frozen against further edits."
    ], ACCENT_AMBER, "Step 2")

    add_card(s6, Inches(6.8), Inches(1.8), Inches(2.7), Inches(5.0), "3. Checker Diff Review", [
        "Role: Checker (admin).",
        "Maker cannot approve their own draft (separation of duties).",
        "Checker inspects Visual Diff tab: Green (adds), Yellow (edits), Red (retires)."
    ], ACCENT_CYAN, "Step 3")

    add_card(s6, Inches(9.8), Inches(1.8), Inches(2.7), Inches(5.0), "4. Decision & Publish", [
        "Action: Checker clicks 'Approve' or 'Reject' with notes.",
        "Effective Date: Defaults to immediate activation.",
        "Result: v7 atomically PUBLISHED · in effect.",
        "Database: g2p_catalogue_materialise_list runs."
    ], ACCENT_GREEN, "Step 4")

    add_speaker_notes(s6, """[PILLAR 3: MAKER-CHECKER WORKFLOW]
Our third pillar is the Maker-Checker workflow, enforcing the Four-Eyes principle.
In national digital infrastructure, reference data governance is critical. The workflow proceeds through four stages:
1. The Maker initiates changes in a draft.
2. The Maker submits the draft with a business change note. The draft is immediately frozen to prevent tampering.
3. An independent Checker logs in. The platform enforces that the Maker cannot approve their own submission. The Checker reviews the exact side-by-side Visual Diff, where green highlights new additions, yellow shows metadata edits, and red indicates retirements.
4. The Checker makes a formal decision: Approving with an approval note (or Rejecting with rework instructions). Upon approval, the draft atomically materializes into the new live version v7, ready for ecosystem consumption.""")

    # ==========================================
    # SLIDE 7: PILLAR 4 - REGISTRY INTEGRATION
    # ==========================================
    s7 = create_base_slide(
        "Pillar 4: Interoperability & Integration with FR, CSR, and LR",
        "Eliminating data silos: External registries query MDS as the single source of truth over secure REST APIs.",
        "PILLAR 4: REGISTRY INTEGRATION"
    )
    add_card(s7, Inches(0.8), Inches(1.8), Inches(3.6), Inches(5.0), "Farmer Registry (FR)", [
        "Crops & Varieties: Dropdowns populated dynamically via POST /catalogue/get_list_values.",
        "Fertilizers & Inputs: Validates subsidy eligibility.",
        "Cascading Geography: Region -> Zone -> Woreda dropdowns powered by /catalogue/get_geo_units.",
        "Zero local code duplication in FR."
    ], ACCENT_CYAN)

    add_card(s7, Inches(4.8), Inches(1.8), Inches(3.6), Inches(5.0), "Livestock Registry (LR)", [
        "Animal Breeds & Species: Dynamic lookups for cattle, camel, and sheep breeds.",
        "Health & Disease Codes: Standardized epidemiological tracking.",
        "Veterinary Verification: Single-item verification via POST /catalogue/get_list_value.",
        "Standardized census data reporting."
    ], ACCENT_AMBER)

    add_card(s7, Inches(8.8), Inches(1.8), Inches(3.6), Inches(5.0), "Civil & Social Registry (CSR)", [
        "Socio-Economic Taxonomies: Asset types, citizenship categories, and identification types.",
        "Beneficiary Verification: Validates national ID types during onboarding.",
        "P-Code Location Matching: Ensures social welfare benefits match official Woreda boundaries."
    ], ACCENT_GREEN)

    add_speaker_notes(s7, """[PILLAR 4: REGISTRY INTEGRATION ARCHITECTURE]
Now we arrive at the core value of MDS: Interoperability with consuming registries.
Consuming registries do not store static, duplicated copies of reference data.
- The Farmer Registry (FR) integrates via REST APIs: When an extension agent registers a farm, the crop, seed variety, and fertilizer dropdowns are populated directly by calling MDS.
- The Livestock Registry (LR) queries MDS for certified livestock species and indigenous breeds like Boran or Fogera.
- The Civil and Social Registry (CSR) validates beneficiary ID types, household asset types, and geographic residency against canonical P-codes.
This ensures that the moment data is updated in MDS, all three registries remain 100% harmonized without manual database synchronization.""")

    # ==========================================
    # SLIDE 8: END-TO-END DATA REFLECTION FLOW
    # ==========================================
    s8 = create_base_slide(
        "Pillar 4 (Contd): Real-Time Data Reflection Lifecycle",
        "Step-by-step trace showing how modifying a record in MDS instantly reflects in FR, CSR, and LR.",
        "PILLAR 4: SYNDICATION LIFECYCLE"
    )
    add_card(s8, Inches(0.8), Inches(1.8), Inches(3.6), Inches(5.0), "1. MDS Modification", [
        "Step 1: Maker edits record in MDS draft (e.g. adds new breed BORAN_CROSS_2026).",
        "Step 2: Maker submits draft for review.",
        "Step 3: Checker approves draft.",
        "Step 4: MDS triggers materialization -> v7 becomes active."
    ], ACCENT_CYAN, "MDS Phase")

    add_card(s8, Inches(4.8), Inches(1.8), Inches(3.6), Inches(5.0), "2. Secure API Syndication", [
        "M2M Authentication: Registries authenticate via Keycloak Client Credentials.",
        "Standard OpenG2P Envelope: Complete audit traceability (request_id, sender_app).",
        "Endpoint 1: POST /catalogue/get_list_values (returns newly approved active values).",
        "Endpoint 2: POST /catalogue/get_geo_units."
    ], ACCENT_GREEN, "API Transport")

    add_card(s8, Inches(8.8), Inches(1.8), Inches(3.6), Inches(5.0), "3. Registry Consumption", [
        "Web Registration Dropdowns: Refresh dynamically on form load.",
        "Field Ingestion Validation: Incoming survey records validate against new code.",
        "Zero Redeployment: Consuming registries reflect changes instantly with zero downtime."
    ], ACCENT_PURPLE, "Registry Phase")

    add_speaker_notes(s8, """[DATA REFLECTION LIFECYCLE]
Let's trace how an update moves from MDS to the consuming registries in real time:
1. In MDS, the Maker opens a draft, creates a new entry (for instance, a new certified breed 'BORAN_CROSS_2026'), and submits it. The Checker approves it, making version 7 live.
2. Consuming registries connect using M2M client credentials. They call POST /catalogue/get_list_values.
3. Because the API queries the active materialized version, the newly approved breed appears immediately with status ACTIVE.
4. When a farmer or livestock record is submitted in FR or LR, it validates against MDS in real time.
No registry developer has to touch registry databases, run migration scripts, or restart services. The single source of truth updates the entire ecosystem instantly.""")

    # ==========================================
    # SLIDE 9: OFFLINE ODK FIELD COLLECTION
    # ==========================================
    s9 = create_base_slide(
        "Offline Field Synchronization & Mobile ODK Collect",
        "Ensuring agricultural enumerators in remote rural areas can collect validated data without active internet.",
        "EXTENDED CAPABILITIES"
    )
    add_card(s9, Inches(0.8), Inches(1.8), Inches(3.6), Inches(5.0), "Automated CSV Itemsets", [
        "Endpoint: GET /public/datasets/{code}/download.csv.",
        "Generates clean itemsets.csv bundled directly into ODK Collect mobile forms.",
        "Enables instant offline cascading search for crops, varieties, and fertilizers.",
        "Zero network dependency during rural farmer enumeration."
    ], ACCENT_CYAN)

    add_card(s9, Inches(4.8), Inches(1.8), Inches(3.6), Inches(5.0), "P-Code Geographic Alignment", [
        "Endpoint: GET /public/geography/levels/{level}/units.csv.",
        "Distributes 1,148 Woredas and 107 Zones as lightweight offline files.",
        "Guarantees that GPS points taken in the field tie to official P-codes.",
        "Eliminates manual post-survey geographic reconciliation."
    ], ACCENT_GREEN)

    add_card(s9, Inches(8.8), Inches(1.8), Inches(3.6), Inches(5.0), "DCAT-3 & Open Data Feeds", [
        "GET /public/catalog provides DCAT-3 and SKOS JSON-LD metadata feeds.",
        "Cross-ministerial data syndication with national portals.",
        "ETag caching & per-IP rate limiting protecting upstream servers.",
        "Full compliance with international open data standards."
    ], ACCENT_AMBER)

    add_speaker_notes(s9, """[OFFLINE FIELD COLLECTION & ODK]
A crucial real-world consideration in Ethiopia is rural connectivity. In many woredas, enumerators have zero cellular connectivity.
MDS addresses this natively:
- We provide automated CSV export endpoints that generate ODK-compatible itemsets.csv files.
- These files are bundled directly into mobile ODK Collect XForms on Android tablets.
- Enumerators in remote fields can search and select official crops, varieties, and fertilizer blends with instant response times, completely offline.
- When enumerators return to cellular coverage and sync back, their submitted records match MDS P-codes and commodity IDs perfectly, without requiring tedious manual data cleansing.""")

    # ==========================================
    # SLIDE 10: DEMO SUMMARY & ROADMAP
    # ==========================================
    s10 = create_base_slide(
        "Demo Summary & Live Walkthrough Roadmap",
        "Transitioning to the live interactive demonstration on the develop portal.",
        "LIVE DEMONSTRATION"
    )
    add_card(s10, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0), "Key Takeaways Recap", [
        "Authoritative DPI: 125 standardized reference datasets live on develop.",
        "Spatial Hierarchy: 21,037 Administrative Geography units with GeoJSON maps.",
        "Security & RBAC: Strict Keycloak role segregation (Maker vs Checker).",
        "Four-Eyes Governance: Sandboxed drafts, visual diff reviews, and immutable approval logging.",
        "Instant Interoperability: Direct REST API consumption by Farmer, Livestock, and Social Registries.",
        "Offline Ready: Native ODK CSV itemset generation for rural enumeration."
    ], ACCENT_GREEN)

    add_card(s10, Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.0), "Live Interactive Demo Steps", [
        "Step 1: Explore live catalog datasets & Geography hierarchy on MDS Portal.",
        "Step 2: Log in as Maker (alex.carter) -> Open Draft -> Add new record.",
        "Step 3: Submit Draft -> Switch to Checker (admin) -> Inspect Visual Diff -> Approve.",
        "Step 4: Execute Postman API check (/get_list_values) showing live data reflection.",
        "Step 5: Open Q&A and stakeholder discussion."
    ], ACCENT_CYAN)

    add_speaker_notes(s10, """[TRANSITION TO LIVE DEMO]
To summarize before we switch to the live demonstration:
Master Data Service provides the single, authoritative data language for the Ethiopia Agri-Stack.
With 125 curated datasets, 21,000 geography units, Four-Eyes Maker-Checker governance, and high-performance APIs for Farmer, Livestock, and Social Registries, the platform is fully ready.
I will now share my browser screen and walk through our 4 live verification steps:
1. Exploring the Catalogues & Geography Portal.
2. Logging in as Maker to perform a draft CRUD operation.
3. Submitting and having our Checker review the Diff and Approve.
4. Calling the Integration APIs to verify live data reflection.
Thank you, and let's jump straight into the live platform.""")

    output_path = "/home/user/master-data-standalone/MDS_Client_Demo_Presentation.pptx"
    prs.save(output_path)
    print(f"Presentation successfully generated at: {output_path}")

if __name__ == "__main__":
    create_deck()
