"""Preserve and record human-saved changes, never restore/select/publish them."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
OUT=STORE/'Evidence/ReloadIndexContactV6/preflight_v1'
assert not OUT.exists(),'Preserve occupied evidence'
OUT.mkdir(parents=True)
(OUT/'source.py').write_bytes(Path(__file__).read_bytes())
rows=json.loads((STORE/'Evidence/ReloadRepairV5/checkpoint_v1/guards.json').read_text())['files']
rows+=json.loads((ROOT/'Docs/Development/NPCInteractionV1/NPC_INTERACTION_V1_DRAFT_INVENTORY_20261004.json').read_text())['files']
assert len(rows)==528 and len({r['path'] for r in rows})==528
current=[];changed=[]
for row in rows:
    p=ROOT/row['path'];now=dict(row)
    now.update(size_bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
    current.append(now)
    if (now['size_bytes'],now['sha256'])!=(row['size_bytes'],row['sha256']):
        changed.append({'before':row,'after':now,'resolved_physical_path':str(p.resolve())})
expected={
 'Unreal/ParisStreetCombat/Content/ParisCombat/Maps/LV_ParisStreetCombat_V1.umap':'de39b998d97cc992454db9dbd91b9f3b96bf304e2164a17375a170c9817a305a',
 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Content/ParisCombat/Maps/LV_ParisStreetCombat_V1.umap':'de39b998d97cc992454db9dbd91b9f3b96bf304e2164a17375a170c9817a305a',
 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Content/ParisCombat/Blueprints/PlayerActionsV1/BP_PCParisPlayerActionsV6.uasset':'572a0d9929ad65aa6fec0b206960524979314e1591eeaec27af2e75e8f22fbe8'}
assert {c['after']['path']:c['after']['sha256'] for c in changed}==expected
result={'scope':__doc__,'status':'known_human_save_recorded_not_adopted',
 'files':current,'changed_guard_records':changed,'current_count':528,
 'unchanged_old_record_count':525,'changed_physical_count':len({c['resolved_physical_path'] for c in changed}),
 'map_selection':False,'catalog_or_old_inventory_modified':False,'native_modified':False}
(OUT/'result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('files','changed_guard_records')}))
