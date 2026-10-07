"""Read-only delivered Blender library inventory and bounded diagnostic renders."""
import argparse
import collections
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

p = argparse.ArgumentParser()
p.add_argument('--source', required=True)
p.add_argument('--out', required=True)
p.add_argument('--render', nargs='*', default=[])
a = p.parse_args(sys.argv[sys.argv.index('--') + 1:])
source, out = Path(a.source).resolve(), Path(a.out).resolve()
out.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False, use_scripts=False)

def animation_info(obj):
    ad = obj.animation_data
    return {'action': ad.action.name if ad and ad.action else None,
            'nla': [t.name for t in ad.nla_tracks] if ad else [],
            'drivers': len(ad.drivers) if ad else 0}

rows = []
for obj in bpy.data.objects:
    row = {'name': obj.name, 'type': obj.type, 'parent': obj.parent.name if obj.parent else None,
           'collections': sorted(c.name for c in obj.users_collection),
           'asset_marked': bool(obj.asset_data), 'dimensions': list(obj.dimensions),
           'location': list(obj.location), 'animation': animation_info(obj)}
    if obj.type == 'MESH':
        obj.data.calc_loop_triangles()
        row.update(vertices=len(obj.data.vertices), triangles=len(obj.data.loop_triangles),
                   uv_layers=[u.name for u in obj.data.uv_layers],
                   materials=[m.name if m else None for m in obj.data.materials],
                   modifiers=[{'name': m.name, 'type': m.type,
                               'target': m.object.name if m.type == 'ARMATURE' and m.object else None}
                              for m in obj.modifiers], vertex_groups=[g.name for g in obj.vertex_groups])
    elif obj.type == 'ARMATURE':
        row['bones'] = [{'name': b.name, 'parent': b.parent.name if b.parent else None,
                         'deform': b.use_deform} for b in obj.data.bones]
    rows.append(row)
images = []
for im in bpy.data.images:
    packed = bool(im.packed_file) or bool(im.packed_files)
    path = bpy.path.abspath(im.filepath, library=im.library) if im.filepath else ''
    images.append({'name': im.name, 'source': im.source, 'size': list(im.size),
                   'packed': packed, 'filepath': im.filepath,
                   'external_exists': Path(path).is_file() if path else False})
report = {'blender': bpy.app.version_string, 'source': source.name,
          'original_saved': False, 'scenes': [s.name for s in bpy.data.scenes],
          'collections': [{'name': c.name, 'objects': [o.name for o in c.objects],
                           'children': [x.name for x in c.children], 'asset_marked': bool(c.asset_data)}
                          for c in bpy.data.collections],
          'objects': rows, 'images': images,
          'actions': [{'name': x.name, 'frame_range': list(x.frame_range)} for x in bpy.data.actions],
          'materials': [{'name': m.name, 'images': sorted({n.image.name for n in m.node_tree.nodes
                                                        if n.type == 'TEX_IMAGE' and n.image})
                         if m.use_nodes else []} for m in bpy.data.materials],
          'linked_libraries': [x.filepath for x in bpy.data.libraries], 'renders': []}
(out / 'weapon_library_inventory.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'objects': len(rows), 'types': dict(collections.Counter(r['type'] for r in rows)),
                  'collections': [c['name'] for c in report['collections']],
                  'actions': [x['name'] for x in report['actions']],
                  'images': len(images), 'packed': sum(x['packed'] for x in images)}, ensure_ascii=True), flush=True)

for name in a.render:
    candidates = [o for o in bpy.data.objects if o.type == 'MESH' and o.name == name]
    if not candidates:
        coll = bpy.data.collections.get(name)
        candidates = [o for o in coll.all_objects if o.type == 'MESH'] if coll else []
    if not candidates:
        report['renders'].append({'name': name, 'error': 'No exact object/collection'})
        continue
    # New temporary scene reuses source datablocks without writing the delivery.
    scene = bpy.data.scenes.new('Inspection_' + name)
    for obj in candidates:
        scene.collection.objects.link(obj)
        obj.hide_render = False
    deps = bpy.context.evaluated_depsgraph_get()
    points = [o.matrix_world @ Vector(c) for o in candidates for c in o.bound_box]
    low = Vector([min(v[i] for v in points) for i in range(3)])
    high = Vector([max(v[i] for v in points) for i in range(3)])
    center = (low + high) * .5
    extent = max(high - low)
    cam_data = bpy.data.cameras.new('InspectCamera')
    cam = bpy.data.objects.new('InspectCamera', cam_data)
    scene.collection.objects.link(cam)
    scene.camera = cam
    cam_data.type = 'ORTHO'
    cam_data.ortho_scale = extent * 1.25
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.display.shading.light = 'STUDIO'
    scene.display.shading.color_type = 'TEXTURE'
    scene.display.shading.show_shadows = True
    scene.display.shading.show_cavity = True
    scene.display.shading.background_type = 'WORLD'
    scene.world = bpy.data.worlds.new('InspectWorld')
    scene.world.color = (.055, .055, .055)
    scene.render.resolution_x, scene.render.resolution_y = 1100, 650
    scene.render.resolution_percentage = 100
    for view, direction in [('side', Vector((1, -2, 1))), ('opposite', Vector((-1, 2, .6)))]:
        cam.location = center + direction.normalized() * max(extent * 3, 1)
        cam.rotation_euler = (center - cam.location).to_track_quat('-Z', 'Y').to_euler()
        filename = ''.join(c if c.isalnum() or c in '_-' else '_' for c in name) + '_' + view + '.png'
        scene.render.filepath = str(out / filename)
        bpy.ops.render.render(write_still=True, scene=scene.name)
        report['renders'].append({'name': name, 'view': view, 'file': filename,
                                  'objects': [o.name for o in candidates], 'renderer': 'Workbench texture diagnostic; not UE/PBR acceptance'})
    bpy.data.scenes.remove(scene)
(out / 'weapon_library_inventory.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
