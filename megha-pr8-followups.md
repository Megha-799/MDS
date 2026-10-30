# Follow-ups after PR #8: SEED_VARIETY names

**To:** Megha
**PR:** Centre-for-Open-Societal-Systems/openg2p-data#8 (commit `86a91f9`)
**Checked:** 2026-10-27

---

## First: thank you

PR #8 fixed everything the CI checks look for:
- `check_pack_lists.py` reports 0 findings (502 fixed).
- `validate_pack.py` on ETH-OAN is `ok`.
- The transformations log (`scripts/packs/sources/seed_variety_transformations.md`) is exactly the audit trail we needed.

The points below are things **the checks cannot see**. They are about whether a name is the real variety name and whether two codes are the same variety. They are not blockers for merging #8. Please fix them in **one follow-up PR before the first seed**.

**Why before the first seed:** a code becomes permanent once a farmer record uses it. Nothing is seeded yet (`geoSeed.enabled: false` everywhere), so today any code can still be renamed or removed for free. After the first seed, each fix means retiring codes and migrating records.

---

## 1. Values with no real variety name

These show only the crop name, so a user can't tell what variety they are:

| Code | Shows | Source row |
|---|---|---|
| `VAR_SORGHUM_SORGHUM` | Sorghum – Sorghum | 2009, MARC/EIAR |
| `VAR_ONION_ONION` | Onion – Onion | 2004, MARC/EIAR |
| `VAR_TOMATO_TOMATO` | Tomato – Tomato | 2013, Green life trading PLC |
| `VAR_FABA_BEAN_FABA_BEAN` | Faba bean – Faba bean | HARC/EIAR |
| `VAR_PIGEON_PEA_PIGEON_PEA` | Pigeon pea – Pigeon pea | 2023 |
| `VAR_BARLEY_FOOD_BARLEY` | Food Barley – food barley | 2023, row 902 |

`VAR_CACAO_CACAO` ("Cacao – Cacao (Theobroma cacao)") is similar: the name in brackets is the botanical name, not a variety.

**Fix:** treat these like the 38 nameless rows. Find the real name, or drop them and list them in section 3 of the transformations log.
**Guard:** in `check_varieties()`, fail when the variety part (after " – ") equals the crop name, ignoring case and spaces.

---

## 2. The same variety under two codes

Same crop, same release year, same research centre. Only the spelling differs:

| Keep | Remove | Why they look the same |
|---|---|---|
| `VAR_WHEAT_DANDAA` (**base pack**, "Danda'a", Danphe #1) | `VAR_BREAD_WHEAT_DANDA_A` ("Danda’a (Danphe#1)") | 2010, Kulumsa. The curly ’ vs straight ' made the base-pack check miss it |
| one of | `VAR_MAIZE_MELKASA1Q` / `VAR_MAIZE_MELKASA_1Q` | 2013, Melkasa |
| one of | `VAR_SORGHUM_PAC537` / `VAR_SORGHUM_PAC_537` | "PAC537" vs "PAC 537" |
| one of | `VAR_MAIZE_A7033_F_7215` / `VAR_MAIZE_A7033_F7215` | "F-7215" vs "F7215", BARC |
| check | `VAR_FINGER_MILLET_HARO` / `VAR_FINGER_MILLET_HARO_LANDRACE` | both "Haro (FMC-33)", 2023 |

`Amibara` (2017) and `Amibera` (2015) have different release years, so they're probably two varieties. Leave them, but mention it in the log.

**Fix:** when you merge a pair, keep the code without extra separators. Carry over any detail only one row has (release year, breeding code).
**Guard:** compare names after **normalising**: lower-case, `’` → `'`, and remove spaces, hyphens and other punctuation. Check within the converter's own output **and** against the base pack.

---

## 3. Codes built from the wrong part of the name

When the source puts the variety's local name in brackets, the converter builds the code from the line number instead:

| Code now | Shows | Should be |
|---|---|---|
| `VAR_CHICKPEA_ICCMABCA` | Chickpea – (Girar) ICCMABCA | `VAR_CHICKPEA_GIRAR`, shown as "Girar (ICCMABCA)" |
| `VAR_CHICKPEA_ACC_41053` | Chickpea – (Maritu) Acc.41053 | `VAR_CHICKPEA_MARITU` |
| `VAR_CHICKPEA_DZ_2012_CK_001_FLIP` | Chickpea – (Hora) DZ-2012 CK-001/FLIP | `VAR_CHICKPEA_HORA` |
| `VAR_CHICKPEA_DZ_2012_CK_009_FLIP` | Chickpea – (Dhera) DZ-2012 CK-009/FLIP | `VAR_CHICKPEA_DHERA` |
| `VAR_SOYBEAN_TGX1990_114FN` | Forage Soyabean – (Milkii) TGX1990-114FN | `VAR_SOYBEAN_MILKII` |
| `VAR_SORGHUM_14MWLSDT7114` | Sorghum – (Tilahun) 14MWLSDT7114 | `VAR_SORGHUM_TILAHUN` |
| `VAR_SORGHUM_ETS_2752` | Sorghum – ((Jiru) (yellow)/ETS-2752) | `VAR_SORGHUM_JIRU` |
| `VAR_COMMON_BEAN_HARICOT_BEAN` (row 704) | Common/Haricot/ bean – Haricot bean- (Hundaf) | `VAR_COMMON_BEAN_HUNDAF` |
| `VAR_POTATO_HERMES` | Irish potato – (Solanum tuberosum)Hermes | shown as "Hermes" |
| `VAR_FINGER_MILLET_KUMSA` | Finger Millet – : Kumsa | shown as "Kumsa" (no leading colon) |

**Rule:** the variety name comes first, and the line or pedigree code goes in brackets after it, e.g. "Girar (ICCMABCA)". The code is built from the variety name.
**Guard:** fail when the variety part starts with `(`, `:`, `-` or `/`.

---

## 4. Crop name repeated inside the variety name (about 20)

The source often repeats the crop ("soyabean- katta"), and that ends up in both the code and the display:

```
VAR_SOYBEAN_SOYABEAN_KATTA            Soybean – soyabean- katta(PR-145-2)
VAR_SOYBEAN_SOYABEAN_BELESA_95        Soybean – soyabean- belesa -95
VAR_SOYBEAN_SOYABEAN_KORME            Soybean – soyabean- korme (AGS-129-2)
VAR_SOYBEAN_SOYABEAN_CHERI_IPB_81_EP7
VAR_SOYBEAN_SOYABEAN_ETHIO_YUGOSLAVIA
VAR_SOYBEAN_SOYBEAN_ETHIOYUGOZLAVIA   ← also likely the same variety as the one above
VAR_SOYBEAN_SOYBEAN_AFGAT
VAR_SORGHUM_SORGHUM_MELKAM
VAR_RICE_RICE_NERIKA_4
VAR_MALT_BARLEY_MALT_BARLEY_ABDANE
VAR_BARLEY_FOOD_BARLEY_HB_1307
VAR_FABA_BEAN_FABA_BEAN_DOSHA
VAR_MUNG_BEAN_MUNGBEAN_ARKEBE / _BORDA
VAR_POTATO_IRISH_POTATO_WORKU
VAR_SWEET_POTATO_SWEET_POTATO_NASPOT_12   Sweet potato – Sweet potato (Ipomoea batatas)-NASPOT-12 (Orange)
VAR_TARO_TARO_MULU_04
VAR_CASSAVA_CASSAVA_HAWASSA_5
VAR_WATERMELON_WATERMELON_TAMERLAN_F1
VAR_ADZUKI_BEAN_ADZUKI_BEAN_JAPAN
VAR_TOMATO_JORGIE_2_CHERRY_TOMATO
```

**Fix:** before building the name, strip a leading crop name, including spelling variants (soyabean/soybean, mungbean/mung bean) and a botanical name in brackets, then the separator after it. For example, "soyabean- katta(PR-145-2)" becomes "Katta (PR-145-2)" with code `VAR_SOYBEAN_KATTA`. Also title-case lower-case names ("katta" → "Katta").

Small cleanups in the same pass: "Mekelle- 03" → "Mekelle-03" and "Melkasa- 5" → "Melkasa-5" (stray space after a hyphen). Check whether "Gofta- Food" and "Ayenew- Food" are names or a "food type" note; if they're notes, the codes should be `VAR_COMMON_BEAN_GOFTA` / `_AYENEW`.

**Guard:** fail when the code contains the crop part twice (e.g. `SOYBEAN_SOYABEAN`, `SORGHUM_SORGHUM`).

---

## 5. Question: maize parent lines

These are breeding parent lines used to produce hybrid seed, not varieties a farmer plants:

```
VAR_MAIZE_142_1_E       142-1-e (Maize parental line)
VAR_MAIZE_144_7_B       144-7-b (Male parent for BH670)
VAR_MAIZE_CML395_CML202 CML395/CML202 (Female parent for BH661)
VAR_MAIZE_BKL001        BKL001 (Male parent for BH546)
VAR_MAIZE_BKL003        BKL003 (Male parent for BH547)
VAR_MAIZE_124_B         124-b(109) (Male parent for Basic)
… plus CML395, CML202, SC22, BKL002, A7033/F7215 and CML 395 X CML 202
```

Please ask the farmer-registry team whether `SEED_VARIETY` is "what the farmer planted". If it is, leave these out, or move them to a separate list for seed producers. Either way, say what you decided in the PR.

---

## 6. Evidence for two claims in the PR

- **Deka (rows 195 and 198):** the PR comment says both are "the 2018 Kulumsa release, ETBW 6583". Both source rows are cut off at "ETBW …", so please say where 6583 comes from (a MoA catalogue page, or the details page) and put that reference in the transformations log.
- **Awash-1 / Awash Mitra:** the converter comments name the releasing centres. Please add the document they come from (title and year of the MoA National Variety Release catalogue), so a reviewer can check it.

---

## 7. Make the converter guard catch these

Add these to `check_varieties()` so none of the above can come back. All of them must fail **before anything is written**:

```python
import re, unicodedata

def norm(s):
    s = unicodedata.normalize("NFKC", s).replace("’", "'").casefold()
    return re.sub(r"[^a-z0-9]", "", s)

def variety_part(display):
    return display.split(" – ", 1)[1] if " – " in display else display

def crop_key(crop_code):          # CROP_SOYBEAN -> "soybean"
    return norm(crop_code.removeprefix("CROP_"))

# inside check_varieties(values, base_values):
#   1. name is only the crop
if norm(variety_part(disp)) in (crop_key(crop), norm(crop_display)):
    errs.append(f"{vid}: no variety name, only the crop: {disp!r}")
#   3. starts with punctuation
if re.match(r"^[\s(:/\-]", variety_part(disp)):
    errs.append(f"{vid}: variety part starts with punctuation: {disp!r}")
#   4. crop repeated in the code
crop_part = crop.removeprefix("CROP_")
if vid.count(crop_part) > 1:
    errs.append(f"{vid}: crop name repeated in the code")
#   2. near-duplicates, within the output and against the base pack
#   key = (crop, norm(name before the first "(")); two values with the same key fail
```

`crop_display` is the crop's display name from `CROP_COMMODITY`. Also cover spelling variants the source uses (soyabean, mungbean) when you strip a leading crop name.

---

## Before you push

```
python scripts/packs/convert_moa_catalogs.py          # guard must pass
python scripts/packs/build_eth_oan_pack.py ...         # rebuild the pack
cd scripts/packs && python validate_pack.py ../../packs/ETH-OAN   # [ETH-OAN] ok (0 errors, …)
cd ../.. && python scripts/ci/check_pack_lists.py      # 0 new, 0 ETH-OAN additions error(s)
python scripts/ci/check_data_files.py                  # 0 error(s)
```

Open `packs/ETH-OAN/domains/agriculture/seed_variety.json` and read through a few hundred names. Everything in this note can be found by eye that way.

## Checklist

- [ ] Crop-only names named or dropped (Sorghum, Onion, Tomato, Faba bean, Pigeon pea, Food barley, Cacao)
- [ ] Duplicate pairs merged (Danda'a vs the base pack, Melkasa-1Q, PAC 537, A7033/F7215; check Haro)
- [ ] Codes built from the local variety name, not the line number (Girar, Maritu, Hora, Dhera, Milkii, Tilahun, Jiru, Hundaf)
- [ ] Leading punctuation removed (Kumsa, Hermes)
- [ ] Crop name stripped from the start of variety names, and codes regenerated (about 20)
- [ ] Decision on maize parent lines, written in the PR
- [ ] Sources noted for Deka ETBW 6583 and the Awash names
- [ ] `check_varieties()` extended with the guards in section 7
- [ ] Transformations log updated with every renamed, merged or dropped code
- [ ] Reviewer assigned before merge
