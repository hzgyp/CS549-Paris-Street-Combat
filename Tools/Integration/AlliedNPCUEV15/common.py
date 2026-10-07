"""Exact611-row epoch and explicitly selected project-descriptor epoch."""
import json
import sys
import importlib.util
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'AlliedNPCGripV2'))
spec=importlib.util.spec_from_file_location('allied_v14_common',Path(__file__).resolve().parents[1]/'AlliedNPCGripV2/common.py')
prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
ROOT,STORE,GRIP,checkpoint,read,write,sha=(prior.ROOT,prior.STORE,prior.BASE,prior.checkpoint,prior.read,prior.write,prior.sha)
BASE=STORE/'Evidence/AlliedNPCUEV15'
PLUGIN=ROOT/'Unreal/ParisStreetCombat/Plugins/ParisNPCGripV15'
DESCRIPTOR=ROOT/'Unreal/ParisStreetCombat/WW2FranceLiberation.uproject'
CONFIG=BASE/'preflight_v1/binding.json'
PACKAGE='/Game/ParisCombat/Animation/AlliedGripV15/ABP_PC_AlliedGripPostV15'
DATA='/Game/ParisCombat/Animation/AlliedGripV15/DA_PC_AlliedGripV15'

def guards(enabled=False):
    rows=checkpoint.guard_rows()
    assert len(rows)==611
    mismatches=[]
    for row in rows:
        p=ROOT/row['path']
        if not p.is_file() or p.stat().st_size!=row['size_bytes'] or sha(p)!=row['sha256']:
            mismatches.append(row['path'])
    assert not mismatches,mismatches
    pre_path=BASE/'preflight_v1/result.json'
    if pre_path.exists():
        pre=read(pre_path)
        actual=read(DESCRIPTOR)
        expected=pre['descriptor_json']
        if enabled:
            expected['Plugins'].append({'Name':'ParisNPCGripV15','Enabled':True})
        assert actual==expected,'Project descriptor differs from the explicitly selected epoch'
        if not enabled:
            assert sha(DESCRIPTOR)==pre['descriptor_sha256'],'Original descriptor bytes must be exact'
    return len(rows)

if __name__=='__main__':print('current guards',guards('--enabled' in sys.argv))
