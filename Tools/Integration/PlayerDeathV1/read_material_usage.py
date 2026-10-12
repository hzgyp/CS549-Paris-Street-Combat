"""Read-only cooked-material usage prerequisites; never set/save usage flags."""
import unreal,json
from pathlib import Path
out=Path(r'D:/0.Rutgers/CS549/Project-New/tmp/g1-player-death-20261011/material-audit-v3');out.mkdir(exist_ok=True)
paths=['/Game/WW2City/Library_Meshingun/VFX_Meshingun/Firework/Material/M_Glow','/Game/MsvFx_MuzzleFlash_Pack/Sources/Materials/MasterMTL/M_Muzzle_Flash','/Game/WW2City/Environment/Particle/Fire/Material/Fire/M_Fire_SubUV_11X11_Noise','/Game/WW2City/Environment/Particle/BulletTrail/M_GlowTrails','/Game/WW2City/Library_Meshingun/VFX_Meshingun/SmokeFog/Material/MI_Smoke']
result=[];lib=unreal.MaterialEditingLibrary
for path in paths:
    obj=unreal.load_asset(path);r=dict(path=path,loaded=bool(obj))
    if obj:
        for key in ['used_with_particle_sprites','used_with_niagara_sprites','used_with_mesh_particles','blend_mode']:
            try:r[key]=str(obj.get_editor_property(key))
            except Exception as e:r[key+'_unavailable']=str(e)
        if isinstance(obj,unreal.Material):
            r['scalars']={str(k):lib.get_material_default_scalar_parameter_value(obj,k) for k in lib.get_scalar_parameter_names(obj)}
            r['vectors']={str(k):str(lib.get_material_default_vector_parameter_value(obj,k)) for k in lib.get_vector_parameter_names(obj)}
    result.append(r)
(out/'USAGE.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
unreal.log('PARIS_DEATH_READ_ONLY_MATERIAL_USAGE_COMPLETE')
