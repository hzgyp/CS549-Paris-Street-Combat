"""German V11 adoption epoch; no obsolete snapshot rollback."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
BASE=STORE/'Evidence/GermanNPCFormalV14'
PLUGIN=ROOT/'Unreal/ParisStreetCombat/Plugins/ParisNPCGripV15'
MAP=ROOT/'Unreal/ParisStreetCombat/Content/ParisCombat/Maps/LV_ParisStreetCombat_V1.umap'
DESCRIPTOR=ROOT/'Unreal/ParisStreetCombat/WW2FranceLiberation.uproject'
ENTRY='/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1'
DATA='/Game/ParisCombat/Animation/GermanGripV14/DA_PC_GermanGripV11'
GRAPH='/Game/ParisCombat/Animation/GermanGripV14/ABP_PC_GermanGripPostV11'
CLASS='/Game/ParisCombat/Blueprints/CityGameplayV1/BP_PCParisGermanNPCV1'
GUN='/Game/ParisCombat/Weapons/GermanRifleUEV1/BP_PC_GermanRifleAttachmentV2'
GUNMESH='/Game/ParisCombat/Weapons/GermanRifleUEV1/ImportV1/GermanRifle_FineWood_V15/StaticMeshes/SM_PC_GermanRifleV15'
CONFIG=BASE/'preflight/binding.json'
LABEL='PC_GermanApprovedGripV11'
sys.path.insert(0,str(ROOT/'Tools/Integration/AlliedNPCGripV2'))
import transform_math as tm
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def row(p):return {'path':p.relative_to(ROOT).as_posix(),'size_bytes':p.stat().st_size,'sha256':sha(p)}
def exact(r):
    p=ROOT/r['path'];return p.is_file() and p.stat().st_size==r['size_bytes'] and sha(p)==r['sha256']
def guards(map_allowed=False,binaries_allowed=True):
    pre=read(BASE/'preflight/result.json')
    allowed={MAP.resolve()} if map_allowed else set()
    if binaries_allowed:allowed.update((ROOT/r['path']).resolve() for r in pre['binary_files'])
    bad=[r['path'] for r in pre['guards'] if not exact(r) and (ROOT/r['path']).resolve() not in allowed]
    assert not bad,bad
    assert exact(pre['descriptor']) and all(exact(r) for r in pre['baseline_files'])
    if CONFIG.exists():assert sha(CONFIG)==pre['config_sha256']
    return {'epoch_rows':len(pre['guards']),'unchanged_rows':sum(exact(r) for r in pre['guards']),
            'allowed_map_change':map_allowed,'allowed_rebuilt_binary_paths':[r['path'] for r in pre['binary_files']] if binaries_allowed else []}
