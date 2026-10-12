"""Read-only correction for a tall, multipart source collection's diagnostic framing."""
import sys
from pathlib import Path
import bpy
from mathutils import Vector

root=Path(__file__).resolve().parents[2]
source=next((root/'Assets/LocalWorking/Intake/2026-10-03/01_MW2_Guns_Asset_Library').rglob('*.blend'))
out=root/'Assets/LocalWorking/AssetWorkbench/previews/pila-framing-v2'
out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
objects=[o for o in bpy.data.collections['PILA'].all_objects if o.type=='MESH']
scene=bpy.data.scenes.new('PILA_preview_only')
for o in objects:scene.collection.objects.link(o);o.hide_render=False
points=[o.matrix_world @ Vector(c) for o in objects for c in o.bound_box]
lo=Vector([min(v[i] for v in points) for i in range(3)])
hi=Vector([max(v[i] for v in points) for i in range(3)])
center=(lo+hi)*.5;extent=max(hi-lo)
cam_data=bpy.data.cameras.new('preview_camera');cam=bpy.data.objects.new('preview_camera',cam_data)
scene.collection.objects.link(cam);scene.camera=cam;cam_data.type='ORTHO'
# Account for landscape camera aspect and the separated parts in the source collection.
cam_data.ortho_scale=extent*2.2
scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.color_type='TEXTURE'
scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.background_type='WORLD'
scene.world=bpy.data.worlds.new('preview_world');scene.world.color=(.055,.055,.055)
scene.render.resolution_x=1100;scene.render.resolution_y=650;scene.render.resolution_percentage=100
for name,direction in [('side',Vector((1,-2,1))),('opposite',Vector((-1,2,.6)))]:
    cam.location=center+direction.normalized()*max(extent*3,1)
    cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=str(out/('PILA_'+name+'.png'))
    bpy.ops.render.render(write_still=True,scene=scene.name)
# No save operation: original delivery and all other scenes remain on disk unchanged.
