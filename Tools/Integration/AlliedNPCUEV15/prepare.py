"""Derive accepted V14 rotations; never copy unrelated idle-phase locals."""
import math
from common import *
import transform_math as tm
OUT=BASE/'preflight_v1'
assert not OUT.exists()
guards()
source=GRIP/'fp_wrist_native_v14/result.json'
native=read(source)
assert native['guards_after']==611 and not native['errors']
parents=read(GRIP/'pivot_raise_measure_v7/result.json')['parents']
old=native['original']['bones'];accepted=native['after']['bones']
names=['upperarm_l','lowerarm_l','hand_l','lowerarm_twist_01_l','upperarm_twist_01_l',
       'upperarm_r','lowerarm_r','hand_r','lowerarm_twist_01_r','upperarm_twist_01_r','index_03_r']
rules=[]
for n in names:
    before=tm.local_q(old[parents[n]],old[n]);after=tm.local_q(accepted[parents[n]],accepted[n])
    delta=tm.qmul(after,tm.qinv(before))
    assert tm.angle(tm.qmul(delta,before),after)<.0001
    rules.append({'bone':n,'delta':delta,'source_q':before,'accepted_q':after,
        'angle_degrees':tm.angle(before,after)})
hand=accepted['hand_r'];gun=native['after']['gun_world']
relative={'t':tm.inverse_point(hand,gun['t']),'q':tm.local_q(hand,gun),
          's':[gun['s'][i]/hand['s'][i] for i in range(3)]}
assert math.dist(tm.point(hand,relative['t']),gun['t'])<1e-8
cfg={'schema':1,'source_mesh':native['original']['mesh'],'rules':rules,'gun_hand_relative':relative,
     'origin':'Human accepted actual Allied NPC V14, not first-person offsets',
     'source_record_sha256':sha(source),'scope':'rotation-only existing-action postprocess',
     'known_index_blade_crossings':10}
write(CONFIG,cfg)
write(OUT/'result.json',{'guards':611,'source':source.relative_to(ROOT).as_posix(),
    'source_sha256':sha(source),'binding_sha256':sha(CONFIG),'descriptor_sha256':sha(DESCRIPTOR),
    'descriptor_json':read(DESCRIPTOR),'descriptor_original_text':DESCRIPTOR.read_text(),
    'all_guard_rows':checkpoint.guard_rows(),'rules':len(rules),'source_motion_changed':False,
    'selected':False,'known_contact_limitation_retained':True})
print('Prepared11 accepted rotation differences and original gun-hand transform;611 exact')
