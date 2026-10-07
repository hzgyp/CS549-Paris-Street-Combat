"""Fresh native single-tip delta, zero protected/gun delta and current guards."""
import argparse,math
from PIL import Image
from common import *
import transform_math as tm
parser=argparse.ArgumentParser();parser.add_argument('identity');args=parser.parse_args()
out=BASE/args.identity;n=read(out/'result.json');t=read(BASE/'tip_curl_v12/result.json')
assert n['status']=='tip_curl_v12_native_comparison_requires_review' and not n['errors']
assert t['comparison_only'] and t['comparison_gate_passed'] and not t['errors']
assert n['frozen_diagnostic_only'] and n['diagnostic_component_native_refresh_while_paused']
assert not n['fp_binding_called'] and not n['original_npc_driver_changed'] and not n['map_saved'] and not n['formal_selected']
for row in (n,t):
    assert row['inputs_unchanged'] and row['guards_before']==row['guards_after']==guards()==611
    assert all(sha(ROOT/p)==h for p,h in row['input_hashes'].items())
assert read(out/'early_acceptance.json')['accepted'] and len(n['captures'])==12
images=[]
for capture in n['captures']:
    p=out/capture['file'];im=Image.open(p);im.load();assert im.size==(1600,1000)
    assert capture['gun_drift_cm']<.01 and capture['pose_parity']['max_bone_position_cm']<.01 and capture['pose_parity']['max_bone_rotation_deg']<.01
    images.append({'path':p.name,'sha256':sha(p),'size_bytes':p.stat().st_size})
assert len({row['sha256'] for row in images})==12
b,a=n['before']['bones'],n['after']['bones'];protected=set(t['bone_names'])-{'index_03_r'}
pos=max(math.dist(b[j]['t'],a[j]['t']) for j in protected);rot=max(tm.angle(b[j]['q'],a[j]['q']) for j in protected)
assert pos<.001 and rot<.01
gun=n['after']['gun_world'];old=n['before']['gun_world'];gunpos=math.dist(old['t'],gun['t']);gunrot=tm.angle(old['q'],gun['q'])
assert gunpos<.001 and gunrot<.01 and t['before_gun_world']==t['after_gun_world']
curl=tm.angle(tm.local_q(b['index_02_r'],b['index_03_r']),tm.local_q(a['index_02_r'],a['index_03_r']))
assert abs(curl-t['additional_curl_deg'])<.01
write(out/'verification.json',{'guards':611,'all_retained_inputs_exact':True,'images':images,
    'protected_native_position_cm':pos,'protected_native_rotation_deg':rot,
    'gun_position_change_cm':gunpos,'gun_angle_change_deg':gunrot,'additional_existing_tip_curl_deg':curl,
    'total_existing_tip_curl_deg':t['total_curl_deg'],'local_index_contact_gate_passed':t['contact_gate_passed'],
    'index_crossing_faces':t['final_contact']['digits']['index'],'comparison_only':True,'formal_selected':False})
print({'guards':611,'images':len(images),'protected_cm':pos,'gun_cm':gunpos,'additional_curl_deg':curl,'index_contact':t['final_contact']['digits']['index']})
