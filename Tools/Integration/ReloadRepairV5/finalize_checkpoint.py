"""Record guarded unselected drafts/evidence only. No asset moves/Catalog/Git writes."""
import hashlib,json
from pathlib import Path
from common import ROOT,STORE,records,check
OUT=STORE/'Evidence/ReloadRepairV5/checkpoint_v1';assert not OUT.exists();OUT.mkdir()
(OUT/'source.py').write_bytes(Path(__file__).read_bytes())
rows=records(True);assert len(rows)==522 and check(rows)
ids=('blend_capability_v2','transition_proof_author_v2','transition_proof_fresh_v2',
     'owner_blend_author_v1','owner_blend_city_v1','owner_reframe_author_v2','owner_reframe_city_v1',
     'sleeve_weights_offline_v2','sleeve_weights_validate_v1','sleeve_native_import_v1','sleeve_native_views_v1','sleeve_native_views_v2')
reports={i:json.loads((STORE/'Evidence/ReloadRepairV5'/i/'result.json').read_text()) for i in ids}
assert reports['sleeve_native_views_v2']['status']!='starting'
files=rows[514:];assert len(files)==8
statuses={i:{'status':r['status'],'errors':r.get('errors',[])} for i,r in reports.items()}
result={'scope':__doc__,'date':'2026-10-04','protected_count':len(rows),'protected_records_unchanged':True,
        'original_514_unchanged':True,'new_unselected_drafts':8,'statuses':statuses,
        'selection':False,'catalog_changed':False,'restore_authority':False,
        'formal_map_sha256':'2791b4a7f76b4b3d07f42286b6ad0156c3a185c2e3e795fa2446aaac0ad68519'}
(OUT/'guards.json').write_text(json.dumps({'files':rows},indent=2)+'\n')
(OUT/'result.json').write_text(json.dumps(result,indent=2)+'\n')
inventory=ROOT/'Assets/Integration/RELOAD_REPAIR_V5_DRAFT_INVENTORY_20261004.json';assert not inventory.exists()
inventory.write_text(json.dumps({'schema_version':1,'scope':'Local unselected reload V5 diagnostic drafts; not Catalog/teammate automatic restore authority',
    'date':'2026-10-04','selected':False,'files':files,'original_protected_count':514,'combined_protected_count':522,
    'guard_snapshot':str((OUT/'guards.json').relative_to(ROOT)).replace('\\','/'),
    'result':str((OUT/'result.json').relative_to(ROOT)).replace('\\','/'),
    'stopped_owners':['BP_PCReloadOwnerBlendV5','BP_PCReloadOwnerReframeV5'],
    'private_only':True,'commercial_native_bytes_in_git':False},indent=2)+'\n')
print(json.dumps({k:result[k] for k in ('protected_count','original_514_unchanged','new_unselected_drafts')}))
