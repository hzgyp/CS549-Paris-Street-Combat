"""Read-only source/target proportions and installed native retarget API inventory."""
import json
from pathlib import Path
import unreal

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/P2/Retarget'
OUT.mkdir(exist_ok=True)
DEST = OUT / 'reference_diagnosis_v1.json'
if DEST.exists():
    raise RuntimeError('Preserve existing diagnosis; choose a new run identity')
MESH = '/Game/ParisCombat/Characters/Adaptation/Meshes/'
paths = ['/Game/RifleAnimsetPro/UE4_Mannequin/Mesh/SK_Mannequin'] + [MESH + x for x in (
    'SK_WWII_GermanSoldier_varA_UE582_v1', 'SK_WWII_GermanSoldier_varB_UE582_v1',
    'SK_WWII_US_Paratrooper_simple_UE582_v1', 'SK_WWII_US_Paratrooper_simpleB_UE582_v1')]
report = {'engine': unreal.SystemLibrary.get_engine_version(),
          'meshes': [json.loads(unreal.ParisBlueprintAuthoring.describe_reference_skeleton(p)) for p in paths],
          'native_api': {}}
for name in ('IKRigDefinitionFactory', 'IKRetargetFactory', 'IKRigController', 'IKRetargeterController',
             'IKRetargetBatchOperation', 'IKRetargetBatchOperationInputs', 'RetargetSourceOrTarget', 'AutoMapChainType'):
    cls = getattr(unreal, name, None)
    report['native_api'][name] = {'doc': str(getattr(cls, '__doc__', None)),
                                'methods': {n: str(getattr(cls, n).__doc__) for n in dir(cls)
                                            if not n.startswith('_') and ('retarget' in n or 'chain' in n or 'mesh' in n or 'default_ops' in n or 'align' in n or 'controller' in n)}}
report['animations'] = [str(x.package_name) for x in unreal.AssetRegistryHelpers.get_asset_registry().get_assets_by_path(
    '/Game/RifleAnimsetPro/Animations/InPlace', recursive=True)]
DEST.write_text(json.dumps(report, indent=2), encoding='utf-8')
unreal.log('CS549_REFERENCE_DIAGNOSIS_DONE')
