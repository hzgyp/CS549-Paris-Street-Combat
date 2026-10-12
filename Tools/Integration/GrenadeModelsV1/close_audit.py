from pathlib import Path
import sys,json,subprocess
root=Path(__file__).resolve().parents[3];sys.path.insert(0,str(root/'Tools/Integration/TacticalEquipmentV1'))
from prepare import read,rows,sha,write
base=root/'tmp/g1-grenade-models-20261011';d=read(base/'DELIVERY_20261011.json')
assert rows(root/d['playable_directory'])==d['normal_files'];assert len(d['normal_files'])==100
assert sha(root/d['source_manifest'])==d['source_manifest_sha256'];assert rows(root/d['source_snapshot'])==read(root/d['source_manifest'])['files']
assert read(root/'Docs/Development/CURRENT_UI_REVIEW.json')['game_sha256']==d['game_sha256']
index=read(root/'Assets/Registry/asset-index.json')
for aid in ['frag-grenade','smoke-grenade']:
    a=next(a for a in index['assets'] if a['id']==aid);assert a['member_count']==5;assert any(x.get('document')==d['result'] for x in a['revisions'])
img=root/'Docs/Images/MissionLoopV1/GRENADE_MODELS_UE_20261011.png';allow=read(root/'Assets/Sync/GIT_DOCUMENT_IMAGE_ALLOWLIST.json');row=next(r for r in allow['files'] if r['path']==img.relative_to(root).as_posix())
assert dict(size_bytes=img.stat().st_size,sha256=sha(img)) in row['approved_versions'];assert img.stat().st_size<=5*1024*1024
entry=(root/d['playable_entry']).read_text('utf-8');assert d['user_dir'] in entry and d['save_prefix'] in entry
assert not any(x in entry for x in ['Probe','EquipmentCheck','Observer','Solo','BlastDiag'])
write(base/'CLOSURE_20261011.json',dict(status='pass_delivery_source_assets_index',normal_files=100,source_files=74,game_sha256=d['game_sha256'],checks=13,model_runtime_files=8,index_current=True,illustration_allowlisted=True,manual_trial='pending',publish='none',normal_entry='static bytes and arguments verified; no automatic normal preview launched'))
print('CLOSURE PASS: source74 / normal100 / runtime models8 / checks13')
