"""Read-only input/guard verification and a private local-review receipt."""
import hashlib
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
BASE=STORE/'Evidence/LeftSupportV20'
OUT=BASE/'verification_v1'
assert not OUT.exists(), 'Preserve occupied verification identity'
OUT.mkdir()
(OUT/'source.py').write_bytes(Path(__file__).read_bytes())
sys.path.insert(0,str(ROOT/'Tools/Integration/NPCInteractionV1'))
from common import guard_rows,guards_match

def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def exact(row):
    p=ROOT/row['path']
    return p.is_file() and p.stat().st_size==row['size_bytes'] and sha(p)==row['sha256']

cfg=read(BASE/'config_verification_v1/result.json')
native=read(BASE/'native_review_v1/result.json')
boundary=read(BASE/'skin_boundary_verification_v1/result.json')
provenance=read(BASE/'rotation_provenance_v1/result.json')
exitrow=read(ROOT/'tmp/left-support-v20/native_review_v1.log.exit.json')
assert not native['errors'] and native['guards_after_match'] and native['one_original_reload_conserved']
assert exitrow['pid']==native['pid'] and exitrow['exit_code']==0 and not exitrow['timed_out']
assert boundary['local_boundary_pass'] and not boundary['new_crossing_faces']
assert sha(BASE/'reuse_pose_v2/binding.json')==cfg['config_sha256']
assert sha(STORE/'Evidence/GripBindingV18/config_v1/binding.json')==cfg['baseline_config_sha256']
v19=read(STORE/'Evidence/FPUpperBodyV19/verification_v1/result.json')
plugin=[row for row in v19['files'] if '/Plugins/ParisGripBindingV18/' in row['path']]
assert plugin and all(exact(row) for row in plugin) and exact(v19['accepted_source'])
rows=guard_rows();assert guards_match(rows)
mapfile=STORE/'Content/ParisCombat/Maps/LV_ParisStreetCombat_V1.umap'
assert sha(mapfile)=='2791b4a7f76b4b3d07f42286b6ad0156c3a185c2e3e795fa2446aaac0ad68519'
ready=[s for s in native['samples'] if s['action']=='Ready' and s['holding_alpha']>.9999]
receipt={
    'status':'V20_left_thumb_approach_improved_local_native_regression_recorded_human_review_pending',
    'guard_count':len(rows),'all_guards_match':True,'map_sha256':sha(mapfile),
    'accepted_source_and_original_runtime_match':True,
    'config_sha256':cfg['config_sha256'],'baseline_config_sha256':cfg['baseline_config_sha256'],
    'existing_pose_phase_s':provenance['phase_s'],
    'source_quaternion_provenance_max_error_degrees':max(provenance['quaternion_errors_degrees'].values()),
    'native_pid':native['pid'],'native_exit_code':exitrow['exit_code'],
    'native_last_observed_updates':native['samples'][-1]['native_updates'],
    'ready_finger_max_error_degrees':max(max(s['finger_errors_degrees'].values()) for s in ready),
    'unchanged_native_finger_max_error_degrees':max(max(s['unchanged_finger_errors_degrees'].values()) for s in native['samples']),
    'paired_gun_max_delta_cm':max(s['gun_pair_delta_cm'] for s in native['samples']),
    'paired_left_wrist_max_delta_cm':max(s['left_wrist_pair_delta_cm'] for s in native['samples']),
    'left_walk_speed_cm_s':next(s['speed_cm_s'] for s in native['samples'] if s['name']=='candidate_left_walk'),
    'reload_before':native['reload_before']['ammo'],'reload_after':native['samples'][-1]['ammo'],
    'one_original_reload_conserved':native['one_original_reload_conserved'],
    'static_mean_pad_gap_cm':read(BASE/'reuse_pose_v2/result.json')['remaining_mean_pad_gap_cm'],
    'all_thumb_influence_boundary':boundary,
    'actual_native_images_inspected':[c['file'] for c in native['captures']],
    'visual_note':'Thumb turns toward wooden fore-end instead of splaying; fine clearance remains. Mid/post reload sleeve sheets persist and are deliberately deferred.',
    'full_grasp_accepted':False,'human_review_pending':True,
    'full_return_lifecycle_nearwall_fps_measured':False,
    'selected_formal':False,'native_asset_authored':False,'deleted_old_assets':False,
    'catalog_release_commit_push':False,
}
(OUT/'result.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k!='all_thumb_influence_boundary'}))
