"""Fresh native transform, contact provenance, private inputs and image checks."""
import argparse,math
from PIL import Image
from common import *
import transform_math as tm
parser=argparse.ArgumentParser();parser.add_argument('identity');args=parser.parse_args()
out=BASE/args.identity;n=read(out/'result.json');t=read(BASE/'trigger_pad_v10d/result.json')
assert n['status']=='trigger_fit_v10_native_views_require_user_review' and not n['errors']
assert t['status']=='trigger_pad_v10d_local_geometry_pass' and t['contact_gate_passed']
assert n['frozen_diagnostic_only'] and n['diagnostic_component_native_refresh_while_paused']
assert not n['fp_binding_called'] and not n['original_npc_driver_changed']
assert not n['map_saved'] and not n['formal_selected'] and not t['v8_translation_consumed']
assert sum(t['final_contact']['digits']['index'].values())==0
assert t['final_contact']['actual_pad_to_blade_cm']<=.15
assert t['preservation']['new_severe_edges']==0
for r in (n,t,read(BASE/'pivot_raise_measure_v7/result.json')):
    assert r['inputs_unchanged'] and not r['errors']
    assert r['guards_before']==r['guards_after']==guards()==611
    assert all(sha(ROOT/p)==h for p,h in r['input_hashes'].items())
assert read(out/'early_acceptance.json')['accepted']
assert len(n['captures'])==12
images=[]
for capture in n['captures']:
    p=out/capture['file'];im=Image.open(p);im.load();assert im.size==(1600,1000)
    assert capture['gun_drift_cm']<.01
    assert capture['pose_parity']['max_bone_position_cm']<.01
    assert capture['pose_parity']['max_bone_rotation_deg']<.01
    images.append({'path':p.name,'sha256':sha(p),'size_bytes':p.stat().st_size})
assert len({i['sha256'] for i in images})>=11
b,a=n['before']['bones'],n['after']['bones']
protected=set(t['bone_names'])-set(t['allowed_bones'])
pos=max(math.dist(b[j]['t'],a[j]['t']) for j in protected)
rot=max(tm.angle(b[j]['q'],a[j]['q']) for j in protected)
assert pos<.001 and rot<.01
gun=n['after']['gun_world']
assert math.dist(gun['t'],t['after_gun_world']['t'])<.001
assert tm.angle(gun['q'],t['after_gun_world']['q'])<.01
angle=tm.angle(n['before']['gun_world']['q'],gun['q'])
assert abs(angle-t['additional_angle_deg'])<.01
actual_pivot=tm.point(gun,t['pivot_gun_cm'])
goal=[a+b for a,b in zip(t['pivot_world_cm'],t['pivot_displacement_world_cm'])]
pivot_error=math.dist(actual_pivot,goal);assert pivot_error<.001
write(out/'verification.json',{'guards':611,'all_retained_inputs_exact':True,'images':images,
    'protected_native_position_cm':pos,'protected_native_rotation_deg':rot,
    'actual_native_additional_angle_deg':angle,'marked_pivot_goal_error_cm':pivot_error,
    'local_index_geometry_gate_passed':True,'actual_pad_to_blade_cm':t['final_contact']['actual_pad_to_blade_cm'],
    'index_crossing_faces':t['final_contact']['digits']['index'],
    'all_grip_motion_gameplay_accepted':False,'formal_selected':False})
print({'guards':611,'images':len(images),'protected_cm':pos,'angle_deg':angle,'pivot_goal_error_cm':pivot_error,'local_index_gate':True})
