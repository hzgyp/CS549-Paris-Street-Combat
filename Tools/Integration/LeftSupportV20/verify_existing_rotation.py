"""Independent quaternion provenance check against the retained native pose."""
import hashlib
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
BASE=STORE/'Evidence/LeftSupportV20'
OUT=BASE/'rotation_provenance_v1'
assert not OUT.exists(), 'Preserve occupied provenance identity'
OUT.mkdir()
(OUT/'source.py').write_bytes(Path(__file__).read_bytes())
cache=STORE/'Evidence/ReloadIndexContactV6/contact_exchange_v1/result.json'
assert hashlib.sha256(cache.read_bytes()).hexdigest()=='194cd91e6e6d743654ec961d6a387ec8ae3a0c318ca3f5303ac89859fec95bf1'
data=json.loads(cache.read_text())
proof=json.loads((BASE/'reuse_pose_v2/result.json').read_text())
cfg=json.loads((BASE/'reuse_pose_v2/binding.json').read_text())
chosen=proof['chosen_existing_pose']
clip=data['clips']['owner_reload']
assert clip['asset']==chosen['clip']
sample=clip['samples'][str(chosen['phase_s'])]['bones_component']

def unit(q):
    norm=math.sqrt(sum(v*v for v in q));return [v/norm for v in q]

def multiply(a,b):
    x,y,z,w=a;u,v,t,s=b
    return [w*u+x*s+y*t-z*v,w*v-x*t+y*s+z*u,w*t+x*v-y*u+z*s,w*s-x*u-y*v-z*t]

parents={'thumb_01_l':'hand_l','thumb_02_l':'thumb_01_l','thumb_03_l':'thumb_02_l'}
errors={}
for bone,parent in parents.items():
    p=unit(sample[parent]['q']);child=unit(sample[bone]['q'])
    local=unit(multiply([-p[0],-p[1],-p[2],p[3]],child))
    target=unit(cfg['fingers_local'][bone]['q'])
    dot=abs(sum(a*b for a,b in zip(local,target)))
    errors[bone]=math.degrees(2*math.acos(max(-1,min(1,dot))))
assert max(errors.values())<.001, errors
r={'status':'existing_recorded_local_rotation_provenance_verified',
   'clip':clip['asset'],'phase_s':chosen['phase_s'],
   'quaternion_errors_degrees':errors,
   'new_animation_or_angle_authored':False,
   'source_is_retained_D059_native_derivative_not_untouched_vendor':True}
(OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r))
