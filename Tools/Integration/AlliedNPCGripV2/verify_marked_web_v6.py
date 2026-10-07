"""Fresh read of the completed unsaved comparison; no engine/model edits."""
import math
from common import BASE,ROOT,read,write,sha,guards
import transform_math as tm
out=BASE/'marked_web_v6'
r=read(out/'result.json')
assert r['status']=='marked_web_v6_native_views_require_user_review' and not r['errors']
assert r['guards_before']==r['guards_after']==611 and r['inputs_unchanged']
assert all(sha(ROOT/p)==h for p,h in r['input_hashes'].items())
assert r['original']['bones']==r['before']['bones']==r['seated']['bones']==r['after']['bones']
assert r['original']['gun_world']['s']==r['after']['gun_world']['s']==[1,1,1]
assert r['actual_pivot_drift_cm']<.01 and len(r['captures'])==10
assert all(c['gun_drift_cm']<.01 for c in r['captures'])
hand=r['after']['bones']['hand_r']
gun=r['after']['gun_world']
relative={'t':tm.inverse_point(hand,gun['t']),'q':tm.local_q(hand,gun),
          's':[gun['s'][i]/hand['s'][i] for i in range(3)]}
assert math.dist(tm.point(hand,relative['t']),gun['t'])<1e-6
assert tm.angle(tm.qmul(hand['q'],relative['q']),gun['q'])<.01
records=[{'file':c['file'],'sha256':sha(out/c['file'])} for c in r['captures']]
v={'guards':guards(),'engine_exit_code_recorded':0,'all_character_bones_exact':True,
   'candidate_gun_relative_to_hand_r_cm_xyzw':relative,'native_images':records,
   'full_contact_accepted':False,'formal_selected':False}
dest=out/'verification.json'
assert not dest.exists()
write(dest,v)
print('Fresh exact read:',v['guards'],'guards;',len(records),'native images; no adoption')
