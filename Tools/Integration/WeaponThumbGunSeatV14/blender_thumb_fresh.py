"""Independent fresh read of V14 frozen diagnostic geometry, not a playable rig."""
import hashlib
import sys
import traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'WeaponTriggerPivotV12'))
from pivot_common import *

BASE = STORE/'Evidence/WeaponThumbGunSeatV14'
SOURCE = BASE/'thumb_seat_v1'
OUT = BASE/'fresh_check_v1'
assert not OUT.exists()
OUT.mkdir(parents=True)
blend = SOURCE/'FixedHandThumbSeat.blend'
inputs = [blend,SOURCE/'result.json',FBX,POSES,AUDIT,INDEX,Path(__file__)]
hashes = {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
r = {'errors':[],'native_authored':False}
try:
    proof = json.loads((SOURCE/'result.json').read_text())
    assert not proof['errors']
    d = load()
    bones = {n:np.array(v) for n,v in proof['candidate_component_bones'].items()}
    expected = evaluate(d,bones,np.array(proof['baseline_gun_component_matrix']))
    expected_gun = transform(d['gp'],np.array(proof['rigid_change_gun_local']))
    bpy.ops.wm.open_mainfile(filepath=str(blend))
    errors = {}
    for name,target in [('Fixed right thumb_seated',expected),('Support thumb_seated',expected),
                        ('Continuous arms thumb_seated',expected),('Rifle thumb_seated',expected_gun)]:
        obj = bpy.data.objects[name]
        actual = np.array([list(obj.matrix_world@v.co) for v in obj.data.vertices])*100
        errors[name] = float(np.max(np.linalg.norm(actual-target,axis=1)))
        assert errors[name]<.0001,name
    r.update(status='fresh_static_geometry_read_passed',saved_geometry_max_errors_cm=errors,
             source_armature_bones=len(next(o for o in bpy.data.objects if o.type=='ARMATURE').data.bones),
             limitation='Static geometry verification does not override failed overall seating/trigger/continuity checks.')
except Exception:
    r['status'] = 'stopped'
    r['errors'].append(traceback.format_exc())
finally:
    r['input_hashes'] = hashes
    r['inputs_unchanged'] = all(hashlib.sha256((ROOT/k).read_bytes()).hexdigest()==v for k,v in hashes.items())
    (OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(r))
