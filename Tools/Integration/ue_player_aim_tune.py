"""Bounded existing-aim upper-spine mask adjustment, preserving the first trial."""
import hashlib,json,runpy,shutil,traceback
from pathlib import Path
import unreal
ROOT=Path(__file__).resolve().parents[2]
STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
OUT=STORE/'Evidence/CityGameplay20261002/RifleCrosshairV4/author_v4'
assert not OUT.exists();OUT.mkdir()
r=json.loads((OUT.parent/'author_v3/result.json').read_text());assert not r['errors']
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
f=ROOT/r['saved_trial']['path'];assert digest(f)==r['saved_trial']['sha256']
shutil.copy2(f,OUT/'ABP_PC_PlayerAimV4.before.uasset')
try:
    bp=unreal.load_asset(r['saved_trial']['package'])
    axis=json.loads((OUT.parent/'upper_audit_v1/result.json').read_text())['calibration']['hand_r']['axis']
    r['mask_adjustment']=json.loads(unreal.ParisBlueprintAuthoring.add_player_aim_layer(bp,unreal.Vector(*axis)))
    assert r['mask_adjustment']['success']
    assert unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
    r['saved_trial'].update(sha256=digest(f),size_bytes=f.stat().st_size)
except Exception:r['status']='failed';r['errors'].append(traceback.format_exc())
(OUT/'result.json').write_text(json.dumps(r,indent=2))
if not r['errors']:runpy.run_path(str(Path(__file__).with_name('ue_player_rifle_aim_author.py')),run_name='__main__')
unreal.SystemLibrary.quit_editor()
