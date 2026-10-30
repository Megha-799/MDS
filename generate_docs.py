import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def create_document():
    doc = docx.Document()

    # Page Margins
    for s in doc.sections:
        s.top_margin = Inches(0.8)
        s.bottom_margin = Inches(0.8)
        s.left_margin = Inches(0.8)
        s.right_margin = Inches(0.8)

    # Styles & Colors
    PRIMARY = RGBColor(24, 76, 120)     # Navy Blue
    SECONDARY = RGBColor(41, 128, 185)  # Soft Blue
    DARK_TEXT = RGBColor(44, 62, 80)    # Charcoal
    MUTED = RGBColor(127, 140, 141)

    # Title
    title = doc.add_paragraph()
    title_run = title.add_run("OpenG2P Master Data Service (MDS)")
    title_run.font.name = 'Calibri'
    title_run.font.size = Pt(26)
    title_run.font.bold = True
    title_run.font.color.rgb = PRIMARY
    title.paragraph_format.space_after = Pt(2)

    subtitle = doc.add_paragraph()
    sub_run = subtitle.add_run("Comprehensive QA Tester, Operations & Registry Developer Handbook")
    sub_run.font.name = 'Calibri'
    sub_run.font.size = Pt(15)
    sub_run.font.color.rgb = SECONDARY
    subtitle.paragraph_format.space_after = Pt(14)

    # Metadata Banner
    meta_table = doc.add_table(rows=1, cols=1)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_cell = meta_table.cell(0, 0)
    meta_cell.width = Inches(6.9)
    set_cell_background(meta_cell, "F2F4F7")
    set_cell_margins(meta_cell, top=120, bottom=120, left=180, right=180)
    mp = meta_cell.paragraphs[0]
    mp.paragraph_format.space_after = Pt(0)
    mr1 = mp.add_run("Target Audience: ")
    mr1.bold = True
    mr1.font.color.rgb = DARK_TEXT
    mp.add_run("QA Automation Engineers, Testers, Registry Integrators (Farmer, Livestock, Crop), and MoA Stakeholders\n")
    mr2 = mp.add_run("Environments: ")
    mr2.bold = True
    mp.add_run("Staging (https://master-data-ui.development.oanstaging.com) | Local Standalone (http://localhost:3005)\n")
    mr3 = mp.add_run("Core Architecture: ")
    mr3.bold = True
    mp.add_run("OpenG2P Gen 2 Master Data Engine with Keycloak Single Sign-On (SSO) & Four-Eyes Governance")

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # Helper function for Section Headings
    def add_heading(text, level=1):
        h = doc.add_paragraph()
        r = h.add_run(text)
        r.font.name = 'Calibri'
        r.bold = True
        if level == 1:
            r.font.size = Pt(18)
            r.font.color.rgb = PRIMARY
            h.paragraph_format.space_before = Pt(16)
            h.paragraph_format.space_after = Pt(6)
        elif level == 2:
            r.font.size = Pt(14)
            r.font.color.rgb = SECONDARY
            h.paragraph_format.space_before = Pt(12)
            h.paragraph_format.space_after = Pt(4)
        elif level == 3:
            r.font.size = Pt(12)
            r.font.color.rgb = DARK_TEXT
            h.paragraph_format.space_before = Pt(8)
            h.paragraph_format.space_after = Pt(2)
        return h

    # Helper function for tables
    def style_table(table, col_widths, headers, data):
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        hdr_cells = table.rows[0].cells
        for i, h_text in enumerate(headers):
            hdr_cells[i].text = h_text
            hdr_cells[i].paragraphs[0].runs[0].font.bold = True
            hdr_cells[i].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
            set_cell_background(hdr_cells[i], "184C78")
            set_cell_margins(hdr_cells[i], top=100, bottom=100, left=120, right=120)
            hdr_cells[i].width = Inches(col_widths[i])
        
        for row_idx, row_data in enumerate(data):
            row_cells = table.add_row().cells
            bg = "FFFFFF" if row_idx % 2 == 0 else "F8FAFC"
            for col_idx, cell_value in enumerate(row_data):
                row_cells[col_idx].text = str(cell_value)
                set_cell_background(row_cells[col_idx], bg)
                set_cell_margins(row_cells[col_idx], top=80, bottom=80, left=120, right=120)
                row_cells[col_idx].width = Inches(col_widths[col_idx])
                p = row_cells[col_idx].paragraphs[0]
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.space_before = Pt(2)
                if len(p.runs) > 0:
                    p.runs[0].font.name = 'Calibri'
                    p.runs[0].font.size = Pt(9.5)
                    p.runs[0].font.color.rgb = DARK_TEXT

    # ==========================================
    # SECTION 1: USER ROLES & SEGREGATION OF DUTIES
    # ==========================================
    add_heading("1. User Roles & Segregation of Duties (Maker vs Checker)", level=1)
    
    p = doc.add_paragraph()
    p.add_run(
        "MDS enforces strict Maker-Checker governance. Reference data changes (such as crops, seed varieties, "
        "or livestock breeds) cannot be edited directly in production. Instead, changes must be drafted by an "
        "authorized Maker and independently approved by an authorized Checker."
    )

    add_heading("1.1 Maker User (Create Draft & Submit Only)", level=2)
    p = doc.add_paragraph()
    p.add_run("A Maker is responsible for preparing new entries or updates. They have the following configuration:\n")
    p.add_run("• Keycloak Client Roles: ").bold = True
    p.add_run("Reference Data Specialist, Data Editor (or MASTER_DATA_MAKER on staging)\n")
    p.add_run("• IAM Permissions Granted: ").bold = True
    p.add_run("referenceData:create, referenceData:edit, referenceData:view\n")
    p.add_run("• UI Capabilities: ").bold = True
    p.add_run("Can browse catalogs, click '+ Add entry', create draft versions, edit draft records, and click 'Submit for approval'.\n")
    p.add_run("• UI Restrictions: ").bold = True
    p.add_run("The 'Approve' and 'Publish' buttons are hidden/disabled. They cannot publish changes.")

    add_heading("1.2 Checker User (Approve / Reject Only)", level=2)
    p = doc.add_paragraph()
    p.add_run("A Checker is a senior officer or data steward who reviews drafts for quality:\n")
    p.add_run("• Keycloak Client Roles: ").bold = True
    p.add_run("Data Approver, Data Supervisor, or MASTER_DATA_CHECKER\n")
    p.add_run("• IAM Permissions Granted: ").bold = True
    p.add_run("referenceData:publish, geo:publish, referenceData:view\n")
    p.add_run("• UI Capabilities: ").bold = True
    p.add_run("Can access 'Awaiting approval' items, inspect full version diffs, approve (publish) drafts, or reject drafts with a decision note.\n")
    p.add_run("• UI Restrictions: ").bold = True
    p.add_run("Cannot create draft versions or edit entry values.")

    add_heading("1.3 Hard System Rule: Segregation of Duties", level=2)
    callout = doc.add_table(rows=1, cols=1)
    c_cell = callout.cell(0, 0)
    c_cell.width = Inches(6.9)
    set_cell_background(c_cell, "FEF3C7")
    set_cell_margins(c_cell, top=100, bottom=100, left=150, right=150)
    cp = c_cell.paragraphs[0]
    cpr = cp.add_run("MANDATORY SEGREGATION OF DUTIES (created_by != decided_by):\n")
    cpr.bold = True
    cpr.font.color.rgb = RGBColor(180, 83, 9)
    cp.add_run(
        "Even if an administrator (like alex.carter or admin) holds both Maker and Checker roles, the system "
        "strictly forbids a user from approving their own draft. If User A submitted draft v3, User B MUST review "
        "and approve it. If User A attempts to approve their own draft, the API returns: "
        "'You created this draft; another authorized user must approve it.'"
    )

    add_heading("1.4 Troubleshooting: 'Waiting for a user with publish permission'", level=2)
    p = doc.add_paragraph()
    p.add_run(
        "If a user opens a submitted draft and sees the yellow alert: 'Submitted: waiting for a user with publish permission to approve or reject it', "
        "it means that user currently lacks the 'publish' permission in Keycloak for that client. To fix this:\n"
        "1. In Keycloak Admin Console -> Users -> Select the user (e.g. nina.patel or alex.carter).\n"
        "2. Role mapping tab -> Assign role -> Filter by clients.\n"
        "3. Under client 'master-data': Assign role 'MASTER_DATA_CHECKER' or 'MASTER_DATA_ADMIN'.\n"
        "   (Under client 'farmer-registry-staff-portal': Assign role 'Data Supervisor' or 'Technical Administrator').\n"
        "4. Refresh the page: the Approve and Reject buttons will immediately appear."
    )

    # ==========================================
    # SECTION 2: END-TO-END APPROVAL WORKFLOW
    # ==========================================
    add_heading("2. End-to-End Approval Workflow (Four-Eyes Governance)", level=1)
    p = doc.add_paragraph()
    p.add_run(
        "The approval workflow governs how new entries and edits transition from initial draft to official published baseline. "
        "It protects downstream registries from breaking changes and guarantees an immutable audit trail."
    )

    add_heading("2.1 Lifecycle State Machine", level=2)
    t_wf = doc.add_table(rows=1, cols=4)
    style_table(
        t_wf,
        [1.3, 1.2, 2.4, 2.0],
        ["State", "Owner / Role", "Allowed Actions", "System Enforcement"],
        [
            [
                "PUBLISHED (vN)",
                "System Baseline",
                "• Read-only for registries\n• Clone to create new draft",
                "Immutable. Database triggers block direct UPDATE or DELETE operations."
            ],
            [
                "DRAFT (vN+1)",
                "Maker (Author)",
                "• Add new entries (upsert)\n• Edit existing draft entries\n• Retire deprecated entries\n• Discard unsubmitted draft",
                "Visible only to authorized makers/checkers. Not visible to external registry lookups."
            ],
            [
                "SUBMITTED",
                "Checker (Reviewer)",
                "• Review version diff\n• Approve (Publish)\n• Reject (with decision note)",
                "Draft is LOCKED. No further entry edits allowed unless rejected back or reopened."
            ],
            [
                "APPROVED (vN+1)",
                "Checker",
                "• System bumps active version\n• Publishes to live registries",
                "Immediately becomes the new default baseline served to registries."
            ],
            [
                "REJECTED",
                "Checker / Maker",
                "• Review decision note\n• Copy to a new draft to rework\n• Discard draft",
                "Remains in audit history with decision rationale for governance compliance."
            ]
        ]
    )

    add_heading("2.2 Step-by-Step Walkthrough (UI & API)", level=2)
    p = doc.add_paragraph()
    p.add_run("Step 1: Draft Creation (Maker)\n").bold = True
    p.add_run(
        "The Maker opens a catalog (e.g. CROP_COMMODITY) and clicks '+ Add entry'. If no draft is open, MDS creates "
        "a new draft version (e.g. version 4 based on version 3). In API: POST /catalogue/create_list_draft with list_code.\n\n"
    )
    p.add_run("Step 2: Adding / Editing Entries (Maker)\n").bold = True
    p.add_run(
        "The Maker enters the value_code (e.g. 'CROP_BARLEY_NEW'), display name, translations, and domain attributes. "
        "The entry is saved into the draft. In API: POST /catalogue/upsert_draft_values.\n\n"
    )
    p.add_run("Step 3: Submission for Approval (Maker)\n").bold = True
    p.add_run(
        "Once all changes are staged, the Maker enters a change note (e.g. 'Added certified lowland barley varieties') "
        "and clicks 'Submit for approval'. Status transitions from DRAFT to SUBMITTED. In API: POST /catalogue/submit_draft.\n\n"
    )
    p.add_run("Step 4: Independent Review & Decision (Checker)\n").bold = True
    p.add_run(
        "A separate Checker logs in, navigates to the dataset page, and clicks the grey 'View draft' button (or selects Draft v4 from dropdown). "
        "The UI displays the diff highlighting added, modified, and retired values.\n"
        "• To Approve: Checker clicks 'Approve', enters optional decision note. Draft becomes the new live PUBLISHED version (v4).\n"
        "• To Reject: Checker clicks 'Reject' and enters mandatory explanation. Draft is marked REJECTED."
    )

    add_heading("2.3 QA Testing Test Cases for Approval Workflow", level=2)
    t_tc = doc.add_table(rows=1, cols=3)
    style_table(
        t_tc,
        [1.8, 2.5, 2.6],
        ["Test Case ID & Scenario", "Steps to Execute", "Expected Result"],
        [
            [
                "TC-WF-01: Happy Path Full Lifecycle",
                "1. Login as Maker\n2. Create draft on CROP_CATALOG\n3. Add new entry TEST_01\n4. Submit draft\n5. Login as Checker\n6. Approve draft",
                "Draft publishes successfully. Active version increments. New entry is immediately returned in /public/datasets/CROP_CATALOG/entries."
            ],
            [
                "TC-WF-02: Segregation of Duties Violation",
                "1. Login as Admin User\n2. Create and submit draft\n3. Attempt to approve own draft as Admin User",
                "System blocks approval with 403 Forbidden: 'User who created the draft cannot approve it. Independent reviewer required.'"
            ],
            [
                "TC-WF-03: Rejection & Resubmission Flow",
                "1. Maker submits draft\n2. Checker clicks Reject with note 'Invalid botanical code'\n3. Maker reviews rejected status\n4. Maker creates reworked draft copy",
                "Original draft is marked REJECTED with note preserved in audit trail. New draft incorporates feedback."
            ],
            [
                "TC-WF-04: Immutability Guard",
                "Attempt to run direct SQL UPDATE on g2p_list_version_values where status = 'PUBLISHED'.",
                "Database trigger 'trg_g2p_list_versions_guard' fires and aborts transaction with error."
            ]
        ]
    )

    # ==========================================
    # SECTION 3: RELEASES & REGISTRY CONSUMPTION
    # ==========================================
    add_heading("3. Catalogue Releases & Registry Data Consumption Modes", level=1)
    p = doc.add_paragraph()
    p.add_run(
        "A Release is an official, immutable snapshot bundle (e.g. '2026.1' or 'ETH-2026-Q1') that pins together "
        "a specific Geography version (e.g. v2) and specific published versions of chosen datasets. "
        "This allows registries (Farmer Registry, Crop Registry, Livestock Registry) to synchronize reference codes."
    )

    add_heading("3.1 Step-by-Step: How to Create and Publish a Release", level=2)
    p = doc.add_paragraph()
    p.add_run("Follow these steps to create an official release snapshot:\n")
    p.add_run("1. In the left navigation menu, click 'Releases'.\n")
    p.add_run("2. Click the '+ Create release' button in the top right.\n")
    p.add_run("3. In the popup modal, enter:\n")
    p.add_run("   • Release Code (Required): A version string, e.g. '2026.1' or 'ETH-2026-Q1'.\n")
    p.add_run("   • Title (Optional): e.g. 'Ethiopia Agricultural Reference Baseline 2026'.\n")
    p.add_run("   • Note (Optional): Context regarding the release.\n")
    p.add_run("   Click 'Create release'. The release is created in DRAFT status.\n")
    p.add_run("4. Click on the newly created draft row in the table to display its detail panel below.\n")
    p.add_run("5. Click the 'Set members' button:\n")
    p.add_run("   • Click 'Pin all versions in effect' to automatically lock in the active version of all catalogs and geography.\n")
    p.add_run("   • Or individually select datasets and assign their specific version numbers.\n")
    p.add_run("   Click 'Save members'.\n")
    p.add_run("6. Click the 'Publish' button. Confirm the popup prompt. The release becomes completely immutable.\n")
    p.add_run("   *(Note: Under Maker-Checker rules, if you created the release or last set members, another user must click Publish).*")

    add_heading("3.2 How Registries Fetch Data: Released vs Latest Published", level=2)
    p = doc.add_paragraph()
    p.add_run(
        "When external registries or downstream developer services query Master Data, they can operate in distinct modes:\n"
    )

    t_rel = doc.add_table(rows=1, cols=4)
    style_table(
        t_rel,
        [1.5, 1.8, 1.8, 1.8],
        ["Consumption Mode", "API Request", "What Registry Receives", "Use Case"],
        [
            [
                "Mode 1: Default / Latest Published (Dynamic)",
                "GET /public/datasets/{code}/entries",
                "Always returns the latest approved and published version currently in effect.",
                "Standard operational mode. As soon as MoA approves new crops/seeds, registries receive updates automatically."
            ],
            [
                "Mode 2: Pinned by Release (Frozen Bundle)",
                "GET /public/releases/{release_code}",
                "Returns the exact snapshot versions locked into that release (e.g. 2026.1).",
                "Certified annual baselines, offline field mobile sync, and audit-sensitive data collection."
            ],
            [
                "Mode 3: Pinned by Version Number",
                "GET /public/datasets/{code}/entries?version=3",
                "Returns specifically version 3, regardless of newer versions published later.",
                "Historic registration lookups and backwards compatibility testing."
            ],
            [
                "Mode 4: Point-in-Time Lookup (as_of)",
                "GET /public/datasets/{code}/entries?as_of=2026-06-01T00:00:00Z",
                "Returns the version that was active on that exact historical timestamp.",
                "Regulatory dispute resolution, historic compliance verification."
            ]
        ]
    )

    # ==========================================
    # SECTION 4: REAL-TIME BULK IMPORT
    # ==========================================
    add_heading("4. How Bulk Import Works in Real Time", level=1)
    p = doc.add_paragraph()
    p.add_run(
        "In production and staging, master data is never directly inserted via arbitrary SQL scripts because doing so "
        "bypasses data triggers, audit trails, and version immutability. Instead, official mechanisms exist for bulk import:"
    )

    t1 = doc.add_table(rows=1, cols=3)
    style_table(
        t1, 
        [1.8, 2.5, 2.6],
        ["Import Mechanism", "How it Works in Real Time", "When to Use"],
        [
            [
                "1. Country Pack JSON Loader (Automated Seeding)",
                "Data is structured as JSON files in 'packs/ETH-OAN/'. The seeder container validates data schema with 'validate_pack.py' and calls Master Data ingestion. Initial import publishes Version 1; subsequent deployments create drafts for approval.",
                "Official releases, baseline deployments, CI/CD pipeline deployments, and large official government datasets."
            ],
            [
                "2. Batch API Bulk Ingestion (/catalogue/upsert_draft_values)",
                "Admins/Testers open a draft version via API, post a JSON array of up to thousands of entries to '/catalogue/upsert_draft_values', verify the diff, and submit the draft batch for approval.",
                "Programmatic bulk imports, syncing reference tables from external government ERPs or staging databases."
            ],
            [
                "3. GeoJSON Boundary Bulk Upload",
                "Administrative level boundaries are uploaded via '/catalogue/upload_draft_boundary' as standard GeoJSON FeatureCollections, mapped to P-codes and stored in MinIO S3 object storage.",
                "Importing geographic boundaries (Regions, Zones, Woredas, Kebeles) for spatial map visualization."
            ]
        ]
    )

    # ==========================================
    # SECTION 5: DASHBOARD & HOME EXPLANATION
    # ==========================================
    add_heading("5. Dashboard & Home UI Walkthrough", level=1)
    p = doc.add_paragraph()
    p.add_run(
        "The MDS Home page provides real-time visibility into all master data catalogs, active drafts, and review queues. "
        "Below is an explanation of every component on the dashboard:"
    )

    t2 = doc.add_table(rows=1, cols=3)
    style_table(
        t2,
        [1.8, 2.0, 3.1],
        ["Dashboard Element", "Display Format", "Detailed Explanation"],
        [
            [
                "DATASETS Metric Card",
                "Total Count & Themes (e.g. 105 Datasets, 3 Themes)",
                "Shows the total number of distinct reference datasets registered in the system and their thematic groupings."
            ],
            [
                "GEOGRAPHY Metric Card",
                "Version & Units (e.g. v2, 21,037 administrative units)",
                "Displays the currently active geography version and total count of administrative units down to the Kebele level."
            ],
            [
                "PENDING WORK Card",
                "Count & Breakdown (e.g. 2 Pending: 1 awaiting approval, 1 drafts)",
                "Work-in-progress indicator. Alerts team members how many drafts need review (awaiting approval) vs how many are being authored."
            ],
            [
                "RELEASES Metric Card",
                "Release Count (e.g. 1 / Latest: 2026.1)",
                "Official immutable release bundles that pin together specific dataset versions and geography versions for external registries."
            ],
            [
                "Datasets by Theme",
                "Categorized Badges (Core: 43, Agriculture: 41, etc.)",
                "Browsing grid. Clicking any theme pill or dataset badge filters records. Orange indicator dots highlight datasets with active drafts."
            ],
            [
                "Geography Summary Card",
                "Country Code & Level Counts (Country: 1, Region: 14, Zone: 125, Woreda: 1,362, Kebele: 19,535)",
                "Hierarchical breakdown of Ethiopia's administrative structure with status badge (e.g. 'v2 IN EFFECT')."
            ],
            [
                "Pending Work Drawer",
                "Awaiting Approval & Drafts In Progress Lists",
                "Action center: Checkers click 'Review' to inspect diffs and approve; Makers click 'Continue' to finish drafting."
            ],
            [
                "Navigation Sidebar",
                "Home, Datasets, Geography, Releases, Activity",
                "Direct navigation across the primary management views of the Master Data Service."
            ]
        ]
    )

    # ==========================================
    # SECTION 6: DATASET CREATION & FIELDS
    # ==========================================
    add_heading("6. Dataset Creation, Fields & Schema Explanation", level=1)
    p = doc.add_paragraph()
    p.add_run(
        "A Dataset (or Catalog) in MDS represents a governed list of allowed master reference values (e.g. Crops, Fertilizers, Breeds). "
        "Below are the instructions for creating new datasets and the complete schema definition."
    )

    add_heading("6.1 Step-by-Step: How to Create a New Dataset", level=2)
    p = doc.add_paragraph()
    p.add_run("Follow these steps to create a new reference dataset:\n")
    p.add_run("1. Click 'Datasets' in the left sidebar menu.\n")
    p.add_run("2. Click the '+ Create dataset' button in the top right.\n")
    p.add_run("3. Fill in the Dataset Header Modal:\n")
    p.add_run("   • List Code (Required): Permanent uppercase key, e.g. 'SOIL_TYPE_CATALOG'.\n")
    p.add_run("   • Title / Display (Required): Human-readable name, e.g. 'Soil Type Catalog'.\n")
    p.add_run("   • Theme / Domain (Optional): e.g. 'agriculture', 'livestock', 'core'.\n")
    p.add_run("   • Description (Optional): Purpose and institutional authority.\n")
    p.add_run("   • Visibility: 'private' (default for internal registries) or 'public' (open data portal).\n")
    p.add_run("   • Is Hierarchical: Toggle ON if entries have parent-child relations.\n")
    p.add_run("   • License details: Optional (leave blank for internal government catalogs).\n")
    p.add_run("4. Click 'Create dataset'. MDS automatically initializes Version 1 in DRAFT status.\n")
    p.add_run("5. Add entries via '+ Add entry' (or batch API), submit the draft, and have an authorized Checker approve Version 1.\n")
    p.add_run("   API Equivalent: POST /catalogue/create_list with {list_code, display, domain, visibility}.")

    add_heading("6.2 Dataset-Level Metadata Fields & Licensing Policy", level=2)
    t3 = doc.add_table(rows=1, cols=3)
    style_table(
        t3,
        [1.8, 1.4, 3.7],
        ["Field Name", "Type", "Description & Purpose"],
        [
            ["list_code", "String (Required)", "Permanent uppercase system identifier (e.g. CROP_COMMODITY, SEED_CATALOG). Never changed."],
            ["display / title", "String (Required)", "Official human-readable name displayed in the UI (e.g. 'Crop Commodity Catalog')."],
            ["description", "String (Optional)", "Purpose of the dataset and source authority."],
            ["domain / theme", "String (Optional)", "Functional grouping (e.g. agriculture, livestock, geography, core)."],
            ["owner_org", "String (Optional)", "Responsible government body (e.g. 'Ministry of Agriculture (MoA)')."],
            ["is_hierarchical", "Boolean (Optional)", "True if entries have parent-child relations (e.g. Breed -> Species; Zone -> Region)."],
            ["visibility", "Enum (Optional)", "'private' (default; internal staff & registries only) or 'public' (published in open data catalog)."],
            ["licence_uri", "String (Optional)", "License URL terms (e.g. https://creativecommons.org/licenses/by/4.0/). Completely optional."],
            ["licence_label", "String (Optional)", "License title (e.g. 'CC-BY-4.0'). Optional; recommended only if visibility is public."],
            ["current_version_no", "Integer", "The version currently published and actively served to external registries."],
            ["open_draft_version_no", "Integer / Null", "Version number of open draft, or null if no edits are in progress."],
            ["open_draft_status", "Enum / Null", "State of the open draft: 'DRAFT', 'SUBMITTED', or null."]
        ]
    )

    p_lic = doc.add_paragraph()
    p_lic.add_run("Licensing Policy Note: ").bold = True
    p_lic.add_run(
        "For government registries (MoA, Farmer Registry), license fields should be left BLANK. "
        "Only specify licensing if the catalog is intentionally marked as 'public' for open-data portal distribution."
    )

    add_heading("6.3 Entry-Level Fields (Catalog Values)", level=2)
    t4 = doc.add_table(rows=1, cols=3)
    style_table(
        t4,
        [1.8, 1.4, 3.7],
        ["Entry Field", "Type", "Description & Purpose"],
        [
            ["value_code", "String (Required)", "Immutable unique business key (e.g. 'CROP_TEFF', 'FERT_UREA'). Stored in farmer registry records."],
            ["display", "String (Required)", "Official title / name displayed in registry dropdowns (e.g. 'Teff (Eragrostis tef)')."],
            ["display_i18n", "JSON Object (Optional)", "Multilingual localization dictionary, e.g. {'am': 'ጤፍ', 'or': 'Xaafii'}."],
            ["parent_code", "String / Null", "For hierarchical catalogs, the value_code of the parent entry."],
            ["sort_order", "Integer (Optional)", "Display sequence order in dropdown menus."],
            ["status", "Enum", "'ACTIVE' (live for selection) or 'RETIRED' (historic, cannot be selected for new records)."],
            ["attributes", "JSON Object (Optional)", "Domain-specific fields defined in schema (e.g. release_year, breeding_code, fertilizer_composition)."]
        ]
    )

    # ==========================================
    # SECTION 7: API REFERENCE FOR TESTERS & DEVS
    # ==========================================
    add_heading("7. API Reference for Testers & Registry Developers", level=1)
    p = doc.add_paragraph()
    p.add_run(
        "Registry developers (Farmer Registry, Livestock Registry, Crop Portal) and QA automation engineers "
        "can use these APIs to consume and manage reference data. All requests can be tested using the accompanying "
        "Postman collection 'MDS_QA_Testing_Collection.postman_collection.json'."
    )

    add_heading("7.1 Public Read-Only APIs (No Auth Required for Registries)", level=2)
    t5 = doc.add_table(rows=1, cols=3)
    style_table(
        t5,
        [2.3, 1.0, 3.6],
        ["Endpoint", "Method", "Description & Use Case"],
        [
            ["/public/datasets", "GET", "List all available catalogs, descriptions, themes, and current active version numbers."],
            ["/public/datasets/{list_code}/entries", "GET", "Fetch active entries for a catalog. Defaults to latest published version. Supports ?page=1&limit=100."],
            ["/public/datasets/{list_code}/download.json", "GET", "Download full catalog dataset as JSON for offline caching or registry sync."],
            ["/public/datasets/{list_code}/download.csv", "GET", "Download complete catalog as CSV for spreadsheet reporting."],
            ["/public/geography/levels", "GET", "Get all administrative levels (country, region, zone, woreda, kebele)."],
            ["/public/geography/units", "GET", "Fetch administrative units with P-codes, parent links, and localized names."],
            ["/public/releases", "GET", "List official published releases."],
            ["/public/releases/{code}", "GET", "Fetch full details and member version pins of a specific published release (e.g. 2026.1)."]
        ]
    )

    add_heading("7.2 Authenticated Management APIs (Maker-Checker Operations)", level=2)
    t6 = doc.add_table(rows=1, cols=3)
    style_table(
        t6,
        [2.3, 1.0, 3.6],
        ["Endpoint", "Method", "Description & Use Case"],
        [
            ["/catalogue/create_list", "POST", "Create a new master reference dataset."],
            ["/catalogue/get_lists", "POST", "Query all catalogs with open draft versions and author details."],
            ["/catalogue/get_list_values", "POST", "Retrieve all values of a specific version (works on both drafts and published)."],
            ["/catalogue/create_list_draft", "POST", "Maker creates a new draft version based on the latest published version."],
            ["/catalogue/upsert_draft_values", "POST", "Maker bulk-adds or updates entries in an open draft."],
            ["/catalogue/retire_draft_values", "POST", "Maker flags entries as RETIRED in the draft."],
            ["/catalogue/submit_draft", "POST", "Maker submits open draft for review (transitions status from DRAFT -> SUBMITTED)."],
            ["/catalogue/approve_draft", "POST", "Checker approves draft (publishes version; becomes the new live active baseline)."],
            ["/catalogue/reject_draft", "POST", "Checker rejects draft with a required decision note."],
            ["/catalogue/discard_draft", "POST", "Maker or Admin discards an unsubmitted draft."],
            ["/catalogue/create_release", "POST", "Create a new draft release bundle."],
            ["/catalogue/set_release_members", "POST", "Pin dataset versions and geography version into a draft release."],
            ["/catalogue/publish_release", "POST", "Publish release (becomes immutable)."]
        ]
    )

    output_path = "/home/user/master-data-standalone/MDS_Tester_and_Developer_Guide.docx"
    doc.save(output_path)
    print(f"Document updated successfully at: {output_path}")

if __name__ == '__main__':
    create_document()
