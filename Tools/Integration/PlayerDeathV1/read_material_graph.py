"""Inspect expression inputs without modifying material/native assets."""
import unreal,json
from pathlib import Path
out=Path(r'D:/0.Rutgers/CS549/Project-New/tmp/g1-player-death-20261011/material-audit-v4');out.mkdir(exist_ok=True)
lib=unreal.MaterialEditingLibrary;result=[]
for path in ['/Game/WW2City/Environment/Particle/Fire/Material/Fire/M_Fire_SubUV_11X11_Noise']:
    obj=unreal.load_asset(path);nodes=[]
    def walk(expressions):
        for e in expressions:
            name=e.get_class().get_name();r=dict(type=name)
            if name=='MaterialExpressionDynamicParameter':
                for key in ['param_names','default_value']:
                    try:r[key]=str(e.get_editor_property(key))
                    except Exception as err:r[key+'_unavailable']=str(err)
            if name=='MaterialExpressionMaterialFunctionCall':
                f=e.get_editor_property('material_function')
                if f:r['function']=f.get_path_name();walk(lib.get_material_function_expressions(f))
            nodes.append(r)
    walk(lib.get_material_expressions(obj));result.append(dict(path=path,expressions=nodes))
(out/'GRAPH.json').write_text(json.dumps(result,indent=2),encoding='utf-8');unreal.log('PARIS_DEATH_MATERIAL_GRAPH_READ_ONLY_COMPLETE')
