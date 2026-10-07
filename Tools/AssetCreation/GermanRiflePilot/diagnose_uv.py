"""Matched unlit base-color views isolate reduction artifacts from gloss."""
import json
from pathlib import Path
import bpy
from mathutils import Vector, Matrix

root=Path(__file__).resolve().parents[3]
store=root/'Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-v1'
out=store/'evidence/color_diagnostic_v1';out.mkdir(parents=True,exist_ok=False)
matrix=Matrix(json.loads((store/'evidence/incoming_v2/inspection.json').read_text())['normalizationMatrix'])
for label,source,normalize in [('incoming',store/'incoming/kar98k-base-v1.glb',True),('adapt_v2',store/'blender/adapt_v2/Kar98k_WorldCandidate_v2.glb',False)]:
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(source))
    if normalize:
        for o in list(bpy.context.scene.objects):
            if o.type=='MESH':
                world=matrix @ o.matrix_world;o.parent=None;o.matrix_world=world
    for mat in bpy.data.materials:
        nodes=mat.node_tree.nodes;links=mat.node_tree.links
        shader=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
        emission=nodes.new('ShaderNodeEmission');emission.inputs['Strength'].default_value=1
        if shader.inputs['Base Color'].is_linked:links.new(shader.inputs['Base Color'].links[0].from_socket,emission.inputs['Color'])
        else:emission.inputs['Color'].default_value=shader.inputs['Base Color'].default_value
        output=next(n for n in nodes if n.type=='OUTPUT_MATERIAL');links.new(emission.outputs[0],output.inputs['Surface'])
    scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=1;scene.cycles.use_denoising=False
    scene.render.resolution_x=1440;scene.render.resolution_y=810;scene.render.resolution_percentage=100
    scene.view_settings.view_transform='Standard';scene.render.image_settings.file_format='PNG'
    d=bpy.data.cameras.new('Frozen_RightSide_BaseColor');cam=bpy.data.objects.new(d.name,d);scene.collection.objects.link(cam)
    cam.location=(0,-3,0);cam.rotation_euler=(-cam.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=1.30;scene.camera=cam
    scene.render.filepath=str(out/(label+'_unlit_color.png'));bpy.ops.render.render(write_still=True)
print('Matched unlit diagnostic complete; no geometry or saved asset edited')
