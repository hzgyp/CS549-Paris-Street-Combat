"""V3 renderer wrapper; reuse reviewed staging, not V2's rejected angle solver."""
import sys,os
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'GermanNPCGripV1'))
from common import *
proof=read(STORE/'Evidence/GermanNPCSmallPivotV3/marked_rotation_v1/result.json')
assert proof['angle_deg']==-5 and proof['whole_gun_max_vertex_displacement_cm']<8
for e in (proof['renderer_template'],proof['v2_rejected_result'],proof['v2_marking_proof']):
    assert sha(ROOT/e['path'])==e['sha256']
template=ROOT/proof['renderer_template']['path'];source_text=template.read_text(encoding='utf-8')
old_base="BASE=STORE/'Evidence/GermanNPCTriggerPivotV2'"
assert source_text.count(old_base)==1
source_text=source_text.replace(old_base,"BASE=STORE/'Evidence/GermanNPCSmallPivotV3'",1)
# Wrapper stays __file__ so the native entry records its source hash. The proof
# separately records the exact unmodified renderer template and rejected inputs.
exec(compile(source_text,str(Path(__file__)), 'exec'),globals())
