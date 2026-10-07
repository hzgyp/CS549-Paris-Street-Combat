"""Record native draft closure; never select, publish, save or delete UE assets."""
from common import *

OUT=BASE/'closure_v17';assert not OUT.exists(),'Preserve occupied closure'
inventory=ROOT/'Assets/Integration/ALLIED_NPC_UE_V16_DRAFT_INVENTORY_20261006.json'
assert not inventory.exists(),'Preserve existing inventory'
assert guards(False)==611
native=read(BASE/'native_reload_lifecycle_v17/result.json')
draft=read(BASE/'draft_asset_read_v17/result.json')
assert not native['errors'] and not draft['errors']
assert not native['full_motion_gate'] and not draft['selected']
assert native['pending_initialization_frames_recorded_not_audited']==1
assert max(native['ready_local_reference_errors_deg'].values())<.01
assert native['samples'][-1]['ammo']==[8,10]
for row in draft['files']:
    p=ROOT/row['path'];assert p.stat().st_size==row['size_bytes'] and sha(p)==row['sha256']
assert sha(BASE/'preflight_v16/binding.json')==draft['config_sha256']
build=ROOT/'tmp/allied-npc-ue-v15/Build_cpp_lifecycle17'
source_files=[]
for p in sorted((PLUGIN/'Source').rglob('*')):
    if p.is_file():
        relative=p.relative_to(PLUGIN);assert sha(p)==sha(build/relative)
        source_files.append({'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)})
for p in sorted((PLUGIN/'Binaries').rglob('*')):
    if p.is_file():assert sha(p)==sha(build/p.relative_to(PLUGIN))
entries=['native_ready_v1','native_ready_v2','native_hold_v16_early',
    'native_hold_v16_motion','native_hold_v16_motion_b','native_hold_v16_audit17',
    'native_hold_v16_audit17b','native_reload_lifecycle_v17','draft_asset_save',
    'draft_asset_fresh','draft_asset_read_v17']
ledger=[]
for name in entries:
    result=read(BASE/name/'result.json')
    receipt_path=ROOT/f'tmp/allied-npc-ue-v15/{name}.log.exit.json'
    receipt=read(receipt_path)
    assert receipt['exit_code']==0 and receipt['pid']==result['pid']
    assert result['guards_after']==611
    ledger.append({'identity':name,'pid':result['pid'],'exit_code':0,
        'test_errors':len(result['errors']),'status':result['status'],
        'result_sha256':sha(BASE/name/'result.json'),'exit_receipt_sha256':sha(receipt_path)})
images=[]
for name in ('ready_right','ready_front','ready_top','ready_reverse','ready_context',
             'reload_mid_right','reload_return_right'):
    p=BASE/'native_reload_lifecycle_v17'/(name+'.png')
    assert p.is_file() and p.stat().st_size>15000
    images.append({'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),
        'inspected_by_main_agent':True})
record={'schema':1,'date':'2026-10-06','status':'native_draft_unselected',
    'engine':'UE5.8.2 Win64 Editor Development','files':draft['files'],
    'dependencies':draft['dependencies'],'private_binding_sha256':draft['config_sha256'],
    'formal_map_changed':False,'catalog_changed':False,'source_assets_changed':False,
    'first_person_changed':False,'german_changed':False,'b_ai_changed':False,
    'immutable_sftp_release_published':False,'git_commit_push_performed':False,
    'new_uasset_bytes':sum(x['size_bytes'] for x in draft['files']),
    'draft_fresh_read_verified':True,'ready_pose_verified':True,
    'walk_test_speed_cm_s':300,'reload_transaction':[ [2,16], [8,10] ],
    'full_motion_accepted':False,'pending_frames_not_validated':1,
    'remaining':['foreground full-transition/contact','unobstructed shot/muzzle/recoil',
        'near-wall','death/interruption/reset','second Allied NPC','FPS/package/second-machine',
        'dependency release audit and verified SFTP publication'],
    'descriptor_restored_sha256':sha(DESCRIPTOR),'protected_current_rows_exact':611}
write(inventory,record)
write(OUT/'visual_review.json',{'images':images,
    'observations':'No new obvious arm/cuff tear in these actual sampled views. Top/mid muzzle and context boots crop; reverse backpack obscures some contact. Existing blade10 remains, full contact and continuous motion NOT accepted.',
    'human_dynamic_acceptance':False})
write(OUT/'result.json',dict(record,owned_process_ledger=ledger,
    compiled_source_exact=source_files,inventory_sha256=sha(inventory),
    guards_after=guards(False),selected=False))
print('Native draft closure:2 exact assets/55411bytes,611 guards+original descriptor exact; unselected')
