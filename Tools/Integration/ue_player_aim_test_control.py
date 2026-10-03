"""Expose only the new trial's existing enable switch for paired runtime diagnostics."""
import hashlib,json,shutil,traceback
from pathlib import Path
import unreal
ROOT=Path(__file__).resolve().parents[2]
STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
OUT=STORE/'Evidence/CityGameplay20261002/RifleCrosshairV4/author_v3'
assert not OUT.exists();OUT.mkdir()
r=json.loads((OUT.parent/'author_v2/result.json').read_text())
assert not r['errors']
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
f=ROOT/r['saved_trial']['path'];assert digest(f)==r['saved_trial']['sha256']
shutil.copy2(f,OUT/'ABP_PC_PlayerAimV4.before.uasset')
try:
    bp=unreal.load_asset(r['saved_trial']['package'])
    unreal.BlueprintEditorLibrary.set_blueprint_variable_instance_editable(bp,'AimEnabled',True)
    assert unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
    r['saved_trial'].update(sha256=digest(f),size_bytes=f.stat().st_size)
    r['diagnostic_switch']='Only AimEnabled instance-editability changed; prior bytes retained beside this report'
except Exception:
    r['status']='failed';r['errors'].append(traceback.format_exc())
(OUT/'result.json').write_text(json.dumps(r,indent=2));unreal.SystemLibrary.quit_editor()
