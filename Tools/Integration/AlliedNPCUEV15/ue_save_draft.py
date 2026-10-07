"""Persist/fresh-read the proven Ready config only; no adoption or map write."""
import os,sys,traceback
from pathlib import Path
import unreal
sys.path.insert(0,str(Path(__file__).parent))
from common import *
IDENTITY=os.environ['CS549_ALLIED_DRAFT_ID'];MODE=os.environ['CS549_ALLIED_DRAFT_MODE']
assert MODE in ('save','fresh') and IDENTITY.replace('_','').isalnum()
OUT=BASE/IDENTITY;assert not OUT.exists();OUT.mkdir(parents=True)
cfg_path=BASE/'preflight_v16/binding.json'
abp_path='/Game/ParisCombat/Animation/AlliedGripV15/ABP_PC_AlliedGripPostV16'
data_path='/Game/ParisCombat/Animation/AlliedGripV15/DA_PC_AlliedGripV16'
r={'mode':MODE,'pid':os.getpid(),'errors':[],'selected':False,'map_saved':False,
   'scope':'Draft native asset persistence only, no action proof rerun','guards_before':guards(True)}
try:
    early=read(BASE/'native_hold_v16_early/result.json')
    assert not early['errors']
    abp_file=STORE/'Content'/(abp_path.removeprefix('/Game/')+'.uasset')
    assert sha(abp_file)==early['candidate_abp_sha256']
    cls=unreal.EditorAssetLibrary.load_blueprint_class(abp_path);assert cls
    if MODE=='save':
        assert not unreal.EditorAssetLibrary.does_asset_exist(data_path),'Preserve occupied candidate'
        factory=unreal.DataAssetFactory();factory.set_editor_property('data_asset_class',unreal.ParisNPCGripConfig)
        data=unreal.AssetToolsHelpers.get_asset_tools().create_asset(data_path.rsplit('/',1)[1],data_path.rsplit('/',1)[0],unreal.ParisNPCGripConfig,factory)
        assert data
        data.set_editor_property('PostProcessClass',cls);data.set_editor_property('BindingJson',cfg_path.read_text())
        assert unreal.EditorAssetLibrary.save_loaded_asset(data,False)
    else:
        prior=read(BASE/'draft_asset_save/result.json')
        assert not prior['errors']
        for row in prior['files']:
            p=ROOT/row['path'];assert p.stat().st_size==row['size_bytes'] and sha(p)==row['sha256']
        data=unreal.load_asset(data_path);assert data
    assert data.get_editor_property('BindingJson')==cfg_path.read_text()
    assert data.get_editor_property('PostProcessClass')==cls
    assert sha(abp_file)==early['candidate_abp_sha256'],'No graph reauthoring'
    registry=unreal.AssetRegistryHelpers.get_asset_registry()
    opts=unreal.AssetRegistryDependencyOptions(include_hard_package_references=True,include_soft_package_references=True)
    r['dependencies']={p:sorted(str(x) for x in registry.get_dependencies(p,opts)) for p in (data_path,abp_path)}
    r['files']=[{'path':p.relative_to(ROOT).as_posix(),'size_bytes':p.stat().st_size,'sha256':sha(p)}
        for p in (abp_file,STORE/'Content'/(data_path.removeprefix('/Game/')+'.uasset'))]
    r['status']='saved_native_draft_not_formal' if MODE=='save' else 'fresh_native_draft_exact_not_formal'
except Exception:
    r['errors'].append(traceback.format_exc());r['status']='stopped_preserved'
finally:
    r['guards_after']=guards(True);write(OUT/'result.json',r);unreal.SystemLibrary.quit_editor()
