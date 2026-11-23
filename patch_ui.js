/**
 * Agri-Stack UI Customization Patch for Master Data Service
 * 
 * Replaces generic database/developer terminology (Datasets, Open draft, Releases)
 * with user-friendly agricultural terminology for Ethiopia Agri-Stack (MoA)
 * without modifying upstream OpenG2P core code.
 */
const fs = require('fs');
const path = require('path');

console.log('[Agri-Stack UI Patch] Applying agricultural terminology...');

// Mapping of technical terms to user-friendly Agri-Stack terminology
const AGRI_LABEL_OVERRIDES = {
  // Navigation & Core Labels
  'reference_data': 'Agricultural Catalogs',
  'attribute_code': 'Catalog Code',
  'add_new_attribute': 'New Catalog',
  'edit_reference_data': 'Edit Catalog',
  'search_attributes': 'Search catalogs...',
  'no_attributes': 'No catalogs found',
  'confirm_remove_attribute': 'Delete catalog',
  'confirm_remove_attribute_msg': 'Delete this catalog and all of its entries? This cannot be undone:',
  'attribute_added_successfully': 'Catalog created',
  'attribute_updated_successfully': 'Catalog updated',
  'attribute_deleted_successfully': 'Catalog deleted',
  'attribute_delete_failed': 'Failed to delete catalog',
  'attr_code_required': 'A catalog code is required',
  'error_attribute_code_exists': 'A catalog with this code already exists',
  'error_not_hierarchical': 'This catalog is not hierarchical',

  // Versioning & Workflow Actions (Maker-Checker)
  'releases': 'Published Versions',
  'cat_open_draft': 'Edit Catalog',
  'cat_version_draft': 'Pending Updates',
  'cat_status_DRAFT': 'Draft / Under Review',
  'cat_rework_rejected': 'Rework as new update',
  'cat_view_draft': 'View pending updates',
  'cat_edit_draft_details': 'Catalog details',
  'cat_submit_title': 'Submit updates for approval',
  'cat_submit_message': 'The updates are validated and can no longer be edited while waiting for approval.',
  'cat_discard': 'Discard changes',
  'cat_discard_title': 'Discard changes',
  'cat_discard_message': 'Discard pending updates for version {no}?',
  'cat_draft_opened': 'Catalog update draft opened',
  'cat_draft_updated': 'Catalog details saved',
  'cat_draft_submitted': 'Submitted for approval',
  'cat_draft_approved': 'Version approved and published',
  'cat_draft_rejected': 'Updates rejected',
  'cat_draft_discarded': 'Updates discarded',
  'cat_maker_cannot_approve': 'You proposed these changes, so another officer must approve or reject them.',
  'cat_readonly_view_draft_hint': 'This version is read-only. Switch to the pending draft to make changes.',
  'cat_readonly_open_draft_hint': 'This version is read-only. Click "Edit Catalog" to propose updates.',

  // Schema & Fields
  'cat_tab_schema': 'Form Fields & Rules',
  'cat_edit_list': 'Edit catalog details',
  'cat_list_create_hint': 'The catalog is created with its initial draft (version 1). Add entries, then submit for approval to publish.',
  'cat_list_edit_hint': 'Description, publisher and theme apply immediately. Code, label, and entries are submitted for approval.',
  'cat_owner_org_hint': 'Ministry department responsible for this catalog (used for approval routing).',
  'cat_draft': 'Draft / Pending',
  'cat_attributes_json_hint': 'This catalog has no custom fields; entries use standard fields.',
  'cat_attribute_schema': 'Form Fields & Rules',
  'cat_schema_fields': 'Catalog Fields',
  'cat_list_ref': 'Catalog Reference',
  'cat_diff_metadata': 'Catalog details',
  'cat_subject_list': 'Catalogs',
  'cat_subject_release': 'Published Versions',
  'cat_feed_hint': 'Audit log of all catalog, geography and baseline version events, newest first.',

  // Baselines & Releases
  'cat_releases_hint': 'A published version pins an approved baseline of each agricultural catalog plus geography, so registries can pin everything consistently.',
  'cat_create_release': 'Create Baseline Version',
  'cat_release_code': 'Version Code',
  'cat_release_code_hint': 'For example 2026.1',
  'cat_release_code_required': 'A version code is required.',
  'cat_release_created': 'Baseline version created',
  'cat_members': 'Catalogs',
  'cat_no_releases': 'No published baselines yet.',
  'cat_list': 'Catalog',
  'cat_select_list': 'Select a catalog',
  'cat_add_member': 'Add catalog',
  'cat_release_no_members': 'No catalogs pinned.',
  'cat_release_members_saved': 'Baseline members saved',
  'cat_release_published': 'Baseline version published',
  'cat_release_deleted': 'Draft baseline deleted',
  'cat_dataset': 'Catalog',
  'cat_subject_type_list': 'Catalog',
  'cat_subject_type_release': 'Baseline Version',

  // Home Page
  'home_hint': 'Agricultural catalogs by theme, geography baseline, items pending review, and recent activity.',
  'home_datasets_by_theme': 'Catalogs by Theme',
  'home_all_datasets': 'All {count} Catalogs',
  'home_drafts_in_progress': 'Updates in progress',
  'home_no_drafts': 'No pending updates.',
  'home_latest_release': 'Latest Baseline: {code}'
};

// Locate locale chunk in .next/server/chunks/ssr/
const ssrDir = path.join(process.cwd(), '.next/server/chunks/ssr');
if (fs.existsSync(ssrDir)) {
  const files = fs.readdirSync(ssrDir);
  const localeFiles = files.filter(f => f.startsWith('locales_en_json_') && f.endsWith('.js'));

  for (const file of localeFiles) {
    const fullPath = path.join(ssrDir, file);
    try {
      const content = fs.readFileSync(fullPath, 'utf8');
      const idMatch = content.match(/module\.exports=\[(\d+),/);
      const chunkId = idMatch ? idMatch[1] : '807';

      const fn = new Function('module', content);
      const mod = {};
      fn(mod);

      let dict = {};
      mod.exports[1]({ v: (o) => { dict = o; } });

      let modifiedCount = 0;
      for (const [key, val] of Object.entries(AGRI_LABEL_OVERRIDES)) {
        if (dict[key] !== val) {
          dict[key] = val;
          modifiedCount++;
        }
      }

      const serialized = JSON.stringify(JSON.stringify(dict));
      const newChunk = 'module.exports=[' + chunkId + ',a=>{a.v(JSON.parse(' + serialized + '))\n}];\n';
      fs.writeFileSync(fullPath, newChunk, 'utf8');
      console.log(`[Agri-Stack UI Patch] Successfully updated ${modifiedCount} labels in ${file}!`);
    } catch (err) {
      console.error(`[Agri-Stack UI Patch] Error patching ${file}:`, err.message);
    }
  }
} else {
  console.log('[Agri-Stack UI Patch] .next/server/chunks/ssr not found, skipping UI patch.');
}

// 2. Patch attribute formatting to highlight [CERTIFIED], [UNCERTIFIED], [PROVISIONAL]
const ssrAttrFile = path.join(process.cwd(), '.next/server/chunks/ssr/src_features_attributes_index_ts_962d587c._.js');
if (fs.existsSync(ssrAttrFile)) {
  let content = fs.readFileSync(ssrAttrFile, 'utf8');
  const targetK = 'k=(d=a.attributes)?Object.entries(d).map(([a,b])=>`${a}: ${"string"==typeof b?b:JSON.stringify(b)}`).join(" · "):"";';
  const replaceK = 'k=(d=a.attributes)?Object.entries(d).sort(([x],[y])=>x==="certification_status"?-1:y==="certification_status"?1:0).map(([a,b])=>a==="certification_status"?`[${b}]`: `${a}: ${"string"==typeof b?b:JSON.stringify(b)}`).join(" · "):"";';
  if (content.includes(targetK)) {
    content = content.replace(targetK, replaceK);
    console.log('[Agri-Stack UI Patch] Patched SSR attribute formatting to highlight certification_status');
  }
  const targetSearch = '||Object.values(b.display_i18n??{}).some(b=>b.toLowerCase().includes(a)):';
  const replaceSearch = '||Object.values(b.display_i18n??{}).some(b=>b.toLowerCase().includes(a))||(b.attributes&&JSON.stringify(b.attributes).toLowerCase().includes(a)):';
  if (content.includes(targetSearch)) {
    content = content.replace(targetSearch, replaceSearch);
    console.log('[Agri-Stack UI Patch] Patched SSR search filter to include attributes');
  }
  fs.writeFileSync(ssrAttrFile, content, 'utf8');
}

const clientAttrFile = path.join(process.cwd(), '.next/static/chunks/0c07ecbe434fdac7.js');
if (fs.existsSync(clientAttrFile)) {
  let content = fs.readFileSync(clientAttrFile, 'utf8');
  const targetO = 'o=(s=e.attributes)?Object.entries(s).map(([e,t])=>`${e}: ${"string"==typeof t?t:JSON.stringify(t)}`).join(" · "):"";';
  const replaceO = 'o=(s=e.attributes)?Object.entries(s).sort(([x],[y])=>x==="certification_status"?-1:y==="certification_status"?1:0).map(([e,t])=>e==="certification_status"?`[${t}]`: `${e}: ${"string"==typeof t?t:JSON.stringify(t)}`).join(" · "):"";';
  if (content.includes(targetO)) {
    content = content.replace(targetO, replaceO);
    console.log('[Agri-Stack UI Patch] Patched Client attribute formatting to highlight certification_status');
  }
  const targetSearchC = '||Object.values(t.display_i18n??{}).some(t=>t.toLowerCase().includes(e)):';
  const replaceSearchC = '||Object.values(t.display_i18n??{}).some(t=>t.toLowerCase().includes(e))||(t.attributes&&JSON.stringify(t.attributes).toLowerCase().includes(e)):';
  if (content.includes(targetSearchC)) {
    content = content.replace(targetSearchC, replaceSearchC);
    console.log('[Agri-Stack UI Patch] Patched Client search filter to include attributes');
  }
  fs.writeFileSync(clientAttrFile, content, 'utf8');
}


