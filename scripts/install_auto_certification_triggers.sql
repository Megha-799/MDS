-- ==============================================================================
-- Certification Auto-Default Trigger for OpenG2P Master Data Service
-- ==============================================================================
-- Purpose:
--   1. Restricts 'certification_status' exclusively to CROP-related catalogues
--      (CROP_CATALOG, CROP_VARIETY_CATALOG, CROP_CATEGORY_CATALOG).
--   2. General catalogues (Geography, Demography, Bank, etc.) do NOT receive 
--      any certification fields.
--   3. When any new item/entry is added to a CROP catalogue without an explicit
--      status, it automatically defaults to 'CERTIFIED'.
-- ==============================================================================

BEGIN;

-- 1. Remove any legacy triggers that forced certification schema on all catalogues
DROP TRIGGER IF EXISTS trg_g2p_attributes_auto_cert ON g2p_attributes;
DROP TRIGGER IF EXISTS trg_g2p_list_versions_auto_cert ON g2p_list_versions;
DROP FUNCTION IF EXISTS g2p_catalogue_auto_certification_schema();

-- 2. Trigger Function: Automatically default certification_status to 'CERTIFIED'
--    ONLY for CROP catalogues or catalogues defining certification_status in their schema
CREATE OR REPLACE FUNCTION g2p_catalogue_auto_certification_value()
RETURNS trigger AS $$
DECLARE
    has_cert_schema boolean := false;
BEGIN
    -- Only check for crop catalogues or catalogues with certification_status in their schema
    IF NEW.list_id LIKE 'CROP%' THEN
        has_cert_schema := true;
    ELSE
        SELECT (attribute_schema->'properties'->'certification_status' IS NOT NULL)
        INTO has_cert_schema
        FROM g2p_list_versions
        WHERE list_id = NEW.list_id AND version_no = NEW.version_no;
    END IF;

    -- Automatically set default 'CERTIFIED' if the catalogue uses certification_status
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

-- 3. Install Trigger on g2p_list_version_values (Line Items)
DROP TRIGGER IF EXISTS trg_g2p_list_values_auto_cert ON g2p_list_version_values;
CREATE TRIGGER trg_g2p_list_values_auto_cert
BEFORE INSERT ON g2p_list_version_values
FOR EACH ROW
EXECUTE FUNCTION g2p_catalogue_auto_certification_value();

COMMIT;
