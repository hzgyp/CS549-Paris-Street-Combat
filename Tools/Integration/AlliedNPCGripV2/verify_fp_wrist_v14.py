"""Fresh actual native fixed-gun/hand/digit and original-length arm parity."""
import argparse,math
from PIL import Image
from common import *
import transform_math as tm
parser=argparse.ArgumentParser();parser.add_argument('identity');args=parser.parse_args()
out=BASE/args.identity;n=read(out/'result.json');t=read(BASE/'fp_wrist_v14/result.json')
assert n['status']=='fp_wrist_v14_native_comparison_requires_review' and not n['errors']
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
gunpos=math.dist(n['before']['gun_world']['t'],n['after']['gun_world']['t']);gunrot=tm.angle(n['before']['gun_world']['q'],n['after']['gun_world']['q'])
assert gunpos<.001 and gunrot<.01
digits={};lengths={}
for j in t['bone_names']:
    if not j.startswith(('index_','thumb_','middle_','ring_','pinky_')):continue
    parent=t['parents'][j];digits[j]=tm.angle(tm.local_q(b[parent],b[j]),tm.local_q(a[parent],a[j]));assert digits[j]<.01
for first,last in (('upperarm_r','lowerarm_r'),('lowerarm_r','hand_r')):
    lengths[first]=abs(math.dist(b[first]['t'],b[last]['t'])-math.dist(a[first]['t'],a[last]['t']));assert lengths[first]<.001
def bend(bones):
    v=[bones['hand_r']['t'][i]-bones['lowerarm_r']['t'][i] for i in range(3)];h=tm.rotate(bones['hand_r']['q'],[-1,0,0])
    return math.degrees(math.acos(max(-1,min(1,sum(x*y for x,y in zip(v,h))/math.sqrt(sum(x*x for x in v)*sum(x*x for x in h))))))
angles=[bend(b),bend(a)];assert angles[1]<angles[0]-15
assert a['lowerarm_r']['t'][2]<=a['upperarm_r']['t'][2]+.001
assert t['baseline_contact']==t['final_contact']
write(out/'verification.json',{'guards':611,'all_retained_inputs_exact':True,'images':images,
    'protected_native_position_cm':pos,'protected_native_rotation_deg':rot,'gun_position_cm':gunpos,'gun_rotation_deg':gunrot,
    'max_native_digit_local_rotation_error_deg':max(digits.values()),'native_segment_length_errors_cm':lengths,
    'forearm_hand_axis_before_after_deg':angles,'digit_contact_counts_unchanged':True,
    'comparison_only':True,'formal_selected':False,'contact_or_gameplay_accepted':False})
print({'guards':611,'images':len(images),'protected_cm':pos,'gun_cm':gunpos,'digit_angle':max(digits.values()),'angles':angles})
