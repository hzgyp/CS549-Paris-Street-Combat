"""Source-backed mathematical audit of the v2 observer, not native acceptance."""
import ast,json,math
from common import BASE,config
out=BASE/'unit_bias_v1';assert not out.exists();out.mkdir()
error=json.loads((BASE/'cpp_idle_v2/result.json').read_text())['errors'][0]
raw=error.split("'actual_finger_locals': ",1)[1].split(", 'actual_support_relative_cm'",1)[0]
observed=ast.literal_eval(raw)
rows=[]
for bone,row in config()['fingers_local'].items():
    norm2=sum(q*q for q in row['q'])
    bias=math.degrees(math.acos(max(-1.,min(1.,2*norm2-1))))
    rows.append({'bone':bone,'expected_norm_squared':norm2,'predicted_unit_bias_degrees':bias,
                 'observed_degrees':observed[bone]['rotation_degrees'],'residual_degrees':abs(bias-observed[bone]['rotation_degrees'])})
r={'rows':rows,'max_bias_residual_degrees':max(x['residual_degrees'] for x in rows),
   'source':'UE5.8 Core/Public/Math/Quat.h:1228 AngularDistance uses acos(2*dot*dot-1) without normalization',
   'meaning':'All 30 reported differences explained by input norm, not proof of arbitrary rotation mismatch',
   'not_native_visual_acceptance':True,'configuration_changed':False}
assert r['max_bias_residual_degrees']<1.e-5
(out/'result.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({k:v for k,v in r.items() if k!='rows'}))
