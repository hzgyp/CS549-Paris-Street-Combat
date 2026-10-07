"""Explicit adoption epoch; old failure snapshots never get overwritten."""
import importlib.util
import json
import hashlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
BASE=STORE/'Evidence/AlliedNPCFormalV18'
ENTRY='/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1'
MAP=ROOT/'Unreal/ParisStreetCombat/Content/ParisCombat/Maps/LV_ParisStreetCombat_V1.umap'
DESCRIPTOR=ROOT/'Unreal/ParisStreetCombat/WW2FranceLiberation.uproject'
PLUGIN=ROOT/'Unreal/ParisStreetCombat/Plugins/ParisNPCGripV15'
DATA='/Game/ParisCombat/Animation/AlliedGripV15/DA_PC_AlliedGripV16'
GRAPH='/Game/ParisCombat/Animation/AlliedGripV15/ABP_PC_AlliedGripPostV16'
CLASS='/Game/ParisCombat/Blueprints/CityGameplayV1/BP_PCParisAlliedNPCV1'
CONFIG=STORE/'Evidence/AlliedNPCUEV15/preflight_v16/binding.json'
LABEL='PC_AlliedApprovedGripV16'

def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def row(p):return {'path':p.relative_to(ROOT).as_posix(),'size_bytes':p.stat().st_size,'sha256':sha(p)}
def exact(r):
    p=ROOT/r['path'];return p.is_file() and p.stat().st_size==r['size_bytes'] and sha(p)==r['sha256']
def guards(allow_map=False,enabled=False):
    pre=read(BASE/'preflight/result.json')
    mismatches=[r['path'] for r in pre['guards'] if not exact(r)
        and not (allow_map and (ROOT/r['path']).resolve()==MAP.resolve())]
    assert not mismatches,mismatches
    expected=pre['descriptor_json']
    if enabled:expected['Plugins'].append({'Name':'ParisNPCGripV15','Enabled':True})
    assert read(DESCRIPTOR)==expected,'Unapproved descriptor difference'
    if not enabled:assert exact(pre['descriptor'])
    assert exact(pre['config']) and all(exact(f) for f in pre['candidate_files'])
    return {'count':len(pre['guards']),'exact_other_rows':sum(1 for r in pre['guards'] if exact(r)),
        'authorized_physical_map_exception':allow_map,'candidate_exact':True}
