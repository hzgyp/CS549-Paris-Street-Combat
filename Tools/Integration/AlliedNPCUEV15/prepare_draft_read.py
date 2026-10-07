"""Anchor already-written draft bytes; never overwrite or create UE assets."""
from common import *

OUT=BASE/'draft_read_preflight'
assert not OUT.exists(),'Preserve previous input ledger'
assert guards(True)==611
early=read(BASE/'native_hold_v16_early/result.json')
save=read(BASE/'draft_asset_save/result.json')
fresh=read(BASE/'draft_asset_fresh/result.json')
assert not early['errors'] and save['errors'] and fresh['errors']
paths=[STORE/'Content/ParisCombat/Animation/AlliedGripV15'/name for name in
       ('ABP_PC_AlliedGripPostV16.uasset','DA_PC_AlliedGripV16.uasset')]
assert sha(paths[0])==early['candidate_abp_sha256']
write(OUT/'result.json',{'guards':611,'selected':False,'asset_written_before_registry_error':True,
    'files':[{'path':p.relative_to(ROOT).as_posix(),'size_bytes':p.stat().st_size,'sha256':sha(p)} for p in paths],
    'config_sha256':sha(BASE/'preflight_v16/binding.json'),
    'prior_receipts':{name:sha(BASE/name/'result.json') for name in ('draft_asset_save','draft_asset_fresh')}})
print('Occupied native draft anchored; no asset write')
