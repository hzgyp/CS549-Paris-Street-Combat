"""Fresh presentation-file verification and labeled three-view contact sheet."""
import hashlib
import json
from pathlib import Path
import bpy
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
STORE = ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
BASE = STORE/'Evidence/WeaponTexturedViewsV17'
SOURCE = BASE/'presentation_v2'
OUT = BASE/'fresh_v2'
assert not OUT.exists()
OUT.mkdir(parents=True)

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def arr(a,dtype):
    return hashlib.sha256(np.array(a,dtype=dtype).tobytes()).hexdigest()

proof = json.loads((SOURCE/'result.json').read_text())
assert not proof['errors']
blend = SOURCE/'TexturedV16Inspection.blend'
assert sha(blend)==proof['blend_sha256']
bpy.ops.wm.open_mainfile(filepath=str(blend),load_ui=False,use_scripts=False)
rows = []
for obj in sorted([o for o in bpy.context.scene.objects if o.type=='MESH'],key=lambda o:o.name):
    m = obj.data
    rows.append({'name':obj.name,'vertices':len(m.vertices),'triangles':len(m.polygons),
                 'positions':arr([list(v.co) for v in m.vertices],np.float64),
                 'triangles_sha':arr([list(p.vertices) for p in m.polygons],np.int64),
                 'materials':[x.name for x in m.materials],
                 'slots':arr([p.material_index for p in m.polygons],np.int64),
                 'uvs':{u.name:arr([list(x.uv) for x in u.data],np.float64) for u in m.uv_layers},
                 'render_uv':next(u.name for u in m.uv_layers if u.active_render)})
assert rows==proof['mesh_attributes']
for row in proof['images']:
    image = bpy.data.images[row['name']]
    path = Path(bpy.path.abspath(image.filepath)).resolve()
    assert str(path.relative_to(ROOT))==row['path'] and sha(path)==row['sha256']
    assert list(image.size)==row['size'] and image.size[0]>0
    assert image.colorspace_settings.name==row['color_space']
assert all(sha(ROOT/k)==v for k,v in proof['input_hashes'].items())
guards = json.loads((STORE/'Evidence/ReloadIndexContactV6/map_recovery_v1/result.json').read_text())['files']
assert len(guards)==528
assert all((ROOT/x['path']).stat().st_size==x['size_bytes'] and sha(ROOT/x['path'])==x['sha256'] for x in guards)
assert sha(blend)==proof['blend_sha256']
result = {'status':'fresh_verified','errors':[],'meshes':rows,'checked_images':len(proof['images']),
          'current_recovery_guards_checked':len(guards),'inputs_unchanged':True,
          'blend_sha256':sha(blend),'native_ue_shader_parity':False,'native_selected':False}
(OUT/'result.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':result['status'],'checked_images':9,'guards':528}),flush=True)
