"""Record local, unselected player aim drafts without publishing/selecting a city."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
BASE=STORE/'Evidence/CityGameplay20261002/RifleCrosshairV4'
OUT=ROOT/'Assets/Integration/PLAYER_AIM_TRIAL_INVENTORY_20261002.json'
assert not OUT.exists(),'Preserve occupied draft inventory'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
current=json.loads((ROOT/'Assets/Integration/CITY_RIFLE_ACTION_DRAFT_INVENTORY_20261002.json').read_text())
deps=json.loads((ROOT/current['retained_dependency_inventory']).read_text())
original=current['files']+deps['files']+current['retained_unselected_rejected_trial']
files=[json.loads((BASE/n/'result.json').read_text())['saved_trial'] for n in ('author_v4','rigid_author_v1','gun_author_v1')]
assert all((ROOT/e['path']).stat().st_size==e['size_bytes'] and digest(ROOT/e['path'])==e['sha256'] for e in original+files)
r={'schema_version':1,'record_date':'2026-10-02','owner':'yg745','engine':'UE 5.8.2',
   'status':'unselected_unpublished_workspace_trials_not_catalog_or_restore_authority',
   'scope':'Existing-aim comparison and separate common upper-body/rigid gun convergence; original source motions/fingers/camera/lower body preserved',
   'active_city_checkpoint':'Assets/Integration/CITY_RIFLE_ACTION_DRAFT_INVENTORY_20261002.json',
   'active_city_unchanged':True,'current_city_or_release_selection_changed':False,
   'storage':'One physical writable Paris gameplay workspace; no immutable publication',
   'file_count':len(files),'retained_original_file_count':len(original),'all_retained_file_count':len(files)+len(original),
   'total_size_bytes':sum(e['size_bytes'] for e in files),'files':files,
   'human_review':'Runtime-only PIE substitution, never save editor map; contact/FP framing pending',
   'existing_aim_pose_comparison':'author_v4 + live_v5; unselected contact limitation',
   'common_rotation_comparison':'rigid_author_v1 + rigid_live_v1; abnormal shutdown retained, not clean runtime acceptance',
   'evidence_root':BASE.relative_to(ROOT).as_posix()}
OUT.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({k:r[k] for k in ('status','file_count','all_retained_file_count','total_size_bytes','active_city_unchanged')}))
