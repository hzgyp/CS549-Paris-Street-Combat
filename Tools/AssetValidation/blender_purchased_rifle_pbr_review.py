"""Read-only original-material review; no delivery saving or geometry edits."""
import argparse
import json
import sys
from pathlib import Path

import bpy
from mathutils import Vector

p = argparse.ArgumentParser()
p.add_argument('--source', required=True)
p.add_argument('--out', required=True)
p.add_argument('--collections', nargs='+', required=True)
a = p.parse_args(sys.argv[sys.argv.index('--') + 1:])
out = Path(a.out).resolve()
out.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(Path(a.source).resolve()), load_ui=False, use_scripts=False)
report = {'original_saved': False, 'material_changes': False, 'geometry_changes': False, 'collections': []}
for name in a.collections:
    objects = [o for o in bpy.data.collections[name].all_objects if o.type == 'MESH']
    mats = {m for o in objects for m in o.data.materials if m}
    row = {'name': name, 'objects': [o.name for o in objects], 'materials': [], 'views': []}
    for m in sorted(mats, key=lambda x: x.name):
        graph = m.node_tree
        row['materials'].append({'name': m.name, 'nodes': [
            {'name': n.name, 'type': n.type, 'image': n.image.name if n.type == 'TEX_IMAGE' and n.image else None,
             'size': list(n.image.size) if n.type == 'TEX_IMAGE' and n.image else None}
            for n in graph.nodes] if graph else [], 'links': [
                [l.from_node.name, l.from_socket.name, l.to_node.name, l.to_socket.name]
                for l in graph.links] if graph else []})
    scene = bpy.data.scenes.new('ReadOnly_PBR_' + name)
    for o in objects:
        scene.collection.objects.link(o)
        o.hide_render = False
    points = [o.matrix_world @ Vector(c) for o in objects for c in o.bound_box]
    low = Vector([min(v[i] for v in points) for i in range(3)])
    high = Vector([max(v[i] for v in points) for i in range(3)])
    center = (low + high) * .5
    extent = max(high - low)
    camera = bpy.data.objects.new('ReadOnlyCamera', bpy.data.cameras.new('ReadOnlyCamera'))
    scene.collection.objects.link(camera)
    scene.camera = camera
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = extent * 1.25
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 24
    scene.cycles.use_denoising = True
    scene.world = bpy.data.worlds.new('ReadOnlyWorld')
    scene.world.use_nodes = True
    scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.12, .12, .12, 1)
    scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .8
    scene.render.resolution_x, scene.render.resolution_y = 1100, 650
    scene.render.resolution_percentage = 100
    scene.view_settings.view_transform = 'AgX'
    for i, direction in enumerate([Vector((1,-2,3)), Vector((-1,2,1)), Vector((0,0,3))]):
        ld = bpy.data.lights.new('ReadOnlyLight', 'AREA')
        light = bpy.data.objects.new('ReadOnlyLight', ld)
        scene.collection.objects.link(light)
        light.location = center + direction.normalized() * extent * 1.8
        light.rotation_euler = (center - light.location).to_track_quat('-Z', 'Y').to_euler()
        ld.energy = extent ** 2 * (180 if i == 0 else 100)
        ld.shape, ld.size = 'DISK', extent
    for view, direction in [('side', Vector((1,-2,1))), ('opposite', Vector((-1,2,.6)))]:
        camera.location = center + direction.normalized() * max(extent * 3, 1)
        camera.rotation_euler = (center - camera.location).to_track_quat('-Z', 'Y').to_euler()
        filename = name.replace(' ', '_') + '_' + view + '.png'
        scene.render.filepath = str(out / filename)
        bpy.ops.render.render(write_still=True, scene=scene.name)
        row['views'].append(filename)
    report['collections'].append(row)
    bpy.data.scenes.remove(scene)
(out / 'original_material_review.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print('READ_ONLY_REVIEW_COMPLETE', flush=True)
