"""One fresh read, targeted on-disk registry scan, no map/asset writes."""
import os,sys,traceback
from pathlib import Path
import unreal
sys.path.insert(0,str(Path(__file__).parent))
from common import *
OUT=BASE/'draft_asset_read_v17';assert not OUT.exists();OUT.mkdir(parents=True)
r={'pid':os.getpid(),'errors':[],'selected':False,'map_saved':False,'asset_saved':False,
   'guards_before':guards(True)}
abp_path='/Game/ParisCombat/Animation/AlliedGripV15/ABP_PC_AlliedGripPostV16'
data_path='/Game/ParisCombat/Animation/AlliedGripV15/DA_PC_AlliedGripV16'
cfg_path=BASE/'preflight_v16/binding.json'
try:
    pre=read(BASE/'draft_read_preflight/result.json')
    def exact():
        for row in pre['files']:
            p=ROOT/row['path'];assert p.stat().st_size==row['size_bytes'] and sha(p)==row['sha256']
        assert sha(cfg_path)==pre['config_sha256']
    exact()
    data=unreal.load_asset(data_path);abp=unreal.load_asset(abp_path)
    cls=unreal.EditorAssetLibrary.load_blueprint_class(abp_path)
    assert data and abp and cls
    assert data.get_class()==unreal.ParisNPCGripConfig.static_class()
    assert data.get_editor_property('BindingJson')==cfg_path.read_text()
    assert data.get_editor_property('PostProcessClass')==cls
    original=unreal.load_asset(read(cfg_path)['source_mesh']);assert original
    skeleton=original.get_editor_property('skeleton')
    assert abp.get_editor_property('target_skeleton')==skeleton
    r['skeleton']=skeleton.get_path_name()
    registry=unreal.AssetRegistryHelpers.get_asset_registry()
    registry.scan_paths_synchronous([abp_path.rsplit('/',1)[0]],True)
    opts=unreal.AssetRegistryDependencyOptions(include_hard_package_references=True,include_soft_package_references=True)
    r['dependencies']={}
    for package in (data_path,abp_path):
        deps=registry.get_dependencies(package,opts)
        assert deps is not None,'On-disk dependencies unavailable: '+package
        r['dependencies'][package]=sorted(str(x) for x in deps)
    assert abp_path in r['dependencies'][data_path]
    assert skeleton.get_path_name().split('.')[0] in r['dependencies'][abp_path]
    exact();r['files']=pre['files'];r['config_sha256']=pre['config_sha256']
    r['status']='fresh_native_draft_exact_not_formal'
except Exception:
    r['errors'].append(traceback.format_exc());r['status']='stopped_preserved'
finally:
    r['guards_after']=guards(True);write(OUT/'result.json',r);unreal.SystemLibrary.quit_editor()
