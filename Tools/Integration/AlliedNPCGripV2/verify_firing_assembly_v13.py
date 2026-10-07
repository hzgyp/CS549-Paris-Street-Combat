"""Fresh actual native hand/gun/digit parity and full-source image guards."""
import argparse,math
import numpy as np
from PIL import Image
from common import *
import transform_math as tm
parser=argparse.ArgumentParser();parser.add_argument('identity');args=parser.parse_args()
out=BASE/args.identity;n=read(out/'result.json');t=read(BASE/'firing_assembly_v13/result.json')
assert n['status']=='firing_assembly_v13_native_comparison_requires_review' and not n['errors']
assert t['comparison_only'] and t['comparison_gate_passed'] and not t['errors']
assert n['frozen_diagnostic_only'] and n['diagnostic_component_native_refresh_while_paused']
assert not n['fp_binding_called'] and not n['original_npc_driver_changed'] and not n['map_saved'] and not n['formal_selected']
for row in (n,t):
    assert row['inputs_unchanged'] and row['guards_before']==row['guards_after']==guards()==611
    assert all(sha(ROOT/p)==h for p,h in row['input_hashes'].items())
assert read(out/'early_acceptance.json')['accepted'] and len(n['captures'])==15
images=[]
for c in n['captures']:
    p=out/c['file'];im=Image.open(p);im.load();assert im.size==(1600,1000)
    assert c['gun_drift_cm']<.01 and c['pose_parity']['max_bone_position_cm']<.01 and c['pose_parity']['max_bone_rotation_deg']<.01
    images.append({'path':p.name,'sha256':sha(p),'size_bytes':p.stat().st_size})
assert len({q['sha256'] for q in images})==15
b,a=n['before']['bones'],n['after']['bones'];protected=set(t['bone_names'])-set(t['allowed_bones'])
pos=max(math.dist(b[j]['t'],a[j]['t']) for j in protected);rot=max(tm.angle(b[j]['q'],a[j]['q']) for j in protected)
assert pos<.001 and rot<.01
relations={};digits={};lengths={}
for s in ('r','l'):
    beforepoint=tm.inverse_point(b['hand_'+s],n['before']['gun_world']['t'])
    afterpoint=tm.inverse_point(a['hand_'+s],n['after']['gun_world']['t'])
    angle=tm.angle(tm.local_q(b['hand_'+s],n['before']['gun_world']),tm.local_q(a['hand_'+s],n['after']['gun_world']))
    relations[s]={'position_error_cm':math.dist(beforepoint,afterpoint),'rotation_error_deg':angle}
    assert relations[s]['position_error_cm']<.001 and angle<.01
    for first,last in (('upperarm_'+s,'lowerarm_'+s),('lowerarm_'+s,'hand_'+s)):
        lengths[first]=abs(math.dist(b[first]['t'],b[last]['t'])-math.dist(a[first]['t'],a[last]['t']));assert lengths[first]<.001
for j in t['bone_names']:
    if not j.startswith(('index_','thumb_','middle_','ring_','pinky_')):continue
    parent=t['parents'][j]
    digits[j]=tm.angle(tm.local_q(b[parent],b[j]),tm.local_q(a[parent],a[j]));assert digits[j]<.01
old=tm.rotate(n['before']['gun_world']['q'],[0,1,0]);new=tm.rotate(n['after']['gun_world']['q'],[0,1,0])
elevation=[math.degrees(math.asin(q[2]/math.sqrt(sum(v*v for v in q)))) for q in (old,new)]
assert abs(elevation[1])<.01 and abs(elevation[0]-t['barrel_elevation_before_deg'])<.01
assert t['baseline_contact'].keys()==t['final_contact'].keys()
assert all(t['baseline_contact'][j]==t['final_contact'][j] for j in t['baseline_contact'] if isinstance(t['baseline_contact'][j],dict))
write(out/'verification.json',{'guards':611,'all_retained_inputs_exact':True,'images':images,
    'protected_native_position_cm':pos,'protected_native_rotation_deg':rot,'hand_relative_gun_native':relations,
    'max_native_digit_local_rotation_error_deg':max(digits.values()),'native_segment_length_errors_cm':lengths,
    'barrel_elevation_before_after_deg':elevation,'digit_contact_counts_unchanged':True,
    'comparison_only':True,'formal_selected':False,'contact_or_gameplay_accepted':False})
print({'guards':611,'images':len(images),'protected_cm':pos,'hand_gun':relations,'digit_angle':max(digits.values()),'elevation':elevation})
