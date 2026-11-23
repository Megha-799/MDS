#!/usr/bin/env python3
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
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

def create_doc():
    doc = docx.Document()

    for s in doc.sections:
        s.top_margin = Inches(0.8)
        s.bottom_margin = Inches(0.8)
        s.left_margin = Inches(0.8)
        s.right_margin = Inches(0.8)

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

    # Title
    title = doc.add_paragraph()
    r = title.add_run("How to Connect External Registries to Master Data Service (MDS)")
    r.font.name = 'Calibri'
    r.font.size = Pt(22)
    r.font.bold = True
    r.font.color.rgb = PRIMARY
    title.paragraph_format.space_after = Pt(2)

    subtitle = doc.add_paragraph()
    r = subtitle.add_run("Step-by-Step Onboarding, Setup Guide & Developer Handover Checklist")
    r.font.name = 'Calibri'
    r.font.size = Pt(13)
    r.font.color.rgb = SECONDARY
    subtitle.paragraph_format.space_after = Pt(12)

    # 1. Overview
    add_heading("1. Overview in Simple Words", level=1)
    p = doc.add_paragraph()
    p.add_run(
        "Master Data Service (MDS) is the central dictionary for the Ethiopian agricultural ecosystem. "
        "It stores canonical codes for Locations (Regions, Zones, Woredas), Crops, Varieties, Livestock, "
        "and Agricultural Inputs. Consuming registries (Farmer Registry, Crop Sown Registry, Livestock Registry) "
        "must never hardcode dropdown lists; instead, they query MDS to ensure 100% data harmonization across ministries."
    )

    # 2. Cheat Sheet
    add_heading("2. What Details YOU Need to Share with Them (Handover Card)", level=1)
    t_card = doc.add_table(rows=1, cols=2)
    style_table(
        t_card,
        [2.2, 4.7],
        ["Connection Parameter", "Value to Share with External Developer Team"],
        [
            ["Backend API Base URL", "https://master-data.development.oanstaging.com (Local: http://localhost:8044)"],
            ["Keycloak IAM Token URL", "https://keycloak.development.oanstaging.com/realms/staff/protocol/openid-connect/token"],
            ["Keycloak Realm", "staff"],
            ["Keycloak Client ID", "admin-cli (or registered client: farmer-registry-staff-portal)"],
            ["Grant Type", "password (for user workflows) or client_credentials (for background server daemons)"],
            ["HTTP Protocol & Format", "POST with Content-Type: application/json and Authorization: Bearer <TOKEN>"],
            ["Payload Format", "Standard OpenG2P Envelope containing request_header and request_body"],
            ["Primary Geolocation API", "POST /catalogue/get_geo_units (with level_id: l1, l2, l3)"],
            ["Single Location Lookup", "POST /catalogue/get_geo_unit (with unit_id, e.g. ET040103)"],
            ["Primary Catalog Values API", "POST /catalogue/get_list_values (with list_code and optional parent_code)"],
            ["Single Code Validation API", "POST /catalogue/get_list_value (with list_code and value_code)"]
        ]
    )

    # 3. Setup Steps
    add_heading("3. What the External Registry Needs to Setup (Step-by-Step)", level=1)
    
    add_heading("Step 1: Set Environment Variables in Registry Backend", level=2)
    p = doc.add_paragraph()
    p.add_run(
        "MDS_API_BASE_URL=https://master-data.development.oanstaging.com\n"
        "KEYCLOAK_TOKEN_URL=https://keycloak.development.oanstaging.com/realms/staff/protocol/openid-connect/token\n"
        "KEYCLOAK_REALM=staff\n"
        "KEYCLOAK_CLIENT_ID=admin-cli\n"
        "SENDER_APP_MNEMONIC=farmer-registry-backend"
    )

    add_heading("Step 2: Obtain Bearer Token from Keycloak", level=2)
    p = doc.add_paragraph()
    p.add_run(
        "Their backend service calls Keycloak using HTTP POST (x-www-form-urlencoded) passing client_id, "
        "username, password, and grant_type=password to acquire an access_token. The token has a 1-hour lifetime."
    )

    add_heading("Step 3: Implement OpenG2P Request Envelope", level=2)
    p = doc.add_paragraph()
    p.add_run(
        "MDS requires all POST payloads to be enclosed inside an OpenG2P envelope containing a request_header "
        "(with sender_app_mnemonic, request_id, timestamp) and request_body (with pagination_request and request_payload)."
    )

    add_heading("Step 4: Implement Redis / Local Memory Caching", level=2)
    p = doc.add_paragraph()
    p.add_run(
        "To prevent hammering MDS on every user keystroke, external registries must cache catalog responses:\n"
        "• Administrative Geography (Regions, Zones, Woredas): Cache for 24 hours.\n"
        "• Crops, Varieties, and Fertilizers: Cache for 12 to 24 hours.\n"
        "• Single code validation during submission: Check local cache first; if cache miss, call POST /catalogue/get_list_value."
    )

    # 4. Top 10 FAQ
    add_heading("4. What Will the Other Registry Team Ask You? (Top 10 FAQ & Answers)", level=1)
    
    t_faq = doc.add_table(rows=1, cols=2)
    style_table(
        t_faq,
        [2.6, 4.3],
        ["Questions They Will Ask You", "Ready-Made Answers to Give Them"],
        [
            [
                "1. Why do we get 401 Unauthorized or 404 Not Found when calling /public/...?",
                "Our development server enforces strict government privacy (visibility: private). You must use the authenticated Core OpenG2P endpoints (POST /catalogue/...) with your Keycloak Bearer token."
            ],
            [
                "2. How long does the Keycloak token last? Do we need a new token for each request?",
                "Access tokens are valid for 1 hour (3,600 seconds). Cache the token in memory and only refresh it when it expires."
            ],
            [
                "3. What format should we store in our registry database?",
                "Always store canonical codes, NOT English text: store P-codes (ET04, ET040103) for locations, value_code (1) for crops, and input_code (FERT-NPSB) for fertilizers. This guarantees 100% interoperability across ministries."
            ],
            [
                "4. How do we do cascading dropdowns (Region -> Zone -> Woreda)?",
                "Pass parent_unit_id: when Region ET04 is chosen, call /catalogue/get_geo_units with level_id: 'l2', parent_unit_id: 'ET04' to get its Zones. For Woredas, pass parent_unit_id: 'ET0401'."
            ],
            [
                "5. How do we resolve a single Woreda P-code like ET040103?",
                "Call POST /catalogue/get_geo_unit with {'unit_id': 'ET040103'}. It returns Dedo Woreda and its complete ancestry path (Jimma Zone and Oromia Region) in a single response."
            ],
            [
                "6. What happens if MDS is temporarily offline?",
                "Because your registry caches location and catalog data in Redis for 24 hours, your portal continues serving dropdowns and enrolling farmers without interruption."
            ],
            [
                "7. How do we receive updates when new crops or fertilizers are added?",
                "MDS publishes updates using Maker-Checker governance. When your 12-24 hour cache expires, your registry automatically pulls the latest published active baseline."
            ],
            [
                "8. How does pagination work for large catalogs?",
                "Include pagination_request in request_body with current_page and page_size. MDS returns total_records, total_pages, and the current records list."
            ],
            [
                "9. Can we search items by text?",
                "Yes! Pass 'search': 'Wheat' inside request_payload to search across names, scientific labels, and descriptions."
            ],
            [
                "10. Do you have ready Postman collections we can test with?",
                "Yes! We provide MDS_QA_Testing_Collection.postman_collection.json, MDS_Dev_Environment.postman_environment.json, and the MDS_Complete_API_Testing_and_QA_Demo_Guide.docx."
            ]
        ]
    )

    doc.save("/home/user/master-data-standalone/Registry_Onboarding_and_Integration_Setup_Guide.docx")
    doc.save("/home/user/master-data-standalone/docs/Registry_Onboarding_and_Integration_Setup_Guide.docx")
    print("Created Registry_Onboarding_and_Integration_Setup_Guide.docx successfully!")

if __name__ == '__main__':
    create_doc()
