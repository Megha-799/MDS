#!/usr/bin/env python3
import json
import os
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

def style_table(table, col_widths, headers, data):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr_cells = table.rows[0].cells
    for i, h_text in enumerate(headers):
        hdr_cells[i].text = h_text
        if len(hdr_cells[i].paragraphs[0].runs) > 0:
            hdr_cells[i].paragraphs[0].runs[0].font.bold = True
            hdr_cells[i].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
            hdr_cells[i].paragraphs[0].runs[0].font.name = 'Calibri'
            hdr_cells[i].paragraphs[0].runs[0].font.size = Pt(9.5)
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
                p.runs[0].font.size = Pt(9)
                p.runs[0].font.color.rgb = RGBColor(44, 62, 80)

def build_docx():
    print("Loading Postman collection...")
    with open("MDS_Postman_Collection.json") as f:
        col = json.load(f)

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
            r.font.size = Pt(13.5)
            r.font.color.rgb = SECONDARY
            h.paragraph_format.space_before = Pt(12)
            h.paragraph_format.space_after = Pt(4)
        elif level == 3:
            r.font.size = Pt(11)
            r.font.color.rgb = DARK_TEXT
            h.paragraph_format.space_before = Pt(8)
            h.paragraph_format.space_after = Pt(2)
        return h

    # ==========================================
    # TITLE & HEADER
    # ==========================================
    title = doc.add_paragraph()
    r = title.add_run("OpenG2P Master Data Service (MDS)")
    r.font.name = 'Calibri'
    r.font.size = Pt(24)
    r.font.bold = True
    r.font.color.rgb = PRIMARY
    title.paragraph_format.space_after = Pt(2)

    subtitle = doc.add_paragraph()
    r = subtitle.add_run("Core Enterprise API Testing, QA Verification & Demo Handbook")
    r.font.name = 'Calibri'
    r.font.size = Pt(14)
    r.font.color.rgb = SECONDARY
    subtitle.paragraph_format.space_after = Pt(12)

    # Metadata Banner
    meta_table = doc.add_table(rows=1, cols=1)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_cell = meta_table.cell(0, 0)
    meta_cell.width = Inches(6.9)
    set_cell_background(meta_cell, "F2F4F7")
    set_cell_margins(meta_cell, top=120, bottom=120, left=180, right=180)
    mp = meta_cell.paragraphs[0]
    mp.paragraph_format.space_after = Pt(0)
    
    def add_meta_line(lbl, val):
        r1 = mp.add_run(lbl)
        r1.bold = True
        r1.font.name = 'Calibri'
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = DARK_TEXT
        r2 = mp.add_run(val + "\n")
        r2.font.name = 'Calibri'
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = DARK_TEXT

    add_meta_line("Target Audience: ", "QA Automation Engineers, Testers, Technical Facilitators, and Registry Integrators")
    add_meta_line("Backend Server: ", "https://master-data.development.oanstaging.com")
    add_meta_line("Authentication: ", "https://keycloak.development.oanstaging.com (Realm: staff, Client: admin-cli)")
    add_meta_line("Integration Paradigm: ", "Core OpenG2P RPC (POST with Keycloak Bearer Token & JSON Envelope)")

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # ==========================================
    # SECTION 1: ENVIRONMENT & ENVIRONMENT VARIABLES
    # ==========================================
    add_heading("1. Environment Configuration & Postman Variable Setup", level=1)
    
    p = doc.add_paragraph()
    p.add_run(
        "MDS is integrated directly with the OpenG2P Keycloak IAM service. All external registries "
        "(Farmer Registry, Crop Sown Registry, Livestock Registry) authenticate using standard OAuth2 "
        "tokens before querying reference data."
    )

    t_vars = doc.add_table(rows=1, cols=3)
    style_table(
        t_vars,
        [1.8, 2.8, 2.3],
        ["Variable Name", "Develop Staging Value", "Purpose in Collection"],
        [
            ["api_url", "https://master-data.development.oanstaging.com", "Master Data Core API Backend URL"],
            ["keycloak_url", "https://keycloak.development.oanstaging.com", "Keycloak Identity & Access Management Endpoint"],
            ["realm", "staff", "Target Keycloak Realm holding staff accounts"],
            ["client_id", "admin-cli", "OIDC Client with Reference Data permissions"],
            ["list_code", "CROP_CATALOG", "Default catalog for testing"],
            ["test_value_code", "TEST_CROP_QA_01", "Sample entry code for draft upsert tests"]
        ]
    )

    # User Accounts
    add_heading("1.1 Test User Accounts & Role Privileges", level=2)
    t_users = doc.add_table(rows=1, cols=4)
    style_table(
        t_users,
        [1.3, 1.2, 1.8, 2.6],
        ["Username", "Password", "Organization / Department", "Permissions & Role"],
        [
            ["moa.maker", "admin1", "Ministry of Agriculture (MoA)", "MAKER: Create drafts, add/edit entries, submit for review. CANNOT approve."],
            ["moa.checker", "admin1", "Ministry of Agriculture (MoA)", "CHECKER: Review diffs, approve (publish), or reject drafts. CANNOT draft."],
            ["ldi.specialist", "admin1", "Livestock Development Institute (LDI)", "SPECIALIST: Maker & Checker for livestock species and breeds."],
            ["csa.admin", "admin1", "Central Statistical Agency (CSA)", "GEO ADMIN: Administrative levels, P-codes, and boundary GeoJSON."],
            ["alex.carter", "admin1", "Global Administration", "TECHNICAL ADMIN: Full admin permissions across all catalogs."]
        ]
    )

    # ==========================================
    # SECTION 2: LIVE DEMO SCRIPT FOR TESTER
    # ==========================================
    add_heading("2. Step-by-Step QA Demo: How a Single Catalog Data is Retrieved", level=1)
    
    p = doc.add_paragraph()
    p.add_run(
        "Use this exact sequence during your demonstration to show the QA tester how external registries "
        "fetch, filter, and validate catalog data from MDS using authenticated Core OpenG2P endpoints."
    )

    # Demo 1
    add_heading("Step 1: Acquire Keycloak Token", level=2)
    p = doc.add_paragraph()
    p.add_run("• Endpoint: ").bold = True
    p.add_run("POST https://keycloak.development.oanstaging.com/realms/staff/protocol/openid-connect/token\n")
    p.add_run("• Body (x-www-form-urlencoded): ").bold = True
    p.add_run("client_id=admin-cli, username=moa.maker, password=admin1, grant_type=password\n")
    p.add_run("• Result: ").bold = True
    p.add_run("Acquires Bearer access token saved to {{maker_token}}.")

    # Demo 2
    add_heading("Step 2: Discover All Catalogs (POST /catalogue/get_lists)", level=2)
    p = doc.add_paragraph()
    p.add_run("Shows the tester that MDS acts as the central master repository for all national datasets.\n")
    p.add_run("• Endpoint: ").bold = True
    p.add_run("POST https://master-data.development.oanstaging.com/catalogue/get_lists\n")
    p.add_run("• Headers: ").bold = True
    p.add_run("Authorization: Bearer {{maker_token}}, Content-Type: application/json\n")
    p.add_run("• Request Payload:\n").bold = True
    p.add_run(
        "  {\n"
        "    \"request_header\": { \"sender_app_mnemonic\": \"farmer-registry\", \"request_id\": \"demo-01\" },\n"
        "    \"request_body\": { \"request_payload\": { \"include_unpublished\": false } }\n"
        "  }\n"
    )
    p.add_run("• What to Highlight: ").bold = True
    p.add_run("Status 200 SUCCESS. Lists all active published datasets (CROP_CATALOG, LIVESTOCK_CATALOG, INPUT_CATALOG, etc.).")

    # Demo 3
    add_heading("Step 3: Fetch Active Entries of a Single Catalog (POST /catalogue/get_list_values)", level=2)
    p = doc.add_paragraph()
    p.add_run("Demonstrates retrieving all active items (Teff, Bread Wheat, Maize, etc.) from CROP_CATALOG.\n")
    p.add_run("• Endpoint: ").bold = True
    p.add_run("POST https://master-data.development.oanstaging.com/catalogue/get_list_values\n")
    p.add_run("• Request Payload:\n").bold = True
    p.add_run(
        "  {\n"
        "    \"request_header\": { \"sender_app_mnemonic\": \"crop-sown-registry\", \"request_id\": \"demo-02\" },\n"
        "    \"request_body\": {\n"
        "      \"pagination_request\": { \"current_page\": 1, \"page_size\": 10, \"sort_by\": \"display\" },\n"
        "      \"request_payload\": { \"list_code\": \"CROP_CATALOG\", \"version\": \"latest\", \"include_retired\": false }\n"
        "    }\n"
        "  }\n"
    )
    p.add_run("• What to Highlight: ").bold = True
    p.add_run("Status 200 SUCCESS. Returns crops with full domain attributes (isolation distance, ecological zone, inspections needed).")

    # Demo 4
    add_heading("Step 4: Fetch a Single Record by Code (Single Entry Validation)", level=2)
    p = doc.add_paragraph()
    p.add_run("Demonstrates validating a single crop code during farmer parcel registration.\n")
    p.add_run("• Endpoint: ").bold = True
    p.add_run("POST https://master-data.development.oanstaging.com/catalogue/get_list_value\n")
    p.add_run("• Request Payload:\n").bold = True
    p.add_run(
        "  {\n"
        "    \"request_header\": { \"sender_app_mnemonic\": \"crop-sown-registry\", \"request_id\": \"demo-03\" },\n"
        "    \"request_body\": {\n"
        "      \"request_payload\": { \"list_code\": \"CROP_CATALOG\", \"value_code\": \"1\", \"version\": 1 }\n"
        "    }\n"
        "  }\n"
    )
    p.add_run("• What to Highlight: ").bold = True
    p.add_run("Returns exact single record with all registered attributes.")

    # Demo 5
    add_heading("Step 5: Cascading Child Records (Crop -> Variety)", level=2)
    p = doc.add_paragraph()
    p.add_run("Demonstrates filtering child varieties by parent crop name (e.g. Teff -> Quncho, Kora, Dagim).\n")
    p.add_run("• Endpoint: ").bold = True
    p.add_run("POST https://master-data.development.oanstaging.com/catalogue/get_list_values\n")
    p.add_run("• Request Payload:\n").bold = True
    p.add_run(
        "  {\n"
        "    \"request_header\": { \"sender_app_mnemonic\": \"crop-sown-registry\", \"request_id\": \"demo-04\" },\n"
        "    \"request_body\": {\n"
        "      \"pagination_request\": { \"current_page\": 1, \"page_size\": 50 },\n"
        "      \"request_payload\": {\n"
        "        \"list_code\": \"CROP_VARIETY_CATALOG\",\n"
        "        \"parent_code\": \"Teff\",\n"
        "        \"version\": \"latest\"\n"
        "      }\n"
        "    }\n"
        "  }\n"
    )
    p.add_run("• What to Highlight: ").bold = True
    p.add_run("Returns only varieties associated with Teff, including breeder, maintainer, and release year.")

    # Demo 6
    add_heading("Step 6: Cascading Administrative Geography (POST /catalogue/get_geo_units)", level=2)
    p = doc.add_paragraph()
    p.add_run("Demonstrates hierarchical cascading for administrative dropdowns:\n")
    p.add_run("• Level 1 Regions: POST /catalogue/get_geo_units with { \"level_id\": \"l1\" }\n")
    p.add_run("• Level 2 Zones: POST /catalogue/get_geo_units with { \"level_id\": \"l2\", \"parent_unit_id\": \"ET04\" }\n")
    p.add_run("• Level 3 Woredas: POST /catalogue/get_geo_units with { \"level_id\": \"l3\", \"parent_unit_id\": \"ET0401\" }\n")
    p.add_run("• Single P-code Resolve: POST /catalogue/get_geo_unit with { \"unit_id\": \"ET040103\" } (returns Dedo Woreda with full ancestry path).")

    # ==========================================
    # SECTION 3: COMPLETE EXHAUSTIVE CORE API REFERENCE
    # ==========================================
    add_heading("3. Complete Master Core API Reference", level=1)
    
    p = doc.add_paragraph()
    p.add_run(
        "Below is the complete reference of all Core OpenG2P endpoints supported on the develop backend "
        "(https://master-data.development.oanstaging.com), organized by functional module."
    )

    # Let's filter out folder 2 (public) to avoid any confusion!
    folders = [f for f in col.get("item", []) if not f.get("name", "").startswith("02. Open Catalogue")]
    
    for f_idx, folder in enumerate(folders):
        f_name = folder.get("name", "")
        items = folder.get("item", [])
        
        add_heading(f"{f_name} ({len(items)} Endpoints)", level=2)
        
        t_mod = doc.add_table(rows=1, cols=4)
        style_table(
            t_mod,
            [1.8, 0.8, 2.1, 2.2],
            ["Endpoint / Action", "Method", "URL / Path", "Parameters & Payload"],
            [
                [
                    item.get("name", "").replace("POST ", "").replace("GET ", ""),
                    item.get("request", {}).get("method", "POST"),
                    (item.get("request", {}).get("url", {}).get("raw", "") if isinstance(item.get("request", {}).get("url"), dict) else str(item.get("request", {}).get("url"))).replace("{{api_url}}", "").replace("{{base_url}}", "").replace("{{keycloak_url}}", "/auth"),
                    "JSON Body with request_payload" if item.get("request", {}).get("body") and item.get("request", {}).get("body", {}).get("raw") else "None (Query / Form data)"
                ]
                for item in items
            ]
        )
        doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # ==========================================
    # SECTION 4: QA TEST CASES & GOVERNANCE RULES
    # ==========================================
    add_heading("4. QA Verification Test Cases & Negative Testing Scenarios", level=1)
    
    p = doc.add_paragraph()
    p.add_run(
        "QA automation scripts and manual testers must execute the following test matrix to certify "
        "MDS stability before promoting the develop branch to staging and production."
    )

    t_tc = doc.add_table(rows=1, cols=4)
    style_table(
        t_tc,
        [1.3, 1.8, 2.0, 1.8],
        ["Test Case ID", "Scenario", "Execution Steps", "Expected Result"],
        [
            [
                "TC-WF-01",
                "Full Happy Path Approval Lifecycle",
                "1. Maker creates draft\n2. Maker upserts new entry\n3. Maker submits draft\n4. Checker reviews diff\n5. Checker approves",
                "Status 200 SUCCESS. Version increments. New entry is immediately live in /catalogue/get_list_values."
            ],
            [
                "TC-WF-02",
                "Segregation of Duties Enforcement (Negative)",
                "1. User A creates and submits draft\n2. User A attempts to call /approve_draft using User A's token",
                "Status 403 Forbidden: 'User who created the draft cannot approve it. Independent reviewer required.'"
            ],
            [
                "TC-WF-03",
                "Rejection & Audit Trail",
                "1. Maker submits draft\n2. Checker calls /reject_draft with decision_note\n3. Maker inspects draft status",
                "Status 200 SUCCESS. Draft status transitions to REJECTED. Decision note preserved in audit trail."
            ],
            [
                "TC-WF-04",
                "Draft Lock During Submitted State (Negative)",
                "1. Maker submits draft (status: SUBMITTED)\n2. Maker attempts to call /upsert_draft_values",
                "Status 400 Bad Request: 'Cannot modify draft in SUBMITTED state. Draft is locked.'"
            ],
            [
                "TC-WF-05",
                "Database Trigger Immutability Guard",
                "Execute direct SQL UPDATE on g2p_list_version_values WHERE status = 'PUBLISHED'",
                "Transaction aborted: Database trigger 'trg_g2p_list_versions_guard' blocks update."
            ],
            [
                "TC-GEO-01",
                "Cascading Administrative Dropdown",
                "1. Query regions (level_id=l1)\n2. Query zones with parent_unit_id=ET04\n3. Query woredas with parent_unit_id=ET0401",
                "All child units match parent P-code hierarchy with zero orphan records."
            ]
        ]
    )

    output_path = "/home/user/master-data-standalone/MDS_Complete_API_Testing_and_QA_Demo_Guide.docx"
    doc.save(output_path)
    print(f"Document updated successfully at: {output_path}")

    # Also save a copy to docs/
    doc.save("/home/user/master-data-standalone/docs/MDS_Complete_API_Testing_and_QA_Demo_Guide.docx")
    print("Saved copy to docs/ folder as well.")

if __name__ == '__main__':
    build_docx()
