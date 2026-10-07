"""Fresh native matching transforms; no whole contact or animation acceptance."""
import argparse,math
from PIL import Image
from common import *
import transform_math as tm
parser=argparse.ArgumentParser();parser.add_argument('identity');args=parser.parse_args()
out=BASE/args.identity;n=read(out/'result.json');t=read(BASE/'index_curl_v11e/result.json')
assert n['status']=='index_curl_v11_native_comparison_contact_failed' and not n['errors']
assert t['comparison_only'] and not t['contact_gate_passed'] and not t['errors']
assert n['frozen_diagnostic_only'] and n['diagnostic_component_native_refresh_while_paused']
assert not n['fp_binding_called'] and not n['original_npc_driver_changed'] and not n['map_saved'] and not n['formal_selected']
assert t['preservation']['new_severe_edges']==t['preservation']['new_index_neighbor_self_pairs']==0
for r in (n,t):
    assert r['inputs_unchanged'] and r['guards_before']==r['guards_after']==guards()==611
    assert all(sha(ROOT/p)==h for p,h in r['input_hashes'].items())
assert read(out/'early_acceptance.json')['accepted'] and len(n['captures'])==12
images=[]
for capture in n['captures']:
    p=out/capture['file'];im=Image.open(p);im.load();assert im.size==(1600,1000)
    assert capture['gun_drift_cm']<.01 and capture['pose_parity']['max_bone_position_cm']<.01 and capture['pose_parity']['max_bone_rotation_deg']<.01
    images.append({'path':p.name,'sha256':sha(p),'size_bytes':p.stat().st_size})
b,a=n['before']['bones'],n['after']['bones'];protected=set(t['bone_names'])-set(t['allowed_bones'])
pos=max(math.dist(b[j]['t'],a[j]['t']) for j in protected);rot=max(tm.angle(b[j]['q'],a[j]['q']) for j in protected)
assert pos<.001 and rot<.01
gun=n['after']['gun_world'];old=n['before']['gun_world']
assert math.dist(gun['t'],t['after_gun_world']['t'])<.001 and tm.angle(gun['q'],t['after_gun_world']['q'])<.01
angle=tm.angle(old['q'],gun['q']);distance=math.dist(old['t'],gun['t'])
assert angle<.01 and abs(distance-.4)<.001
curl=tm.angle(tm.local_q(b['index_02_r'],b['index_03_r']),tm.local_q(a['index_02_r'],a['index_03_r']))
assert abs(curl-t['curl_degrees'])<.01
write(out/'verification.json',{'guards':611,'all_retained_inputs_exact':True,'images':images,
    'protected_native_position_cm':pos,'protected_native_rotation_deg':rot,'gun_retreat_cm':distance,
    'gun_angle_change_deg':angle,'index03_existing_curl_deg':curl,'local_index_contact_gate_passed':False,
    'index_crossing_faces':t['final_contact']['digits']['index'],'comparison_only':True,
    'all_grip_motion_gameplay_accepted':False,'formal_selected':False})
print({'guards':611,'images':len(images),'protected_cm':pos,'gun_retreat_cm':distance,'curl_deg':curl,'contact_accepted':False})
