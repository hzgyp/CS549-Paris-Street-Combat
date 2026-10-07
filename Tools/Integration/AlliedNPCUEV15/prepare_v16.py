"""New V16 mechanism config; retained V15 source/asset is never rewritten."""
from common import *
OUT=BASE/'preflight_v16';assert not OUT.exists()
guards(True)
failed=read(BASE/'native_ready_v2/result.json')
assert failed['status']=='stopped_preserved' and len(failed['samples'])==1
assert max(failed['ready_local_reference_errors_deg'].values())>3
cfg=read(CONFIG);cfg['accepted_holding']=True
cfg['scope']='Accepted local holding overlay; same-input native action release/return'
cfg['release_seconds']=.15
write(OUT/'binding.json',cfg)
write(OUT/'result.json',{'guards':611,'prior_stopped_result_sha256':sha(BASE/'native_ready_v2/result.json'),
    'v14_pose_unchanged':True,'source_motion_unchanged':True,'new_digit_fit':False,
    'original_binding_sha256':sha(CONFIG),'binding_sha256':sha(OUT/'binding.json')})
print('V16 existing accepted locals prepared,611 exact')
