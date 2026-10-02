"""New-only Blueprint reload authoring and bounded native-world/fresh-load tests."""
import hashlib
import json
import os
import traceback
from pathlib import Path
import unreal

ROOT=Path(__file__).resolve().parents[2]
STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
OUT=STORE/'Evidence/P4/SimplifiedReload20261002'
OUT.mkdir(parents=True,exist_ok=True)
MODE=os.environ.get('CS549_RELOAD_MODE','author')
IDENTITY=os.environ.get('CS549_RELOAD_IDENTITY',MODE)
DEST=OUT/(IDENTITY+'.json')
if DEST.exists():raise RuntimeError('Preserve previous action evidence')
PREFIX='/Game/ParisCombat/Blueprints/Characters/SimplifiedReloadDraft/'
report={'engine':unreal.SystemLibrary.get_engine_version(),'mode':MODE,'scope':'Simplified animation-phase reload transaction only; no M1, FP, live input, shots/traces/HUD/performance/package acceptance','assets':[],'cases':[],'errors':[]}
try:
    if MODE=='author':
        # Do not begin the later action slice before the selected baseline is available.
        assert (ROOT/'Assets/Sync/RIFLE_MOTION_PUBLICATION_STATUS.json').is_file()
        result=json.loads(unreal.ParisBlueprintAuthoring.create_simplified_reload_draft())
        if 'error' in result:raise RuntimeError(result['error'])
        report['authoring']=result
        for path in result['assets']:
            asset=unreal.load_asset(path)
            assert unreal.EditorAssetLibrary.save_loaded_asset(asset,only_if_is_dirty=False)
            report['assets'].append(path)
    elif MODE=='probe':
        fps=int(os.environ.get('CS549_RELOAD_FPS','60'))
        for name in ('BP_PCPlayerReloadV1','BP_PCNPCReloadV1'):
            for rate in (.5,1.0,1.5):
                case=json.loads(unreal.ParisBlueprintAuthoring.probe_simplified_reload(PREFIX+name+'.'+name+'_C',rate,fps))
                report['cases'].append(case)
                DEST.write_text(json.dumps(report,indent=2),encoding='utf-8')
        assert all(c['all_pass'] for c in report['cases']), 'Read failed native Blueprint action assertions'
    elif MODE=='fresh':
        report['bridge_available']=hasattr(unreal,'ParisBlueprintAuthoring')
        assert not report['bridge_available'], 'Fresh test must disable authoring bridge'
        registry=unreal.AssetRegistryHelpers.get_asset_registry();registry.search_all_assets(True)
        for name in ('BP_PCCombatantReloadV1','BP_PCPlayerReloadV1','BP_PCNPCReloadV1'):
            path=PREFIX+name;asset=unreal.load_asset(path);cls=unreal.EditorAssetLibrary.load_blueprint_class(path)
            assert asset and cls
            defaults=unreal.get_default_object(cls)
            # Blueprint-authored FNames are not automatically snake-cased by
            # Python like native reflected properties; use their exact names.
            assert defaults.get_editor_property('Capacity')==8 and defaults.get_editor_property('LoadedAmmo')==2
            dependencies=[str(x) for x in registry.get_dependencies(path,unreal.AssetRegistryDependencyOptions(include_hard_package_references=True,include_soft_package_references=True))]
            assert not any('ParisEditorBridge' in x for x in dependencies)
            file=STORE/'Content'/(path.removeprefix('/Game/')+'.uasset')
            report['assets'].append({'package':path,'path':file.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'size_bytes':file.stat().st_size,'dependencies':dependencies})
    else:raise RuntimeError('Unknown mode')
    report['status']='pass_'+MODE+'_bounded_reload_only'
except Exception:
    report['status']='failed';report['errors'].append(traceback.format_exc())
DEST.write_text(json.dumps(report,indent=2),encoding='utf-8')
unreal.log('CS549_SIMPLIFIED_RELOAD '+report['status'])
if report['errors']:raise RuntimeError('Read preserved simplified reload evidence')
