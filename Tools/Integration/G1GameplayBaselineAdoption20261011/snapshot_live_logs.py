"""Preserve the initial freeze and snapshot only two append-only active Editor logs."""
import hashlib
import shutil
from pathlib import Path
from manage import ROOT,OUT,PROOF,proof,write,sha
authority,plan,mapping=proof()
assert not (OUT/'retirement_initial_v1.json').exists()
shutil.copyfile(OUT/'retirement.json',OUT/'retirement_initial_v1.json')
shutil.copyfile(PROOF/'RETIREMENT_INVENTORY_20261011.json',PROOF/'RETIREMENT_INVENTORY_INITIAL_20261011.json')
names={'editor-candidate_full_v8.log','editor-candidate_full_v16-fallback.log'}
logs=[r for r in plan['protected'] if Path(r['path']).parent==ROOT/'tmp/g1-tactical-equipment-20261010' and Path(r['path']).name in names]
assert len(logs)==2
for r in logs:
    p=Path(r['path']);data=p.read_bytes()
    assert len(data)>=r['size_bytes'] and hashlib.sha256(data[:r['size_bytes']]).hexdigest()==r['sha256'], 'Log is not original prefix plus append'
    snapshot=OUT/'LiveEditorLogSnapshots'/p.name;snapshot.parent.mkdir(exist_ok=True)
    snapshot.write_bytes(data)
    r['snapshot']=dict(path=snapshot.relative_to(ROOT).as_posix(),size_bytes=len(data),sha256=sha(snapshot))
plan['protected']=[r for r in plan['protected'] if r not in logs]
plan['live_editor_logs']=logs
plan['initial_inventory_sha256']=authority['inventory_sha256']
plan['live_log_policy']='Original protected prefix exact; captured full logs exact; active Editor may append. No log is deleted.'
write(OUT/'retirement.json',plan)
authority['initial_inventory_sha256']=authority['inventory_sha256']
authority['inventory_sha256']=sha(OUT/'retirement.json')
authority['live_log_revision']='Two exact active Editor log snapshots plus unchanged original prefixes; all other guards/targets/recovery unchanged'
write(PROOF/'RETIREMENT_INVENTORY_20261011.json',authority)
print('Preserved original freeze; two exact live Editor snapshots/prefixes verified')
