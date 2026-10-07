"""Read-only receipts/current formal epoch check; preserve owned viewer version change."""
import sys,ast
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'GermanNPCGripV1'))
from common import ROOT,STORE,read,write,row,sha,guards
BASE=STORE/'Evidence/GermanNPCLowerGripV11';OUT=BASE/'final_check_v1'
assert not OUT.exists();OUT.mkdir(parents=True)
receipts=[BASE/v/'result.json' for v in ('mature_reuse_v1','stock_section_v2','reach_diagnosis_v1','nearest_surface_v3','frame_diagnosis_v1','source_frame_v4','failure_views_v1','frame_failure_views_v1')]
receipts.append(BASE/'frame_failure_views_v1/presentation.json')
checks=[];historical=[]
for p in receipts:
    rec=read(p)
    for e in rec.get('inputs',[]):
        actual=ROOT/e['path']
        if sha(actual)!=e['sha256']:
            assert p.parent.name=='failure_views_v1' and actual==ROOT/'Tools/Integration/GermanNPCLowerGripV11/review.py'
            frozen=ROOT/'Tools/Integration/GermanNPCLowerGripV11/review_mature_snapshot.py'
            assert sha(frozen)==e['sha256'],'Historical viewer snapshot must match original bytes'
            historical.append({'original':e,'retained_exact_snapshot':row(frozen),'reason':'Owned viewer revised for frame failure; no asset input changed'})
        else:checks.append(e)
    for e in rec.get('images',[]):assert sha(ROOT/e['path'])==e['sha256']
    if 'guards_after' in rec:assert rec['guards_after']==618 and rec['inputs_unchanged']
fit=read(BASE/'source_frame_v4/result.json')
assert fit['status']=='failed_preserved' and not fit['formal_selected'] and not fit['native_tested']
assert fit['protected_bone_matrix_error']==0 and fit['accepted_thumb_skin_cm']==0 and fit['actual_distal_index_skin_cm']==0
tools=list(Path(__file__).parent.glob('*.py'))
for p in tools:ast.parse(p.read_text(encoding='utf-8-sig'),filename=str(p))
r={'status':'failed_contact_candidate_preserved_formal_epoch_exact','guards':guards(),
   'verified_input_references':len(checks),'historical_owned_viewer_version':historical,
   'receipts':[row(p) for p in receipts],'tools':[row(p) for p in tools],
   'original_views_opened':24,'comparison_sheets_opened':3,
   'source_assets_modified':False,'formal_selected':False,'native_tested':False,
   'next_fit_requires_different_constraints_and_new_bounded_plan':True}
write(OUT/'result.json',r);print(r['status'],r['guards'],len(checks),'inputs;',len(tools),'parsed tools;',len(historical),'retained historical viewer version')
