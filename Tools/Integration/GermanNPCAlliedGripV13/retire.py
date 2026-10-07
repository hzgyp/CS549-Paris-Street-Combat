"""Record explicit rejection; verify previous baseline, without model rollback."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'GermanNPCGripV1'))
from common import ROOT,STORE,GLB,read,write,row,sha,guards
BASE=STORE/'Evidence/GermanNPCAlliedGripV13';OUT=BASE/'retired_by_user_v1'
BASELINE=STORE/'Evidence/GermanNPCLowerGripV11/source_frame_v4/result.json'
VIEW=STORE/'Evidence/GermanNPCLowerGripV11/frame_failure_views_v1/result.json'
GEOMETRY=VIEW.parent/'diagnostic_geometry.npz'
SOURCE=STORE/'Evidence/GermanNPCOrderedGripV4/offline_v6/geometry.npz'
assert not OUT.exists()
probe=read(BASE/'probe_v1/result.json')
for p in (BASELINE,GLB,SOURCE):
    old=next(e for e in probe['inputs'] if e['path']==p.relative_to(ROOT).as_posix())
    assert row(p)==old,p
assert not read(VIEW)['errors']
write(OUT/'result.json',{'status':'user_rejected_v13_resume_previous_german_v11_visual_baseline',
  'guards_exact':guards(),'baseline':[row(p) for p in (BASELINE,VIEW,GEOMETRY,SOURCE,GLB)],
  'selection':'V11 human visually accepted thumb/lower-three, not V12/V13',
  'raw_v11_numerical_failures_retained':True,'formal_german_remains_unarmed':True,
  'source_rollback_needed':False,'formal_asset_changed':False,'v13_selected':False,
  'new_fit_performed':False,'failure_evidence_preserved':True,
  'instructions':row(Path(__file__).with_name('RETIRED.md'))})
print('V13 retired; previous V11/model hashes exact;618 guards exact; no source/formal rollback needed')
