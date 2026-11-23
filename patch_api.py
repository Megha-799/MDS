"""
Agri-Stack Backend Extension Patch for Master Data Service (G2R-505)

Enforces server-side validation rejecting past effective_from dates
in catalogue and geography versions without altering upstream OpenG2P core git code.
Runs on container startup before Gunicorn starts.
"""
import os
import sys

print("[Agri-Stack API Patch] Applying G2R-505 past effective date validation...")

SERVICES = [
    "/usr/local/lib/python3.12/site-packages/openg2p_gen2_master_data/services/g2p_catalogue_list_service.py",
    "/usr/local/lib/python3.12/site-packages/openg2p_gen2_master_data/services/g2p_catalogue_geo_service.py",
]

PATCH_CHECK = """        now = utcnow()
        if as_aware(effective_from) < now - timedelta(minutes=5):
            raise CatalogueError(
                "G2P-CAT-400",
                f"effective_from {effective_from} cannot be in the past",
            )
"""

for filepath in SERVICES:
    if not os.path.exists(filepath):
        print(f"[Agri-Stack API Patch] File not found: {filepath}, skipping.")
        continue

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    if "cannot be in the past" in content:
        print(f"[Agri-Stack API Patch] Validation already present in {os.path.basename(filepath)}.")
        continue

    # Ensure timedelta is imported
    if "from datetime import datetime" in content and "timedelta" not in content:
        content = content.replace("from datetime import datetime", "from datetime import datetime, timedelta", 1)

    # Insert validation into _check_effective_from
    target_needle = 'f"effective_from {effective_from} is earlier than the latest published version\'s ({last})",\n            )\n'
    if target_needle in content:
        replacement = target_needle + PATCH_CHECK
        content = content.replace(target_needle, replacement, 1)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[Agri-Stack API Patch] Successfully applied G2R-505 fix to {os.path.basename(filepath)}.")
    else:
        print(f"[Agri-Stack API Patch] Could not locate insertion point in {os.path.basename(filepath)}.")

print("[Agri-Stack API Patch] Backend patch execution completed.")

