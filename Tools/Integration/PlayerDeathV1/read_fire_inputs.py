"""Read-only sprite fire input graph, including numeric defaults."""
import unreal,json
from pathlib import Path
out=Path(r'D:/0.Rutgers/CS549/Project-New/tmp/g1-player-death-20261011/material-audit-v5');out.mkdir(exist_ok=True)
lib=unreal.MaterialEditingLibrary;m=unreal.load_asset('/Game/WW2City/Environment/Particle/Fire/Material/Fire/M_Fire_SubUV_11X11_Noise');nodes=lib.get_material_expressions(m)
result=[]
for e in nodes:
    r=dict(name=e.get_name(),type=e.get_class().get_name(),inputs=[i.get_name() if i else None for i in lib.get_inputs_for_material_expression(m,e)])
    for key in ['constant','r','value','const_a','const_b','const_exponent','default_value','component_type','r','g','b','a']:
        try:r[key]=str(e.get_editor_property(key))
        except Exception:pass
    result.append(r)
(out/'INPUTS.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
unreal.log('PARIS_DEATH_READ_ONLY_FIRE_INPUTS_COMPLETE')
