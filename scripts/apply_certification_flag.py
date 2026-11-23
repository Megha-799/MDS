#!/usr/bin/env python3
"""
apply_certification_flag.py
---------------------------
Applies and synchronizes the 'certification_status' attribute flag
exclusively across CROP-related catalogues (CROP_CATALOG, CROP_VARIETY_CATALOG,
CROP_CATEGORY_CATALOG) in PostgreSQL.

Features:
  1. Does NOT touch general/non-crop catalogues (Geography, Demography, etc.).
  2. Ensures CROP schemas have certification_status with default: "CERTIFIED".
  3. Sets a trigger on CROP line items to auto-default certification_status = 'CERTIFIED'.
  4. Backfills all existing crop records and configures demo uncertified/provisional records.

Usage:
    python3 scripts/apply_certification_flag.py

Zero external dependencies required (uses psql via local port 5434 or docker exec).
"""

import os
import sys
import subprocess
import json

# DB connection settings
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5434")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASS = os.environ.get("DB_PASSWORD", "password")
DB_NAME = os.environ.get("DB_NAME", "master_data")
DOCKER_CONTAINER = "mds-standalone-postgres"


def run_sql(sql_statement: str) -> str:
    """Execute SQL using host psql or fallback to docker exec."""
    env = os.environ.copy()
    env["PGPASSWORD"] = DB_PASS

    try:
        cmd = [
            "psql",
            "-h", DB_HOST,
            "-p", DB_PORT,
            "-U", DB_USER,
            "-d", DB_NAME,
            "-t",
            "-A",
            "-c", sql_statement
        ]
        res = subprocess.run(cmd, env=env, capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        cmd = [
            "docker", "exec", "-i",
            DOCKER_CONTAINER,
            "psql",
            "-U", DB_USER,
            "-d", DB_NAME,
            "-t",
            "-A",
            "-c", sql_statement
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return res.stdout.strip()


def main():
    print("=" * 70)
    print(" MDS Crop Catalog Certification Status Synchronization")
    print("=" * 70)

    print("\n[1/4] Installing Auto-Default Trigger for CROP line items...")
    trigger_sql = """
    BEGIN;
    -- Remove any legacy triggers that forced schema on all catalogues
    DROP TRIGGER IF EXISTS trg_g2p_attributes_auto_cert ON g2p_attributes;
    DROP TRIGGER IF EXISTS trg_g2p_list_versions_auto_cert ON g2p_list_versions;
    DROP FUNCTION IF EXISTS g2p_catalogue_auto_certification_schema();

    -- Install trigger that ONLY defaults certification_status for CROP catalogues
    CREATE OR REPLACE FUNCTION g2p_catalogue_auto_certification_value()
    RETURNS trigger AS $$
    DECLARE
        has_cert_schema boolean := false;
    BEGIN
        IF NEW.list_id LIKE 'CROP%' THEN
            has_cert_schema := true;
        ELSE
            SELECT (attribute_schema->'properties'->'certification_status' IS NOT NULL)
            INTO has_cert_schema
            FROM g2p_list_versions
            WHERE list_id = NEW.list_id AND version_no = NEW.version_no;
        END IF;

        IF has_cert_schema THEN
            IF NEW.attributes IS NULL OR jsonb_typeof(NEW.attributes) != 'object' THEN
                NEW.attributes := '{"certification_status": "CERTIFIED"}'::jsonb;
            ELSIF NEW.attributes->>'certification_status' IS NULL OR NEW.attributes->>'certification_status' = '' THEN
                NEW.attributes := jsonb_set(NEW.attributes, '{certification_status}', '"CERTIFIED"'::jsonb);
            END IF;
        END IF;

        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS trg_g2p_list_values_auto_cert ON g2p_list_version_values;
    CREATE TRIGGER trg_g2p_list_values_auto_cert
    BEFORE INSERT ON g2p_list_version_values
    FOR EACH ROW
    EXECUTE FUNCTION g2p_catalogue_auto_certification_value();
    COMMIT;
    """
    run_sql(trigger_sql)
    print("  -> Trigger installed: New CROP entries will automatically default to 'CERTIFIED'.")
    print("  -> Non-crop catalogues remain completely unaffected.")

    print("\n[2/4] Ensuring 'certification_status' in JSON schemas for CROP catalogs...")
    schema_sql = """
    BEGIN;
    -- Update g2p_attributes schema for CROP catalogs only
    UPDATE g2p_attributes
    SET attribute_schema = jsonb_set(
        COALESCE(attribute_schema, '{"type":"object","properties":{}}'::jsonb),
        '{properties,certification_status}',
        '{"type": "string", "enum": ["CERTIFIED", "UNCERTIFIED", "PROVISIONAL"], "default": "CERTIFIED", "description": "Official certification flag: CERTIFIED, UNCERTIFIED, or PROVISIONAL"}'::jsonb
    )
    WHERE attribute_code IN ('CROP_VARIETY_CATALOG', 'CROP_CATALOG', 'CROP_CATEGORY_CATALOG');

    -- Update g2p_list_versions schema
    ALTER TABLE g2p_list_versions DISABLE TRIGGER trg_g2p_list_versions_guard;

    UPDATE g2p_list_versions
    SET attribute_schema = jsonb_set(
        COALESCE(attribute_schema, '{"type":"object","properties":{}}'::jsonb),
        '{properties,certification_status}',
        '{"type": "string", "enum": ["CERTIFIED", "UNCERTIFIED", "PROVISIONAL"], "default": "CERTIFIED", "description": "Official certification flag: CERTIFIED, UNCERTIFIED, or PROVISIONAL"}'::jsonb
    )
    WHERE list_id IN (
        SELECT attribute_id FROM g2p_attributes WHERE attribute_code IN ('CROP_VARIETY_CATALOG', 'CROP_CATALOG', 'CROP_CATEGORY_CATALOG')
    );

    ALTER TABLE g2p_list_versions ENABLE TRIGGER trg_g2p_list_versions_guard;
    COMMIT;
    """
    run_sql(schema_sql)
    print("  -> Crop schemas updated with default: 'CERTIFIED'.")

    print("\n[3/4] Synchronizing CROP records & demo flags...")
    data_sql = """
    BEGIN;
    ALTER TABLE g2p_list_version_values DISABLE TRIGGER trg_g2p_list_version_values_guard;

    -- 1. CROP_CATALOG
    UPDATE g2p_list_version_values
    SET attributes = jsonb_set(COALESCE(attributes, '{}'::jsonb), '{certification_status}', '"CERTIFIED"'::jsonb)
    WHERE list_id = 'CROP_CATALOG'
      AND (attributes->>'certification_status' IS NULL OR attributes->>'certification_status' = '');

    UPDATE g2p_list_version_values
    SET attributes = jsonb_set(attributes, '{certification_status}', '"UNCERTIFIED"'::jsonb)
    WHERE list_id = 'CROP_CATALOG' AND value_code = '1';

    UPDATE g2p_list_version_values
    SET attributes = jsonb_set(attributes, '{certification_status}', '"PROVISIONAL"'::jsonb)
    WHERE list_id = 'CROP_CATALOG' AND value_code = '5';

    -- 2. CROP_CATEGORY_CATALOG
    UPDATE g2p_list_version_values 
    SET attributes = jsonb_set(COALESCE(attributes, '{}'::jsonb), '{certification_status}', '"CERTIFIED"'::jsonb)
    WHERE list_id = (SELECT attribute_id FROM g2p_attributes WHERE attribute_code = 'CROP_CATEGORY_CATALOG')
      AND version_no = 1;

    INSERT INTO g2p_list_version_values (list_id, version_no, value_id, value_code, display, display_i18n, parent_value_code, sort_order, attributes, roles, status)
    SELECT 
        list_id, 5, value_id, value_code, display, display_i18n, parent_value_code, sort_order, 
        jsonb_set(COALESCE(attributes, '{}'::jsonb), '{certification_status}', '"CERTIFIED"'::jsonb), roles, status
    FROM g2p_list_version_values 
    WHERE list_id = (SELECT attribute_id FROM g2p_attributes WHERE attribute_code = 'CROP_CATEGORY_CATALOG')
      AND version_no = 1
    ON CONFLICT (list_id, version_no, value_id) DO UPDATE 
    SET attributes = EXCLUDED.attributes;

    UPDATE g2p_list_version_values 
    SET attributes = jsonb_set(COALESCE(attributes, '{}'::jsonb), '{certification_status}', '"UNCERTIFIED"'::jsonb)
    WHERE list_id = (SELECT attribute_id FROM g2p_attributes WHERE attribute_code = 'CROP_CATEGORY_CATALOG')
      AND version_no = 5 AND value_id = 'qa1';

    -- 3. CROP_VARIETY_CATALOG
    UPDATE g2p_list_version_values
    SET attributes = jsonb_set(COALESCE(attributes, '{}'::jsonb), '{certification_status}', '"CERTIFIED"'::jsonb)
    WHERE list_id = (SELECT attribute_id FROM g2p_attributes WHERE attribute_code = 'CROP_VARIETY_CATALOG')
      AND (attributes->>'certification_status' IS NULL OR attributes->>'certification_status' = '');

    INSERT INTO g2p_list_version_values (list_id, version_no, value_id, value_code, display, sort_order, status, attributes)
    SELECT attribute_id, 1, 'var_barley_shewa_demo', 'Barley-Shewa-White (Provisional)', 
           'Barley-Shewa-White (Provisional)', 0, 'ACTIVE',
           '{"source": "Indigenous Wild", "crop_name": "Barley", "maintainer": "Regional Agriculture Bureau", "release_year": 2026, "certification_status": "PROVISIONAL"}'::jsonb
    FROM g2p_attributes WHERE attribute_code = 'CROP_VARIETY_CATALOG'
    ON CONFLICT (list_id, version_no, value_id) DO UPDATE 
    SET attributes = EXCLUDED.attributes, status = 'ACTIVE';

    INSERT INTO g2p_list_version_values (list_id, version_no, value_id, value_code, display, sort_order, status, attributes)
    SELECT attribute_id, 1, 'var_teff_field_demo', 'Tef-Local-Landrace (Farmer Selection)', 
           'Tef-Local-Landrace (Farmer Selection)', 0, 'ACTIVE',
           '{"source": "Farmer Selection", "crop_name": "Tef", "maintainer": "Field Enumeration Collection", "release_year": 2026, "certification_status": "UNCERTIFIED"}'::jsonb
    FROM g2p_attributes WHERE attribute_code = 'CROP_VARIETY_CATALOG'
    ON CONFLICT (list_id, version_no, value_id) DO UPDATE 
    SET attributes = EXCLUDED.attributes, status = 'ACTIVE';

    ALTER TABLE g2p_list_version_values ENABLE TRIGGER trg_g2p_list_version_values_guard;
    COMMIT;
    """
    run_sql(data_sql)
    print("  -> Crop records and demo flags synchronized.")

    print("\n[4/4] Verification & Summary:")
    summary_sql = """
    SELECT 
        a.attribute_code,
        val.version_no,
        val.attributes->>'certification_status' as status_flag,
        count(*) as count
    FROM g2p_attributes a
    JOIN g2p_list_version_values val ON a.attribute_id = val.list_id
    WHERE a.attribute_code IN ('CROP_CATEGORY_CATALOG', 'CROP_CATALOG', 'CROP_VARIETY_CATALOG')
    GROUP BY a.attribute_code, val.version_no, val.attributes->>'certification_status'
    ORDER BY a.attribute_code, val.version_no, val.attributes->>'certification_status';
    """
    out = run_sql(summary_sql)
    print("\nCurrent Database Distribution:")
    print("Catalog | Version | Flag | Count")
    print("-" * 50)
    for line in out.splitlines():
        if line.strip():
            parts = line.split("|")
            print(f"{parts[0]:<22} | v{parts[1]:<2} | {parts[2]:<12} | {parts[3]}")

    print("\n" + "=" * 70)
    print(" Done! Only Crop catalogs have certification status.")
    print("=" * 70)


if __name__ == "__main__":
    main()
