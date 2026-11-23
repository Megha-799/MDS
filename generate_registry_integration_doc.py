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

def add_code_block(doc, code_text):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, "F1F5F9")
    set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
    cell.width = Inches(6.9)
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(code_text.strip())
    r.font.name = 'Courier New'
    r.font.size = Pt(8.5)
    r.font.color.rgb = RGBColor(30, 41, 59)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def build_document():
    doc = docx.Document()

    for s in doc.sections:
        s.top_margin = Inches(0.8)
        s.bottom_margin = Inches(0.8)
        s.left_margin = Inches(0.8)
        s.right_margin = Inches(0.8)

    PRIMARY = RGBColor(24, 76, 120)     # Navy Blue
    SECONDARY = RGBColor(41, 128, 185)  # Soft Blue
    DARK_TEXT = RGBColor(44, 62, 80)    # Charcoal
    MUTED = RGBColor(100, 116, 139)

    def add_title(text):
        p = doc.add_paragraph()
        r = p.add_run(text)
        r.font.name = 'Calibri'
        r.font.size = Pt(22)
        r.font.bold = True
        r.font.color.rgb = PRIMARY
        p.paragraph_format.space_after = Pt(2)
        return p

    def add_subtitle(text):
        p = doc.add_paragraph()
        r = p.add_run(text)
        r.font.name = 'Calibri'
        r.font.size = Pt(12)
        r.font.italic = True
        r.font.color.rgb = SECONDARY
        p.paragraph_format.space_after = Pt(12)
        return p

    def add_meta(label, val):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(2)
        r1 = p.add_run(f"{label}: ")
        r1.font.bold = True
        r1.font.name = 'Calibri'
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = PRIMARY
        r2 = p.add_run(val)
        r2.font.name = 'Calibri'
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = DARK_TEXT

    def add_heading(text, level=1):
        h = doc.add_paragraph()
        r = h.add_run(text)
        r.font.name = 'Calibri'
        r.bold = True
        if level == 1:
            r.font.size = Pt(16)
            r.font.color.rgb = PRIMARY
            h.paragraph_format.space_before = Pt(14)
            h.paragraph_format.space_after = Pt(4)
        elif level == 2:
            r.font.size = Pt(12.5)
            r.font.color.rgb = SECONDARY
            h.paragraph_format.space_before = Pt(10)
            h.paragraph_format.space_after = Pt(3)
        elif level == 3:
            r.font.size = Pt(10.5)
            r.font.color.rgb = DARK_TEXT
            h.paragraph_format.space_before = Pt(6)
            h.paragraph_format.space_after = Pt(2)
        return h

    def add_para(text):
        p = doc.add_paragraph()
        r = p.add_run(text)
        r.font.name = 'Calibri'
        r.font.size = Pt(10)
        r.font.color.rgb = DARK_TEXT
        p.paragraph_format.space_after = Pt(4)
        return p

    def add_bullet(text, bold_prefix=""):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(2)
        if bold_prefix:
            r1 = p.add_run(bold_prefix)
            r1.font.name = 'Calibri'
            r1.font.bold = True
            r1.font.size = Pt(10)
            r1.font.color.rgb = PRIMARY
        r2 = p.add_run(text)
        r2.font.name = 'Calibri'
        r2.font.size = Pt(10)
        r2.font.color.rgb = DARK_TEXT

    # Header / Meta
    add_title("Master Data Service (MDS) — Registry Integration & API Guide")
    add_subtitle("Standard Specifications for Connecting Farmer Registry (FR), Crop Registry (CR), and Livestock Enterprise (LE)")

    add_meta("Author", "Megha Gireesh — Master Data Service (MDS) Engineering Lead")
    add_meta("Target Audience", "Registry Backend Developers (FR, CR, LE) & DevOps Engineers")
    add_meta("Platform Version", "OpenG2P Master Data Service (API & UI: 0.0.0-develop.121)")
    add_meta("Date", "November 2026")

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # 1. Executive Summary
    add_heading("1. Executive Summary & Purpose", level=1)
    add_para(
        "The Master Data Service (MDS) serves as the foundational Digital Public Infrastructure (DPI) "
        "for the Ethiopia Agri-Stack ecosystem. Consuming registries—including the Farmer Registry (FR), "
        "Crop Registry (CR), and Livestock Enterprise (LE)—must dynamically consume canonical reference "
        "data and geographic boundaries directly from MDS."
    )
    add_para(
        "By binding external registry dropdowns and validations to MDS canonical codes (CSA P-codes and "
        "Ministry of Agriculture commodity codes), the Agri-Stack ensures 100% interoperability, eliminates "
        "free-text spelling discrepancies, and enables seamless data exchange across national platforms."
    )

    # 2. Connection Parameters
    add_heading("2. Connection Parameters & Authentication", level=1)
    add_para(
        "All API interactions with MDS are secured through Keycloak OAuth2 Bearer Tokens. Consuming backend "
        "services should obtain a service account token via Machine-to-Machine (M2M) client credentials or "
        "forward authenticated staff portal user Bearer tokens."
    )

    t_params = doc.add_table(rows=1, cols=2)
    style_table(
        t_params,
        [2.3, 4.6],
        ["Connection Parameter", "Configuration Value / URL"],
        [
            ["Internal Kubernetes DNS", "http://master-data-api:8000 (cluster local service name)"],
            ["External / Ingress URL", "https://master-data.development.oanstaging.com"],
            ["Keycloak Token Endpoint", "https://keycloak.development.oanstaging.com/realms/staff/protocol/openid-connect/token"],
            ["Keycloak Realm", "staff"],
            ["Keycloak Client ID", "farmer-registry-staff-portal (or registered M2M service account client)"],
            ["Token Grant Type", "client_credentials (for background server calls) or password / authorization_code"],
            ["Required Header 1", "Content-Type: application/json"],
            ["Required Header 2", "Authorization: Bearer <ACCESS_TOKEN>"],
            ["Token Lifetime & Caching", "Access token is valid for 3,600s (1 hour). Registries must cache and reuse token."]
        ]
    )

    # 3. OpenG2P Envelope Structure
    add_heading("3. Standard OpenG2P Request & Response Envelope", level=1)
    add_para(
        "All POST API calls to Master Data Service adhere to the OpenG2P transactional envelope structure, "
        "consisting of a mandatory 'request_header' and 'request_body'."
    )
    add_code_block(doc, """
{
  "request_header": {
    "sender_app_mnemonic": "farmer-registry-backend",
    "sender_app_url": "https://farmer.development.oanstaging.com",
    "request_id": "c1f7a6b0-4e2a-11ec-81d3-0242ac130003",
    "request_timestamp": "2026-11-16T10:00:00Z"
  },
  "request_body": {
    "pagination_request": {
      "page_size": 100,
      "page_number": 1
    },
    "request_payload": { ... }
  }
}
""")

    # 4. Administrative Geography API
    add_heading("4. Administrative Geography API (Cascading Location Dropdowns)", level=1)
    add_para(
        "MDS hosts the authoritative national administrative hierarchy of Ethiopia, comprising 4 levels: "
        "Region (14), Zone (125), Woreda (1,359), and Kebele (19,392). All units are indexed by official CSA P-codes."
    )

    add_heading("4.1 Fetching Cascading Units (POST /catalogue/get_geo_units)", level=2)
    add_para("Used by registry registration forms to populate Region, Zone, Woreda, and Kebele cascading dropdowns.")
    add_bullet("level_id: 'region', 'zone', 'woreda', or 'kebele'", "• Level Indicator: ")
    add_bullet("parent_unit_id: P-code of parent (e.g. 'ET04' to fetch zones of Oromia; omit for root Regions)", "• Parent Filter: ")

    add_para("Sample Request Payload:")
    add_code_block(doc, """
POST /catalogue/get_geo_units
Host: master-data.development.oanstaging.com
Content-Type: application/json
Authorization: Bearer <TOKEN>

{
  "request_header": {
    "sender_app_mnemonic": "farmer-registry-backend",
    "sender_app_url": "https://farmer.development.oanstaging.com",
    "request_id": "req-geo-zones",
    "request_timestamp": "2026-11-16T10:00:00Z"
  },
  "request_body": {
    "request_payload": {
      "level_id": "zone",
      "parent_unit_id": "ET04"
    }
  }
}
""")

    add_heading("4.2 Resolving a Single Location Code (POST /catalogue/get_geo_unit)", level=2)
    add_para("Used when displaying an existing farmer's details or validating a submitted woreda/kebele P-code.")
    add_code_block(doc, """
POST /catalogue/get_geo_unit
{
  "request_header": {
    "sender_app_mnemonic": "farmer-registry-backend",
    "request_id": "req-geo-single",
    "request_timestamp": "2026-11-16T10:00:00Z"
  },
  "request_body": {
    "request_payload": {
      "unit_id": "ET040103"
    }
  }
}
""")

    # 5. Reference Catalogs API
    add_heading("5. Reference Catalogs API (Crops, Seeds, Inputs, Livestock)", level=1)
    add_para(
        "MDS provides canonical lists and metadata for agricultural commodities, varieties, inputs, "
        "and livestock breeds."
    )

    add_heading("5.1 Fetching Catalog Values (POST /catalogue/get_list_values)", level=2)
    add_para("Used to dynamically populate multi-select and dropdown inputs on registry forms.")
    add_code_block(doc, """
POST /catalogue/get_list_values
Content-Type: application/json
Authorization: Bearer <TOKEN>

{
  "request_header": {
    "sender_app_mnemonic": "crop-registry-backend",
    "request_id": "req-crops-list",
    "request_timestamp": "2026-11-16T10:00:00Z"
  },
  "request_body": {
    "request_payload": {
      "list_code": "CROP_CATALOG"
    }
  }
}
""")

    add_para(
        "For hierarchical catalogs (e.g., Crop Varieties under a specific Crop), pass 'parent_code' "
        "to filter varieties belonging solely to that crop."
    )

    # 6. Canonical Catalog Codes Reference Table
    add_heading("6. Canonical Catalog Codes Reference", level=1)
    add_para(
        "External registries must request and validate against these exact canonical catalog codes:"
    )

    t_codes = doc.add_table(rows=1, cols=4)
    style_table(
        t_codes,
        [1.8, 1.4, 2.2, 1.5],
        ["Catalog Code", "Owning Ministry", "Description & Content", "Consuming Registries"],
        [
            ["CROP_CATALOG", "MoA (Ethiopia)", "150 Canonical crops across 7 production categories", "FR, Crop Registry"],
            ["CROP_VARIETY_CATALOG", "MoA (Ethio-Seed)", "902 Registered crop varieties with ecological metadata", "FR, Crop Registry"],
            ["SEED_CATALOG", "MoA / Seed Enterprise", "130 Seed records (Breeder, Basic, Certified 1 & 2)", "FR, Input Registry"],
            ["INPUT_CATALOG", "MoA Plant Health", "11 Certified fertilizer blends (NPSB, Urea, DAP, bio)", "FR, Input Registry"],
            ["LIVESTOCK_CATALOG", "LDI (Livestock Inst)", "6 Indigenous & exotic livestock species", "FR, Livestock Ent."],
            ["LIVESTOCK_BREEDS_CATALOG", "LDI (Livestock Inst)", "94 Standard livestock breeds (Boran, Horro, etc.)", "FR, Livestock Ent."],
            ["LAND_PREPARATION_METHOD_CATALOG", "MoA Natural Resources", "Standard soil & tillage preparation practices", "FR, Land Module"]
        ]
    )

    # 7. Database Best Practices
    add_heading("7. Registry Storage & Architecture Best Practices", level=1)
    add_bullet(
        "Always store canonical P-codes (e.g. 'ET040103') and catalog codes (e.g. '101' or 'FERT-NPSB') in registry relational tables. NEVER store English display strings, which break language localization and reporting.",
        "1. Store Codes, Not Text: "
    )
    add_bullet(
        "National catalogs and geography are updated only on formal releases (quarterly/annually). Registries must cache API responses in Redis or local memory for 12 to 24 hours to guarantee high UI performance.",
        "2. Implement 24-Hour Caching: "
    )
    add_bullet(
        "MDS returns multilingual names (e.g. 'en', 'am' for Amharic, 'om' for Afaan Oromoo). External registry frontends should bind to the active user language while retaining the underlying code.",
        "3. Localized Display: "
    )

    # 8. Available Artifacts
    add_heading("8. Available Developer Resources & Postman Collections", level=1)
    add_para("The Master Data Service team has prepared complete test artifacts ready for your team:")
    add_bullet("MDS_Complete_Develop_API_Collection.postman_collection.json: Pre-configured Postman collection covering all endpoints.", "• Postman Collection: ")
    add_bullet("MDS_Dev_Environment.postman_environment.json: Pre-populated environment variables with endpoints and credentials.", "• Postman Environment: ")
    add_bullet("Sample Python, Node.js, and Java SDK snippets available upon request.", "• SDK Samples: ")

    doc.save("MDS_Registry_Integration_and_API_Specification.docx")
    print("Successfully built MDS_Registry_Integration_and_API_Specification.docx!")

if __name__ == '__main__':
    build_document()
