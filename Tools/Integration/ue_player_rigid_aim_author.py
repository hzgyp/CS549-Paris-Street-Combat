"""Separate common upper-body aim trial; keep the existing-pose comparisons unselected."""
import hashlib,json,traceback
from pathlib import Path
import unreal
ROOT=Path(__file__).resolve().parents[2]
STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
OUT=STORE/'Evidence/CityGameplay20261002/RifleCrosshairV4/rigid_author_v1'
assert not OUT.exists();OUT.mkdir()
r=json.loads((OUT.parent/'author_v4/result.json').read_text());assert not r['errors']
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert digest(ROOT/r['saved_trial']['path'])==r['saved_trial']['sha256']
inventory=json.loads((ROOT/'Assets/Integration/CITY_RIFLE_ACTION_DRAFT_INVENTORY_20261002.json').read_text())
deps=json.loads((ROOT/inventory['retained_dependency_inventory']).read_text())
records=inventory['files']+deps['files']+inventory['retained_unselected_rejected_trial']+[r['saved_trial']]+r['aim_dependencies']
assert all(digest(ROOT/e['path'])==e['sha256'] for e in records)
DEST='/Game/ParisCombat/Animation/WeaponAimingV4/ABP_PC_PlayerRigidAimV4'
try:
    assert not unreal.EditorAssetLibrary.does_asset_exist(DEST)
    bp=unreal.EditorAssetLibrary.duplicate_asset(r['saved_trial']['package'],DEST);assert bp
    axis=json.loads((OUT.parent/'upper_audit_v1/result.json').read_text())['calibration']['spine_03']['axis']
    r['rigid_helper']=json.loads(unreal.ParisBlueprintAuthoring.add_player_rigid_aim_layer(bp,unreal.Vector(*axis)))
    assert r['rigid_helper']['success']
    assert unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
    r['status']='saved_unselected_rigid_upper_aim_requires_runtime_contact_review'
except Exception:r['status']='failed';r['errors'].append(traceback.format_exc())
finally:
    f=STORE/('Content/'+DEST.removeprefix('/Game/')+'.uasset')
    if f.exists():r['saved_trial']={'package':DEST,'path':f.relative_to(ROOT).as_posix(),'size_bytes':f.stat().st_size,'sha256':digest(f)}
    r['all_previous_bytes_unchanged']=all(digest(ROOT/e['path'])==e['sha256'] for e in records)
    (OUT/'result.json').write_text(json.dumps(r,indent=2));unreal.SystemLibrary.quit_editor()
