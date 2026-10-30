#!/usr/bin/env python3
"""
Export any Master Data Service (MDS) dataset to CSV or JSON.
Usage:
    python3 export_dataset.py <DATASET_CODE> [--format csv|json] [--env dev|staging] [--out filename]

Examples:
    python3 export_dataset.py CROP_VARIETY
    python3 export_dataset.py LAND_PREPARATION_METHOD --format csv
    python3 export_dataset.py CROP_COMMODITY --env dev
"""

import sys
import os
import argparse
import urllib.request
import urllib.parse
import json
import csv

ENV_CONFIGS = {
    "dev": {
        "base_url": "https://mds-api-dev.oanstaging.com",
        "keycloak_url": "https://keycloak-dev.oanstaging.com",
        "realm": "mds-develop",
        "client_id": "master-data",
        "client_secret": "lqQVel10DTXO4u0gO76HxILY5kUcBVPt2WcnKEIA"
    },
    "staging": {
        "base_url": "https://mds-api-staging.oanstaging.com",
        "keycloak_url": "https://keycloak-staging.oanstaging.com",
        "realm": "mds-staging",
        "client_id": "master-data",
        "client_secret": "lqQVel10DTXO4u0gO76HxILY5kUcBVPt2WcnKEIA"
    }
}

def get_token(config):
    url = f"{config['keycloak_url']}/realms/{config['realm']}/protocol/openid-connect/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": config["client_id"],
        "client_secret": config["client_secret"],
        "scope": "openid profile email"
    }
    data = urllib.parse.urlencode(payload).encode()
    req = urllib.request.Request(url, data=data)
    with urllib.request.urlopen(req, timeout=15) as res:
        res_json = json.loads(res.read().decode())
        return res_json["access_token"]

def fetch_dataset_values(config, token, dataset_code, version="latest"):
    url = f"{config['base_url']}/catalogue/get_list_values"
    all_values = []
    page = 1
    page_size = 1000

    print(f"Fetching dataset '{dataset_code}' (version: {version}) from {config['base_url']}...")
    while True:
        body = {
            "request_header": {
                "sender_app_mnemonic": "Farmer",
                "sender_app_url": "https://farmer-registry.oanstaging.com",
                "request_id": f"export-{page}",
                "request_timestamp": "2026-10-29T12:00:00Z"
            },
            "request_body": {
                "pagination_request": {
                    "current_page": page,
                    "page_size": page_size
                },
                "request_payload": {
                    "list_code": dataset_code,
                    "version": version,
                    "include_retired": True
                }
            }
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as res:
                data = json.loads(res.read().decode())
                payload = data.get("response_body", {}).get("response_payload") or {}
                if not payload:
                    err_msg = data.get("response_header", {}).get("response_message") or "Dataset not found or has no entries."
                    print(f"Warning for '{dataset_code}': {err_msg}")
                    break
                values = payload.get("values", [])
                total = payload.get("total", len(values))
                all_values.extend(values)
                print(f"  Retrieved page {page}: {len(values)} entries (total retrieved so far: {len(all_values)}/{total})")
                if len(all_values) >= total or len(values) == 0:
                    break
                page += 1
        except urllib.error.HTTPError as e:
            err_msg = e.read().decode()
            print(f"Error fetching dataset (HTTP {e.code}): {err_msg}", file=sys.stderr)
            sys.exit(1)

    return all_values

def export_to_csv(values, filename):
    if not values:
        print("No entries to export.")
        return

    # Collect all attribute field names dynamically
    attr_keys = set()
    for v in values:
        attrs = v.get("attributes") or {}
        if isinstance(attrs, dict):
            attr_keys.update(attrs.keys())
    attr_keys = sorted(list(attr_keys))

    headers = ["value_code", "display", "status", "sort_order", "parent_code"] + attr_keys

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for v in values:
            attrs = v.get("attributes") or {}
            row = [
                v.get("value_code") or v.get("value_id") or "",
                v.get("display") or "",
                v.get("status") or "",
                v.get("sort_order") or "",
                v.get("parent_code") or ""
            ]
            for k in attr_keys:
                row.append(attrs.get(k, ""))
            writer.writerow(row)
    print(f"\nSuccessfully exported {len(values)} entries to CSV: {filename}")

def export_to_json(values, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(values, f, indent=2, ensure_ascii=False)
    print(f"\nSuccessfully exported {len(values)} entries to JSON: {filename}")

def main():
    parser = argparse.ArgumentParser(description="Export datasets from OpenG2P Master Data Service")
    parser.add_argument("dataset", help="Dataset/List code (e.g. CROP_VARIETY, LAND_PREPARATION_METHOD)")
    parser.add_argument("--format", choices=["csv", "json"], default="csv", help="Export format (default: csv)")
    parser.add_argument("--env", choices=["dev", "staging"], default="dev", help="Target environment (default: dev)")
    parser.add_argument("--version", default="latest", help="Version to export ('latest', 'draft', or version number)")
    parser.add_argument("--out", help="Output file path (default: <dataset>.<format>)")

    args = parser.parse_args()
    config = ENV_CONFIGS[args.env]
    out_file = args.out or f"{args.dataset.lower()}_export.{args.format}"

    try:
        token = get_token(config)
    except Exception as e:
        print(f"Failed to authenticate with Keycloak: {e}", file=sys.stderr)
        sys.exit(1)

    values = fetch_dataset_values(config, token, args.dataset, args.version)
    if args.format == "csv":
        export_to_csv(values, out_file)
    else:
        export_to_json(values, out_file)

if __name__ == "__main__":
    main()
