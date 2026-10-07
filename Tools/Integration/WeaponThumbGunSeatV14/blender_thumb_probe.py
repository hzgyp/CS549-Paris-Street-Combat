"""Read-only fixed-thumb and stock surface measurement before V14 gun fitting."""
import sys
import hashlib
import traceback
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'WeaponTriggerPivotV12'))
from pivot_common import *

PROBE = STORE / 'Evidence/WeaponTriggerPivotV12/landmarks_v1/result.json'
PREVIOUS = STORE / 'Evidence/WeaponTriggerPivotV13/pivot_20deg_v1b/result.json'
OUT = STORE / 'Evidence/WeaponThumbGunSeatV14/surface_probe_v1'
assert not OUT.exists()
OUT.mkdir(parents=True)
r = {'errors': [], 'native_authored': False, 'hand_or_gun_authored': False}
inputs = [FBX, POSES, AUDIT, CALIB, TOPOLOGY, INDEX, PROBE, PREVIOUS, Path(__file__)]
hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
try:
    r['guards_before'] = guarded_files()
    assert not r['guards_before']['mismatches']
    d = load()
    p = json.loads(PROBE.read_text())
    bones = {n: np.array(v) for n, v in p['baseline_component_bones'].items()}
    gun = np.array(p['baseline_gun_component_matrix'])
    skin_points = evaluate(d, bones, gun)
    thumb_ids = np.flatnonzero(d['digits']['thumb'])
    thumb_faces = np.flatnonzero(np.all(d['digits']['thumb'][d['tri']], axis=1))
    wood_ids = np.array(next(c for c in d['topo']['components'] if c['id'] == 0)['triangle_ids'], int)
    r.update(thumb_vertex_ids=thumb_ids.tolist(), thumb_triangle_ids=thumb_faces.tolist(),
             thumb_points_cm=skin_points[thumb_ids].tolist(),
             thumb_range_cm=[skin_points[thumb_ids].min(0).tolist(), skin_points[thumb_ids].max(0).tolist()],
             thumb_bones_gun_cm={n: transform(bones[n][None,:3,3], np.linalg.inv(gun))[0].tolist()
                                 for n in ('thumb_01_r','thumb_02_r','thumb_03_r')},
             stock_points_cm=d['gp'][np.unique(d['gt'][wood_ids])].tolist(),
             stock_triangle_ids=wood_ids.tolist(),
             stock_triangles=d['gt'][wood_ids].tolist())
    r['status'] = 'read_only_surface_measurement_complete'
except Exception:
    r['errors'].append(traceback.format_exc())
finally:
    r['input_hashes'] = hashes
    r['inputs_unchanged'] = all(hashlib.sha256((ROOT/k).read_bytes()).hexdigest() == v for k,v in hashes.items())
    (OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:r.get(k) for k in ('status','errors','thumb_range_cm','thumb_bones_gun_cm','inputs_unchanged')}))
