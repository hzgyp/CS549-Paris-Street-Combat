"""Read-only final package closure gate; never saves, generates or refines."""
import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

import bpy


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


parser = argparse.ArgumentParser()
parser.add_argument('--blend', required=True)
parser.add_argument('--glb', required=True)
parser.add_argument('--out', required=True)
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
source, glb, out = (Path(value).resolve() for value in (args.blend, args.glb, args.out))
assert not out.exists(), 'Occupied proof identity'
expected = {
    source: 'b6c9afcd4de1675d533158bef5698e8b05e47e6226880964b241d606292f26b8',
    glb: '77f7fd8cdde8c6b0b030b7b0ed4646f6bce8b03ad47f4ecb1826b51e502b378f'}
assert all(sha(path) == value for path, value in expected.items()), 'Candidate changed'
bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False, use_scripts=False)
assert not bpy.data.libraries, 'External Blender library dependency'
assert not bpy.data.actions, 'Unexpected animations'
meshes = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
slot_materials = {slot.material for obj in meshes for slot in obj.material_slots if slot.material}
used_materials = {obj.data.materials[face.material_index] for obj in meshes for face in obj.data.polygons}
used = {node.image for mat in used_materials for node in mat.node_tree.nodes
        if node.type == 'TEX_IMAGE' and node.image}
assert len(used_materials) == 14
assert all(image.packed_file and image.size[0] > 0 for image in used), 'Unpacked/missing material image'
unpacked_other = [image.name for image in bpy.data.images
                  if image.source not in {'VIEWER', 'GENERATED'} and not image.packed_file]
assert not unpacked_other, ('Other unpacked image dependencies', unpacked_other)
assert not bpy.data.movieclips and not bpy.data.sounds and not bpy.data.cache_files
raw = glb.read_bytes()
size, kind = struct.unpack_from('<II', raw, 12)
assert raw[:4] == b'glTF' and kind == 0x4E4F534A
doc = json.loads(raw[20:20 + size])
assert all('uri' not in item for item in doc.get('buffers', []))
assert len(doc['images']) == 36 and all('bufferView' in im and 'uri' not in im for im in doc['images'])
assert all(sha(path) == value for path, value in expected.items())
report = {'passed': True, 'blender': bpy.app.version_string,
          'blend_used_materials': len(used_materials), 'blend_used_images': len(used),
          'retained_unused_material_slots': sorted(mat.name for mat in slot_materials - used_materials),
          'blend_packed_images': sum(bool(image.packed_file) for image in bpy.data.images),
          'external_libraries': 0, 'glb_embedded_images': 36, 'runtime_dependencies': [],
          'input_sha256': {str(path): value for path, value in expected.items()},
          'inputs_unchanged': True, 'ue_runtime_acceptance': False}
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print(json.dumps({key: report[key] for key in ['passed', 'blend_used_images', 'blend_packed_images', 'glb_embedded_images']}))
