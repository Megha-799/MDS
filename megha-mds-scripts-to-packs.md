# Moving the MDS catalog data into the ETH-OAN country pack

**For:** Megha
**About:** `scripts/mds/` in `Centre-for-Open-Societal-Systems/openg2p-data` (PR #1)
**Visual guide:** https://oan.closedroominc.qzz.io/master-data-seed/

---

## 1. Why this needs to change

The data you collected is valuable. The 902 MoA crop varieties, 94 breeds, fertilizer details
and livestock reference lists are better than what the pack has today, and we want all of it.

The problem is **how it gets into Master Data**, not the data itself.

| What `scripts/mds/` does today | Why that is a problem |
|---|---|
| Writes straight into `g2p_attributes`, `g2p_list_versions`, `g2p_list_version_values`, `g2p_geo_version_units` | Only the Master Data API and its own loader (`load_geo_pack.py`) are allowed to write these tables |
| `ALTER TABLE … DISABLE TRIGGER trg_g2p_list_versions_guard` | Those triggers are what stop published data from changing underneath the registries |
| Sets `status = 'PUBLISHED'` and `DELETE`s values before re-inserting | Skips drafts, approval, the change log and audit events. Deleted values break old records that point at them |
| Uses numeric ids (`cc.id::text`) as `value_code` | Codes must be permanent, readable and never reused. `"17"` means nothing in a farmer record |
| Seeds geography as lists (`ADMIN_REGIONS_CATALOG`…) | Geography already exists once, as the pack's hierarchy keyed by P-code. A second copy creates a second id space |
| Creates Keycloak users | Not master data. It belongs to the IAM/deployment setup |

**The OpenG2P standard:** data lives as **JSON files in a country pack** (`packs/ETH-OAN/`).
`validate_pack.py` checks them. Master Data's own db-seed job loads them, publishing the first
load and creating **drafts for approval** on every later change. Nothing else writes Master Data.

So the job is: **turn your SQL/Excel data into pack JSON files, then delete `scripts/mds/`.**

---

## 2. Where each of your catalogs goes

ETH-OAN already has 36 agriculture lists. Several of your catalogs **already exist there under a
different name**. You extend those lists rather than create duplicates.

| Your catalog | Goes to | What to do |
|---|---|---|
| `CROP_CATALOG` (150 crops) | **`CROP_COMMODITY`** (121, MoA-aligned) | Add only the crops that are missing. Map each of your crop ids to its `CROP_*` code |
| `SEED_CATALOG` (129 "seeds") | **`CROP_COMMODITY`** | These are crop names (e.g. "Maize (Zea mays L.)"), so they merge with the line above |
| `CROP_CATEGORY_CATALOG` | **`CROP_CATEGORY`** (9) | Map onto the existing `CROPCAT_*` codes. Add a value only if one is truly missing |
| `ECOLOGICAL_ZONE_CATALOG` | **`AGRO_ECOLOGICAL_ZONE`** (5: Bereha, Kolla, Weyna Dega, Dega, Wurch) | Map onto the existing `AEZ_*` codes |
| `CROP_VARIETY_CATALOG` (902) | **`SEED_VARIETY`** (only 8 today) | **Your biggest contribution.** Add all varieties, each linked to its crop (section 4) |
| `LIVESTOCK_CATALOG` (species) | **`LIVESTOCK_TYPE`** (8: cattle, camel, sheep, goat, chicken, donkey, horse, mule) | Map onto `LSTK_*`. Add e.g. bee colony only if registries need it |
| `LIVESTOCK_BREED_CATALOG` (94) | **New list `LIVESTOCK_BREED_NAME`** | The existing `LIVESTOCK_BREED` is a breed *category* (local/improved/hybrid), not breed names. Make a new list with a `species` attribute pointing at `LIVESTOCK_TYPE` |
| `LIVESTOCK_BODY_CONDITION_CATALOG` | **`LIVESTOCK_BODY_CONDITION`** (5: POOR…EXCELLENT) | ⚠ Yours is BCS1–5, ours is word labels. Agree one with us first (section 6) |
| `LIVESTOCK_PRODUCTION_TYPE_CATALOG` | **`LIVESTOCK_PRODUCTION_TYPE`** (13) | Compare value by value and add what is missing |
| `LIVESTOCK_GENDER_CATALOG` | **New list `LIVESTOCK_SEX`** | Animal sex (incl. castrated). Not the person `GENDER` list |
| `LIVESTOCK_LOCATION_TYPE_CATALOG` (High/Mid/Low land) | **`AGRO_ECOLOGICAL_ZONE`**, or a new list | Check with us: it may just be the agro-ecological zone |
| `INPUT_CATALOG` (fertilizers) | **`FERTILIZER_TYPE`** (7: Urea, DAP, NPS, NPSB, NPSZnB, compost, manure) | Map `FERT-UREA` → `FERT_UREA` and so on, and add missing products |
| `ADMIN_REGIONS/ZONES/WOREDAS_CATALOG` | **Nothing. Drop it** | Geography is already in the pack, down to kebele, keyed by P-code |
| `SEED_DEMAND_SUMMARY/TREND/BY_CROP` | **Not master data** | These are statistics (quantity per year). They belong in the crop dashboard / reporting layer |
| `LIVESTOCK_POPULATION_CATALOG` (census) | **Not master data** | Statistics → dashboards |
| `LIVESTOCK_RECORD_STATUS_CATALOG` | **Not master data** | A record's workflow state belongs to the livestock registry itself |
| `LIVESTOCK_REGISTRY_ENTRY_CATALOG` (12 animals) | **Not master data** | These are actual registry records. Demo animals belong in the livestock registry's own seed data |
| `setup_keycloak_orgs_and_users.py` | **Not this repo** | Move to the deployment/IAM setup |

**Rule of thumb:** master data is a list of *allowed values* that rarely changes and that records
point to (crops, breeds, fertilizers). Numbers that change every season (demand, population) and
individual records (animals, users) are **not** master data.

---

## 3. The file format: what a list looks like

Every list is one JSON file. Example (the real `fertilizer_type.json`, shortened):

```json
{
  "attribute_id": "FERTILIZER_TYPE",
  "attribute_code": "FERTILIZER_TYPE",
  "attribute_display": "Fertilizer type",
  "description": "What the list is. Source: <where the data came from, with URL and date read>.",
  "is_hierarchical": false,
  "values": [
    {
      "value_id": "FERT_UREA",
      "value_code": "FERT_UREA",
      "value_display": "Urea",
      "sort_order": 1,
      "display_i18n": {}
    }
  ]
}
```

A list can also carry **extra details per value** (`attributes`), declared in an
`attribute_schema`. A detail that points to another list uses `x-list-ref`, and the validator
checks that every reference exists. This is how `SEED_VARIETY` links to its crop:

```json
"attribute_schema": {
  "type": "object",
  "properties": {
    "crop":            { "type": "string", "x-list-ref": "CROP_COMMODITY", "title": "Crop" },
    "official_name":   { "type": "string", "title": "Official name" },
    "breeding_code":   { "type": "string", "title": "Breeding code" },
    "release_year":    { "type": "integer", "minimum": 1950, "maximum": 2100, "title": "Release year" },
    "research_centre": { "type": "string", "title": "Research centre" }
  },
  "required": ["crop"],
  "additionalProperties": false
}
```

### Code rules

- `value_id` and `value_code` are the same: **UPPER_SNAKE_CASE, with the list's prefix**
  (`CROP_`, `VAR_`, `FERT_`, `LSTK_`, `AEZ_`…), e.g. `VAR_BREAD_WHEAT_DURSA`.
- **Never a database number** (`"17"`) and never a name with spaces.
- A code is **permanent**: you can fix `value_display`, but never rename the code or reuse it for
  something else. Registry records store the code forever.
- Put the Amharic name in `display_i18n` as `{"am": "…"}` whenever you have it, the way
  `crop_commodity.json` does. Amharic is the only language the pack carries today, so ask
  before adding others.
- Write the **source and the date you read it** in `description`. For example, your
  `crop_variety` SQL header points at an archived snapshot, so say that.

---

## 4. Step by step

### Step 0: set up

```bash
git clone https://github.com/<your-fork>/openg2p-data.git
cd openg2p-data
git switch -c feat/eth-oan-moa-catalogs origin/develop
pip install jsonschema
```

Wait until PR #5 (the ETH-OAN pack) is merged, or base your branch on it, because the files
below live in `packs/ETH-OAN/` and `scripts/packs/eth_oan_additions/`.

### Step 1: know where your edits go

`packs/ETH-OAN/` is **generated** by `scripts/packs/build_eth_oan_pack.py`. It is built from the
base `packs/ETH` pack plus OAN's extras in `scripts/packs/eth_oan_additions/`. If you edit
`packs/ETH-OAN/…` by hand, the next rebuild throws your edit away. So:

| You want to… | Put the file in |
|---|---|
| Add **values** to an existing list (crops, varieties, fertilizers, production types) | `scripts/packs/eth_oan_additions/values/domains/agriculture/<list>.json` |
| Add a **new list** (`LIVESTOCK_BREED_NAME`, `LIVESTOCK_SEX`) | `scripts/packs/eth_oan_additions/domains/agriculture/<list>.json` |

A **values** file only lists the new values. The build appends them to the base list:

```json
{
  "description": "MoA released varieties not in the base list. Source: ethioseed.moa.gov.et/crop-varieties-all (archived 2025-12-17).",
  "values": [
    {
      "value_id": "VAR_BREAD_WHEAT_DURSA",
      "value_code": "VAR_BREAD_WHEAT_DURSA",
      "value_display": "Bread Wheat – Dursa",
      "sort_order": 101,
      "display_i18n": {},
      "attributes": {
        "crop": "CROP_BREAD_WHEAT",
        "official_name": "Dursa",
        "release_year": 2020,
        "research_centre": "Kulumsa ARC/EIAR"
      }
    }
  ]
}
```

The build **stops** if one of your values has the same `value_id` as a value already in the base
list. That's on purpose: drop the duplicate.

### Step 2: build a crop mapping first

Your tables use numeric ids (`crop_id = 6` → "Tef"). The pack uses codes (`CROP_TEFF`). Make a
small CSV once and reuse it for crops, varieties and seeds:

```csv
your_crop_id,your_crop_name,pack_code
1,Maize,CROP_MAIZE
2,Bread Wheat,CROP_BREAD_WHEAT
3,Durum Wheat,CROP_DURUM_WHEAT
6,Tef,CROP_TEFF
...
```

Look each crop up in `packs/ETH-OAN/domains/agriculture/crop_commodity.json`. If a crop is
genuinely missing, give it a new `CROP_*` code. It then goes into your `crop_commodity.json`
values addition, with its `category` (a `CROPCAT_*` code) and `scientific_name`, which the
base schema requires or allows.

### Step 3: generate the JSON with a script (don't type 902 rows)

Write a **one-off converter**. Keep it next to the other pack tools as
`scripts/packs/convert_moa_catalogs.py`, so the conversion can be repeated and reviewed.
Read from your Excel file or from a CSV export of your SQL tables. Never read from the
Master Data database. Sketch:

```python
#!/usr/bin/env python3
"""Turn the MoA crop-variety export into SEED_VARIETY values for ETH-OAN."""
import csv, json, re

def code(*parts):
    s = "_".join(parts).upper()
    s = re.sub(r"\(.*?\)", "", s)        # drop pedigree in brackets
    s = re.sub(r"[^A-Z0-9]+", "_", s)    # spaces, dashes, Amharic → _
    return s.strip("_")

crop = {r["your_crop_id"]: r["pack_code"] for r in csv.DictReader(open("crop_map.csv", encoding="utf-8"))}

values, seen = [], set()
for i, r in enumerate(csv.DictReader(open("crop_variety.csv", encoding="utf-8")), start=1):
    crop_code = crop[r["crop_id"]]                       # KeyError = fix crop_map.csv
    name = r["common_name"].split("-", 1)[-1].strip()
    vid = code("VAR", crop_code.removeprefix("CROP_"), name)
    if vid in seen:
        print("duplicate, check by hand:", vid, r["id"]); continue
    seen.add(vid)
    attrs = {"crop": crop_code, "official_name": name}
    if r["release_year"]:
        attrs["release_year"] = int(r["release_year"])
    if r["maintainer"]:
        attrs["research_centre"] = r["maintainer"].strip(" /")
    values.append({"value_id": vid, "value_code": vid, "value_display": f'{r["crop_name"]} – {name}',
                   "sort_order": 100 + i, "display_i18n": {}, "attributes": attrs})

out = "eth_oan_additions/values/domains/agriculture/seed_variety.json"
with open(out, "w", encoding="utf-8", newline="\n") as fh:
    json.dump({"description": "MoA released varieties. Source: ethioseed.moa.gov.et/crop-varieties-all "
               "(web.archive.org snapshot 2025-12-17).", "values": values}, fh, ensure_ascii=False, indent=2)
    fh.write("\n")
print(len(values), "varieties written to", out)
```

Then **read the output by eye**. Names like `Tef - (Boni (ቦኒ)` and `Durem Wheat` (a typo) in
the source need cleaning. Clean them in the converter, so the fix is repeatable.

**Fields the schema doesn't have** (`source: Domestic`, `details_url`, `known_for`,
`isolation_distance`, a fertilizer's `license_number` and `manufacturer`) can't simply be added.
The base lists use `"additionalProperties": false`, and an addition can add values but not change
a base list's schema. Leave them out for the first PR and list them in the PR description. We'll
decide together whether to extend the schema (section 6).

### Step 4: rebuild the pack and validate

```bash
cd scripts/packs
python build_eth_oan_pack.py --source <geo_level_values.json> \
    --base ../../packs/ETH --out ../../packs/ETH-OAN --version <today, YYYY-MM-DD>
PYTHONUTF8=1 python validate_pack.py ../../packs/ETH-OAN
```

- `geo_level_values.json` (the location source) is not in the repo. Ask Asmit for it.
- `validate_pack.py` must say **`[ETH-OAN] ok (0 errors, …)`**. It checks that every
  `x-list-ref` points to a real code (every variety's `crop`, every breed's `species`), that
  attributes match the schema, and that codes are unique.
- `[ETH]` and `[XKM]` currently fail on `develop` for an unrelated reason (relationship-to-head
  roles). Ignore those two and fix only what says `[ETH-OAN]`.

Also run the same checks Jenkins runs:

```bash
ruff check scripts --select E9,F63,F7,F82
python scripts/ci/check_data_files.py
```

### Step 5: check the diff

```bash
git diff --stat
```

You should see only:

- `scripts/packs/eth_oan_additions/…` (your new files)
- `scripts/packs/convert_moa_catalogs.py` and your mapping CSV
- the matching lists in `packs/ETH-OAN/domains/agriculture/` (regenerated)
- `packs/ETH-OAN/manifest.json` (version date)

If `values.json`, `boundaries/` or `samples/` changed, stop and ask: something in the build
went wrong.

### Step 6: remove the old path

In the **same PR**:

- delete `scripts/mds/` completely: the SQL, the import scripts, `seed_all_mds.py` and the
  Keycloak script
- keep the source spreadsheet only if it's needed to re-run your converter, and move it next to
  the converter (e.g. `scripts/packs/sources/crop_catalog.xlsx`)

### Step 7: open the PR

Target `Centre-for-Open-Societal-Systems/openg2p-data`, branch `develop`. In the description:

1. Which lists you extended and by how many values (e.g. "SEED_VARIETY +894").
2. The source and date for each.
3. The fields you left out because the schema doesn't have them (step 3).
4. The open questions from section 6.
5. The `validate_pack.py` output for ETH-OAN.

After merge, Jenkins builds the seed image. When it's deployed, Master Data creates **drafts** for
the changed lists, and someone approves them in Master Data. That's the normal path, and nobody
needs to touch the database.

---

## 5. Quick do / don't

**Do**
- Change data only in JSON files, through a PR.
- Extend existing lists before creating new ones.
- Use readable, permanent codes with the list prefix.
- Link related lists with `x-list-ref` (variety → crop, breed → species).
- Record the source and date in `description`.
- Run `validate_pack.py` before every push.

**Don't**
- Write SQL against Master Data tables, or disable triggers.
- Use numeric database ids as codes.
- Delete or rename existing codes.
- Put statistics, registry records or users into master data.
- Seed geography as lists.
- Edit generated files in `packs/ETH-OAN/` by hand.

---

## 6. Questions to settle before you start (talk to Asmit)

1. **Body condition:** your BCS1–BCS5 (national standard) or our POOR…EXCELLENT? If the national
   standard is BCS, we should switch to it and keep the word as `value_display`. That's a
   decision about existing codes, so it needs agreement first.
2. **Extra attributes:** do registries need `isolation_distance`, `num_field_inspection_needed`,
   `known_for`, or fertilizer `license_number`/`manufacturer`? If so, we extend the schema. That
   means either a small change to `build_eth_oan_pack.py`, so an addition can extend a base
   list's schema, or a change to the ETH base list.
3. **Livestock location type:** is "High/Mid/Low land" the same thing as the agro-ecological zone?
4. **Bee colonies:** `LIVESTOCK_TYPE` has no bee/beehive entry. Do the registries need one?
5. **Seed demand and livestock population:** these should feed the crop and livestock
   dashboards. Who owns that work?
