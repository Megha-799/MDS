# Feedback on PR #6: MoA catalogs into ETH-OAN

**To:** Megha
**PR:** Centre-for-Open-Societal-Systems/openg2p-data#6 (merged into `develop` at `4f376d2`)
**Checked:** 2026-10-27, on merged `develop`

---

## First: thank you, the direction is right

You did the hard part. The raw-SQL path is gone, and the data now goes through
`eth_oan_additions/` plus a repeatable converter. That's the standard way.

**Done well:**
- `scripts/mds/` is fully removed: the trigger-disabling SQL, the geography-as-lists data,
  the statistics and the Keycloak script.
- Raw sources are kept in `scripts/packs/sources/` and the converter in
  `scripts/packs/convert_moa_catalogs.py`, so the conversion can be re-run.
- The generated `packs/ETH-OAN/` exactly equals the base pack plus your additions. Nothing was
  hand-edited.
- All codes are valid UPPER_SNAKE_CASE and there are no duplicate IDs.
- Every `crop` reference resolves in `CROP_COMMODITY`, and every `species` in `LIVESTOCK_TYPE`.
- Good new content: 4 crops, 3 fertilizers, `SEED_VARIETY` from 8 to 905,
  `LIVESTOCK_BREED_NAME` (93 breeds, each linked to its species) and `LIVESTOCK_SEX`.

---

## 1. About `validate_pack.py` failing

There are two different results, and only one of them concerns your PR.

### 1a. Run on all packs (as Jenkins does): fails, but **not because of PR #6**

```
cd scripts/packs
PYTHONUTF8=1 python validate_pack.py ../../packs/ETH ../../packs/ETH-OAN ../../packs/XKM
```

```
[ETH]     FAIL (7 errors, 1 warnings)   ← RELATIONSHIP_TO_HEAD has no 'head_of_household' value;
                                           6 sample people use 'SELF', which ETH's list lacks
[ETH-OAN] ok   (0 errors, 1 warnings)   ← our pack, with your data: passes
[XKM]     FAIL (1 errors, 0 warnings)   ← same missing 'head_of_household' role
exit 1
```

`ETH` and `XKM` are OpenG2P's upstream packs. Both failed the same way before your PR, and your
PR doesn't touch them.

- **Please don't edit `packs/ETH` or `packs/XKM` to fix this.** They're upstream data. The fix
  belongs upstream, or Jenkins should gate only on the packs we deploy (ETH-OAN). We're raising
  that with DevOps.
- It does mean **Jenkins "Validate packs" is red for every build**, so a red build is not by
  itself a sign your change is wrong. Always check the `[ETH-OAN]` line.

### 1b. Run with `--strict` on ETH-OAN: fails on one warning

```
[ETH-OAN] WARN  1/110 parents are not cleanly partitioned by their children (1%): ET children cover 19%
[ETH-OAN] FAIL  (0 errors, 1 warnings)
```

This is expected and **not yours**. ETH-OAN only carries boundaries for units that did not
change (7 of 14 regions), so the country polygon isn't fully covered by its regions. The
manifest declares this in `boundary_coverage`. Don't use `--strict` for ETH-OAN.

**What to run before each push:**

```
cd scripts/packs
PYTHONUTF8=1 python validate_pack.py ../../packs/ETH-OAN     # must say: [ETH-OAN] ok (0 errors, …)
cd ../.. && python scripts/ci/check_data_files.py            # must say: 0 error(s)
ruff check scripts --select E9,F63,F7,F82                    # must say: All checks passed!
```

> `validate_pack.py` checks structure (codes, references, schema), not whether names make
> sense. Everything in section 2 passes the validator and is still wrong.

---

## 2. Must fix: `SEED_VARIETY` data quality

The problems below come from the **source**: the archived ethioseed snapshot already has "…"
on 300 lines and blank names. Your converter didn't cause them, but it passed them through.

**Why it's urgent:** codes are permanent once a farmer record uses them. Nothing has been
seeded yet (`geoSeed.enabled: false` in every environment), so **right now we can still change
any of these codes freely**. After the first deploy, each fix means retiring codes and
migrating records.

### 2.1 Names cut off with "…" (204 varieties)

e.g. `Tef – Bishoftu (ቢሾፍቱ ) …`, `Malt Barley – Suba (Pedigree: …`,
`Food Barley – Jalqabne (BARC/JED/003/14) …`.

The **codes** were built from the cut-off names too (`VAR_BREAD_WHEAT_DEKA_ETBW`,
`VAR_MALT_BARLEY_SUBA_PEDIGREE`). This also causes most of the 154 names with unbalanced
brackets.
**Fix:** each source row has a `details_url`
(`https://ethioseed.moa.gov.et/seed-variety-details/<id>/`, or its web.archive.org copy).
Fetch the full name from there, or get a complete export from MoA. Then regenerate the names
**and** codes.

### 2.2 Varieties with no name at all (38)

They display as just `Common/Haricot/ bean –` (33×) or `Rapeseed –` (5×), so a user can't tell
them apart. Their codes fall back to the source row id:

```
VAR_COMMON_BEAN_35 36 37 38 39 132 133 134 136 137 138 139 159 222 223 224 225 226 228 229
                 281 282 353 354 355 418 425 426 665 666 667 668 761
VAR_RAPESEED_291 292 681 682 683
```

**Fix:** recover the names from `details_url`. If a variety has no name even there,
**leave it out** of the list and mention it in the PR.

### 2.3 Same variety listed twice under two codes (8 pairs)

```
VAR_MAIZE_BH546              / VAR_MAIZE_BH546_321
VAR_MAIZE_BH520_W1           / VAR_MAIZE_BH520_W1_107
VAR_MALT_BARLEY_HB1963       / VAR_MALT_BARLEY_HB1963_832
VAR_MALT_BARLEY_HB1964       / VAR_MALT_BARLEY_HB1964_833
VAR_BREAD_WHEAT_OGOLCHO      / VAR_BREAD_WHEAT_OGOLCHO_527
VAR_SESAME_SIFAN             / VAR_SESAME_SIFAN_908
VAR_BREAD_WHEAT_DEKA_ETBW    / VAR_BREAD_WHEAT_DEKA_ETBW_198      ← names truncated: check first
VAR_COMMON_BEAN_AWASH        / VAR_COMMON_BEAN_AWASH_763          ← released 2017 vs 1990: probably two different varieties
```

**Fix:**
- **True duplicates** (the first six, same name and release year): keep **one** code, without
  the numeric suffix, and merge any details (e.g. keep the `breeding_code` that only one of
  them has).
- **The last two:** recover the full names (2.1) first. They're likely different varieties
  whose names were cut to the same prefix. They then get proper distinct codes.

### 2.4 No source-row numbers in codes

A suffix like `_321` or `_908` is a row number from the scraped source. It means nothing and
changes if the source is re-scraped. Once 2.1–2.3 are done, no code should need one. If two
real varieties still collide, tell them apart with something meaningful (release year, breeding
code), e.g. `VAR_COMMON_BEAN_AWASH_1` / `VAR_COMMON_BEAN_AWASH_MELKA`. Pedigree numbers that
are part of the real name (`VAR_DURUM_WHEAT_ETCROSS_21`) are fine.

### 2.5 Amharic inside the English name (46)

e.g. `Tef – Bishoftu (ቢሾፍቱ )`, `Field pea – Hasset (ሀሴት)`.
**Fix:** put the Amharic in `display_i18n` instead, `{"am": "ቢሾፍቱ"}`, and keep
`value_display` English. Your converter can split on the Ethiopic script range
(`[ሀ-፿]`).

### 2.6 Add a guard to the converter so this can't come back

At the end of `convert_moa_catalogs.py`, fail loudly before writing anything:

```python
import re, collections, sys

ALLOWED_NUMERIC_CODES = set()  # e.g. {"VAR_TEFF_DZ_CR_387"} when the digits are the real pedigree

def check_varieties(values):
    errs = []
    for v in values:
        name = (v.get("attributes") or {}).get("official_name", "").strip()
        if not name:
            errs.append(f"{v['value_id']}: no variety name")
        if "…" in v["value_display"] or "..." in v["value_display"]:
            errs.append(f"{v['value_id']}: truncated name {v['value_display']!r}")
        if v["value_display"].count("(") != v["value_display"].count(")"):
            errs.append(f"{v['value_id']}: unbalanced brackets {v['value_display']!r}")
        if re.search(r"[ሀ-፿]", v["value_display"]):
            errs.append(f"{v['value_id']}: Amharic in value_display; move it to display_i18n.am")
        # A real pedigree can end in 3 digits too: allow those by name.
        if re.search(r"_\d{3}$", v["value_id"]) and v["value_id"] not in ALLOWED_NUMERIC_CODES:
            errs.append(f"{v['value_id']}: ends in a 3-digit number; a source row id? (allowlist it if it is part of the real name)")
    seen = collections.Counter(((v.get("attributes") or {}).get("crop"), v["value_display"].strip().lower()) for v in values)
    errs += [f"duplicate name within crop: {k}" for k, n in seen.items() if n > 1]
    if errs:
        sys.exit("\n".join(errs))
```

---

## 3. Smaller points (nice to have)

1. **Breed names repeat across species:** "Afar", "Abergele", "Arsi", "Horro", "Begayit" and
   "Ille" each exist for 2–3 species. That's correct data, and fine when the form filters breeds
   by species, but ambiguous in an unfiltered list. Consider adding the species to the
   display, e.g. `Afar (sheep)`, or confirm with the livestock registry that it always filters.
2. **`LIVESTOCK_SEX`: "Female neuter"** (`SEX_FEMALE_NEUTER`). Check that the National Livestock
   Data Standard really uses this term (vs "spayed female"), and add the Amharic labels if the
   standard has them.
3. **Fertilizer additions:** `FERT_BIO_RHIZO` ("Bio-Rhizobium") is an inoculant rather than a
   fertilizer. Confirm it belongs in `FERTILIZER_TYPE`. Also, the extra details you had
   (licence number, manufacturer, composition) are not carried. That's fine for now, but
   list them in the next PR so we can decide on a schema extension.
4. **Still open from the guide:** body condition scale (BCS1–5 vs POOR…EXCELLENT) and
   whether "High/Mid/Low land" is the agro-ecological zone. Both still need agreement before
   anyone changes those lists.

---

## 4. Process for next time

1. **Ask for a review before merging.** PR #6 merged with no review. For data PRs, one
   reviewer should at least skim a sample of the generated values, not just the green checks.
2. **Run the three checks in section 1** before every push, and paste the `[ETH-OAN]` line into
   the PR description.
3. **Look at the output, not just the counts.** Opening `seed_variety.json` and scrolling
   through a few hundred lines would have shown the "…" and blank names straight away.
4. **Put source caveats in the PR description.** For example: "source is an archived snapshot;
   300 rows are truncated; recovered from details pages".

---

## 5. Checklist for the follow-up PR

- [ ] Full names recovered for the 204 truncated varieties; names **and** codes regenerated
- [ ] 38 nameless varieties named from `details_url`, or dropped and listed in the PR
- [ ] 6 true duplicate pairs merged into one code each; the Deka and Awash pairs resolved after name recovery
- [ ] No source-row-number suffixes left in codes
- [ ] Amharic moved from `value_display` to `display_i18n.am` (46)
- [ ] `check_varieties()` guard added to `convert_moa_catalogs.py` and passing
- [ ] Rebuilt with `build_eth_oan_pack.py`; `validate_pack.py ../../packs/ETH-OAN` → `ok (0 errors, …)`
- [ ] `check_data_files.py` and `ruff` clean
- [ ] PR description: source and date, what was dropped and why, the `[ETH-OAN]` validator line
- [ ] Reviewer assigned before merge
