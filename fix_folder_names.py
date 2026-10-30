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

import urllib.request, json
spec = json.loads(urllib.request.urlopen("https://mds-api-dev.oanstaging.com/openapi.json").read().decode("utf-8"))
folders = {}
for p in sorted(spec["paths"].keys()):
    f = get_folder_name(p, {})
    folders.setdefault(f, []).append(p)

for f, paths in sorted(folders.items()):
    print(f"{f} ({len(paths)} endpoints):")
    for p in paths[:3]:
        print(f"   {p}")
    if len(paths) > 3:
        print(f"   ... and {len(paths)-3} more")
