"""Fresh GLB import: validate exported source-clip bones and deformed bounds."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Assets/LocalWorking/AssetWorkbench/3d/export-v3'
source=json.loads((OUT/'export-report.json').read_text())
report={'models':[],'source_inputs_unchanged':source['inputs_unchanged']}
assert not source['errors'] and source['inputs_unchanged']
for row in source['models']:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.render.fps=30
    bpy.ops.import_scene.gltf(filepath=str(ROOT/row['path']))
    rigs=[o for o in bpy.context.scene.objects if o.type=='ARMATURE']
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
    actions=list(bpy.data.actions)
    result={'id':row['id'],'meshes':len(meshes),'clips':[]}
    assert meshes
    if row['clips']:
        assert len(rigs)==1 and len(actions)==len(row['clips'])
        rig=rigs[0];rig.animation_data_clear();rig.animation_data_create()
        bpy.context.scene.render.fps=30
        for clip in row['clips']:
            action=next(a for a in actions if a.name.startswith(clip['name']))
            rig.animation_data.action=action
            if action.slots:rig.animation_data.action_slot=action.slots[0]
            errors=[];bounds=[]
            for sample in clip['samples']:
                f=sample['time']*30;bpy.context.scene.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update()
                for name in ('hand_l','foot_l'):
                    if sample[name] is not None:
                        actual=(rig.matrix_world@rig.pose.bones[name].matrix).translation
                        errors.append((actual-Vector(sample[name])).length)
                deps=bpy.context.evaluated_depsgraph_get();points=[]
                for obj in meshes:
                    evaluated=obj.evaluated_get(deps)
                    points.extend(evaluated.matrix_world@v.co for v in evaluated.data.vertices)
                size=[max(p[i] for p in points)-min(p[i] for p in points) for i in range(3)]
                assert max(size)<5 and max(size)>.1,(row['id'],clip['name'],size)
                bounds.append(size)
            assert max(errors)<.002,(row['id'],clip['name'],max(errors))
            result['clips'].append({'name':clip['name'],'max_bone_error_m':max(errors),'sample_bounds_m':bounds})
    report['models'].append(result)
    (OUT/'fresh-import-validation.json').write_text(json.dumps(report,indent=2))
    print('FRESH_IMPORT_PASS',row['id'],flush=True)
report['passed']=True
(OUT/'fresh-import-validation.json').write_text(json.dumps(report,indent=2))
