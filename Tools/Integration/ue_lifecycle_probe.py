"""Read-only repeat damage/death/reset on both native Blueprint children."""
import json
import re
from pathlib import Path
import unreal

ROOT=Path(__file__).resolve().parents[2]
command=unreal.SystemLibrary.get_command_line()
identity=re.search(r'-ParisLifecycleIdentity=(\w+)(?:\s|$)',command)
OUT=ROOT/('Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/P2/Lifecycle/'+(identity.group(1) if identity else 'probe_v1')+'.json')
stride='-ParisStride=true' in command
if OUT.exists():
    raise RuntimeError('Refusing existing lifecycle probe')
report={'engine':unreal.SystemLibrary.get_engine_version(),'cases':[],
        'scope':'Fixed-step transient World; Ready/Dead only, not gunplay/reload, hit montage, AI, checkpoint or packaged acceptance'}
for name in ('BP_PCPlayerV2','BP_PCNPCV2'):
    args=['/Game/ParisCombat/Blueprints/Characters/LifecycleDraft/'+name+'.'+name+'_C']
    if stride:
        args.append('/Game/ParisCombat/Animation/DirectionalDraft/ABP_PC_'+('Allied' if name=='BP_PCPlayerV2' else 'German')+'_Stride_v1')
    case=json.loads(unreal.ParisBlueprintAuthoring.probe_lifecycle(*args))
    case['result']='pass' if all(v for c in case['cycles'] for v in c.values() if isinstance(v,bool)) else 'fail'
    report['cases'].append(case)
    OUT.write_text(json.dumps(report,indent=2),encoding='utf-8')
report['result']='pass_bounded_lifecycle' if all(c['result']=='pass' for c in report['cases']) else 'fail'
OUT.write_text(json.dumps(report,indent=2),encoding='utf-8')
assert report['result']=='pass_bounded_lifecycle', 'Inspect lifecycle probe failures'
unreal.log('CS549_LIFECYCLE_PROBE_DONE')
