"""Read source bone evidence; store statistics privately, not pose data in Git."""
import json,math,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/'GripBindingV18'))
from common import STORE,guard
BASE=STORE/'Evidence/FPUpperBodyV19'
p=BASE/sys.argv[1]/'result.json';r=json.loads(p.read_text())
assert not r['errors'] and r['status']=='existing_component_bones_sampled'
assert r['source_inputs_unchanged'] and not r['guards_after']['mismatches']
assert r.get('max_phase_hand_shift_cm',0)>.01,'No valid native pose refresh evidence'
def angle(a,b):
    dot=abs(sum(x*y for x,y in zip(a,b))/math.sqrt(sum(x*x for x in a)*sum(x*x for x in b)))
    return math.degrees(2*math.acos(min(1.,dot)))
def stats(rows,bone,space):
    t=[x[space][bone]['t'] for x in rows];q=[x[space][bone]['q'] for x in rows]
    return {'min_cm':[min(v[i] for v in t) for i in range(3)],'max_cm':[max(v[i] for v in t) for i in range(3)],
            'span_cm':[max(v[i] for v in t)-min(v[i] for v in t) for i in range(3)],
            'max_pair_rotation_degrees':max(angle(a,b) for a in q for b in q)}
out={'source_probe':str(p),'clip_statistics':{},'guards':guard(),'repair_authorized':False}
for name in sorted(set(x['clip'] for x in r['samples'])):
    rows=[x for x in r['samples'] if x['clip']==name]
    out['clip_statistics'][name]={sp:{b:stats(rows,b,sp) for b in rows[0][sp]} for sp in ('component','local')}
assert not out['guards']['mismatches']
target=BASE/('source_analysis_'+sys.argv[1]);assert not target.exists();target.mkdir()
(target/'result.json').write_text(json.dumps(out,indent=2)+'\n')
for clip,s in out['clip_statistics'].items():
    print(clip,'component hand span',s['component']['hand_r']['span_cm'],'pelvis',s['component']['pelvis']['span_cm'])
    print('  local swing degrees', {b:round(s['local'][b]['max_pair_rotation_degrees'],2) for b in ['spine_01','spine_03','clavicle_r','upperarm_r','lowerarm_r','hand_r']})
