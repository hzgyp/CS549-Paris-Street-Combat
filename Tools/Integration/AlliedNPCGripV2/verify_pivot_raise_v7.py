"""Fresh current-epoch/hash/native-transform/image verification; no repair."""
import argparse
import math
from PIL import Image
from common import *
import transform_math as tm
parser=argparse.ArgumentParser();parser.add_argument('identity');args=parser.parse_args()
out=BASE/args.identity
native=read(out/'result.json');trial=read(BASE/'pivot_raise_trial_v7/result.json')
measurement=read(BASE/'pivot_raise_measure_v7/result.json')
assert native['status']=='pivot_raise_v7_native_views_require_user_review' and not native['errors']
assert native['frozen_diagnostic_only'] and not native['formal_selected'] and not native['map_saved']
assert native['diagnostic_component_native_refresh_while_paused'] and not native['fp_binding_called']
assert native['guards_before']==native['guards_after']==guards()==611
for record in (native,trial,measurement):
    assert record['inputs_unchanged'] and not record['errors']
    assert all(sha(ROOT/p)==h for p,h in record['input_hashes'].items())
    assert record['guards_before']==record['guards_after']==611
assert len(native['captures'])==11
images=[]
for c in native['captures']:
    p=out/c['file'];im=Image.open(p);im.load();assert im.size==(1600,1000)
    assert c['gun_drift_cm']<.01
    assert c['pose_parity']['max_bone_position_cm']<.01
    assert c['pose_parity']['max_bone_rotation_deg']<.01
    images.append({'path':p.name,'sha256':sha(p),'size_bytes':p.stat().st_size})
assert len({i['sha256'] for i in images})>=9
protected=[n for n in trial['bone_names'] if n not in trial['allowed_bones']]
b,a=native['before']['bones'],native['after']['bones']
position=max(math.dist(b[n]['t'],a[n]['t']) for n in protected)
rotation=max(tm.angle(b[n]['q'],a[n]['q']) for n in protected)
pivot=tm.point(native['after']['gun_world'],measurement['pivot_gun_cm'])
drift=math.dist(pivot,trial['pivot_world_cm'])
assert position<.001 and rotation<.01 and drift<.001
blade_before=tm.point(trial['before_gun_world'],trial['blade_gun_cm'])
pad=trial['pad_world_cm'];p=trial['pivot_world_cm']
write(out/'verification.json',{'guards':611,'all_retained_inputs_exact':True,
    'protected_native_position_cm':position,'protected_native_rotation_deg':rotation,
    'actual_native_pivot_drift_cm':drift,
    'fixed_pivot_blade_radius_cm':math.dist(p,blade_before),
    'fixed_pivot_pad_radius_cm':math.dist(p,pad),
    'unavoidable_landmark_radius_difference_cm':abs(math.dist(p,blade_before)-math.dist(p,pad)),
    'images':images,'source_model_weights_actions_changed':False,
    'contact_gate_passed':trial['contact_gate_passed'],
    'complete_contact_motion_or_gameplay_accepted':False,'formal_selected':False})
print({'guards':611,'images':len(images),'protected_position_cm':position,'pivot_drift_cm':drift})
