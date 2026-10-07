"""Original-material orthographic presentation of immutable frozen V16 meshes."""
import argparse
import hashlib
import json
import sys
import traceback
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
STORE = ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
LAB = ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/character-ue582-v1/Evidence/Repair20261001'
BASE = STORE/'Evidence/WeaponTexturedViewsV17'
FROZEN = STORE/'Evidence/WeaponMarkedGripV16/marked_raise_v1/FixedMarkedGripMuzzleRaise.blend'
ARM = STORE/'Evidence/ContinuousArmsV3/exchange_v1/SK_PC_ContinuousArmsV3.fbx'
GUN = STORE/'Evidence/ReloadIndexContactV6/contact_exchange_v1/Sm_M1_Garand.fbx'
SOURCE = BASE/'presentation_v1'
parser = argparse.ArgumentParser()
parser.add_argument('--fresh',action='store_true')
args = parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
OUT = BASE/('fresh_v1' if args.fresh else 'presentation_v1')
assert not OUT.exists(), 'Never overwrite an inspection identity'
OUT.mkdir(parents=True)
r = {'errors':[], 'scope':__doc__, 'native_authored':False, 'pose_changed':False,
     'native_ue_shader_parity':False, 'renders':[]}
inputs = [FROZEN, ARM, GUN, LAB/'Exchange/SK_M1_Garand.blend',
          LAB/'Exchange/SK_WWII_US_Paratrooper_simple.blend', Path(__file__)]

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def write():
    (OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')

def guards():
    rows = json.loads((STORE/'Evidence/ReloadIndexContactV6/map_recovery_v1/result.json').read_text())['files']
    bad = [x['path'] for x in rows if not (ROOT/x['path']).is_file()
           or (ROOT/x['path']).stat().st_size!=x['size_bytes'] or sha(ROOT/x['path'])!=x['sha256']]
    return {'checked':len(rows),'mismatches':bad}

def snapshot(obj):
    mesh = obj.data
    return {'vertices_m':np.array([list(obj.matrix_world@v.co) for v in mesh.vertices]),
            'triangles':np.array([list(p.vertices) for p in mesh.polygons],int)}

def source_uv(file):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(file),automatic_bone_orientation=False,use_anim=False)
    obj = next(o for o in bpy.data.objects if o.type=='MESH')
    mesh = obj.data
    mesh.calc_loop_triangles()
    triangles = list(mesh.loop_triangles)
    return {'triangles':np.array([list(t.vertices) for t in triangles],int),
            'slots':np.array([t.material_index for t in triangles]),
            'smooth':[mesh.polygons[t.polygon_index].use_smooth for t in triangles],
            'material_names':[m.name for m in mesh.materials],
            'uvs':{u.name:np.array([[list(u.data[i].uv) for i in t.loops] for t in triangles])
                   for u in mesh.uv_layers},
            'active_uv':mesh.uv_layers.active.name,
            'render_uv':next(u.name for u in mesh.uv_layers if u.active_render)}

def make(name, frozen, source, materials, slot_map):
    assert np.array_equal(frozen['triangles'],source['triangles'][:,::-1]), 'Triangle/corner mapping differs'
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(frozen['vertices_m'].tolist(),[],frozen['triangles'].tolist())
    mesh.update()
    obj = bpy.data.objects.new(name,mesh)
    bpy.context.scene.collection.objects.link(obj)
    for mat in materials:
        mesh.materials.append(mat)
    for p,slot,smooth in zip(mesh.polygons,source['slots'],source['smooth']):
        assert int(slot) in slot_map, ('Unmapped material slot',int(slot))
        p.material_index = slot_map[int(slot)]
        p.use_smooth = smooth
    for name,values in source['uvs'].items():
        uv = mesh.uv_layers.new(name=name)
        flat = values[:,::-1,:].reshape(-1,2)
        assert len(flat)==len(uv.data)
        for item,value in zip(uv.data,flat):
            item.uv = value
        uv.active_render = name==source['render_uv']
    mesh.uv_layers.active_index = mesh.uv_layers.find(source['active_uv'])
    error = float(np.max(np.linalg.norm(snapshot(obj)['vertices_m']-frozen['vertices_m'],axis=1)))*100
    assert error<.0001
    r.setdefault('geometry_max_delta_cm',{})[obj.name] = error
    return obj

def material_append(file,names):
    with bpy.data.libraries.load(str(file),link=False) as (src,dst):
        assert all(n in src.materials for n in names)
        dst.materials = names
    return list(dst.materials)

def attributes(objects):
    rows = []
    for obj in objects:
        mesh = obj.data
        rows.append({'name':obj.name,'vertices':len(mesh.vertices),'triangles':len(mesh.polygons),
                     'position_sha256':hashlib.sha256(np.array([list(v.co) for v in mesh.vertices],dtype=np.float64).tobytes()).hexdigest(),
                     'triangle_sha256':hashlib.sha256(np.array([list(p.vertices) for p in mesh.polygons],dtype=np.int64).tobytes()).hexdigest(),
                     'material_slots':[m.name for m in mesh.materials],
                     'material_indices_sha256':hashlib.sha256(np.array([p.material_index for p in mesh.polygons],dtype=np.int64).tobytes()).hexdigest(),
                     'uv':{u.name:hashlib.sha256(np.array([list(x.uv) for x in u.data],dtype=np.float64).tobytes()).hexdigest() for u in mesh.uv_layers},
                     'render_uv':next(u.name for u in mesh.uv_layers if u.active_render)})
    return rows

try:
    hashes = {str(p.relative_to(ROOT)):sha(p) for p in inputs}
    r['guards_before'] = guards()
    assert not r['guards_before']['mismatches']
    if args.fresh:
        previous = json.loads((SOURCE/'result.json').read_text())
        assert not previous['errors']
        blend = SOURCE/'TexturedV16Inspection.blend'
        r['blend_sha256_before'] = sha(blend)
        bpy.ops.wm.open_mainfile(filepath=str(blend),load_ui=False,use_scripts=False)
        meshes = sorted([o for o in bpy.context.scene.objects if o.type=='MESH'],key=lambda o:o.name)
        actual = attributes(meshes)
        assert actual==previous['mesh_attributes'], 'Fresh geometry/UV/material indices differ'
        r['mesh_attributes'] = actual
        for row in previous['images']:
            image = bpy.data.images[row['name']]
            assert list(image.size)==row['size'] and image.size[0]>0
            path = Path(bpy.path.abspath(image.filepath)).resolve()
            assert str(path.relative_to(ROOT))==row['path'] and sha(path)==row['sha256']
            assert image.colorspace_settings.name==row['color_space']
        assert sha(blend)==r['blend_sha256_before']
        r['status'] = 'fresh_geometry_uv_material_images_verified'
        r['checked_images'] = len(previous['images'])
    else:
        assert hashes[str(FROZEN.relative_to(ROOT))]=='a315ac196dc5b315b2fab9ed38074edc47582f90ffbe013a29d1cca253aa488f'
        bpy.ops.wm.open_mainfile(filepath=str(FROZEN),load_ui=False,use_scripts=False)
        frozen = {'arms':snapshot(bpy.data.objects['Continuous arms raised_v16']),
                  'gun':snapshot(bpy.data.objects['Rifle raised_v16'])}
        arm_uv,gun_uv = source_uv(ARM),source_uv(GUN)
        assert len(frozen['arms']['vertices_m'])==6135 and len(frozen['gun']['vertices_m'])==2131
        assert set(arm_uv['slots'])=={2,8} and set(gun_uv['slots'])=={0}
        r['source_uv_names'] = {'arms':list(arm_uv['uvs']),'gun':list(gun_uv['uvs'])}
        r['source_slot_names'] = {'arms':arm_uv['material_names'],'gun':gun_uv['material_names']}
        bpy.ops.wm.read_factory_settings(use_empty=True)
        gun_mat = material_append(inputs[3],['MI_M1_Garand_portable'])
        arms_mat = material_append(inputs[4],['M_USParatrooperJacket_portable','MI_USParatrooper_feceA_portable'])
        # Import exact donor graphs, including the existing DX-green shader conversion.
        probe = json.loads((BASE/'source_probe_v1/result.json').read_text())
        lookup = {i['name']:Path(i['file']).resolve() for row in probe['sources'][2:]
                  for material in row['materials'] for i in material['images']}
        for image in bpy.data.images:
            assert image.name in lookup
            image.filepath = str(lookup[image.name])
            image.reload()
            assert image.size[0]>0
        assert len(bpy.data.images)==9
        images = []
        for image in bpy.data.images:
            path = Path(image.filepath).resolve()
            hashes[str(path.relative_to(ROOT))] = sha(path)
            images.append({'name':image.name,'path':str(path.relative_to(ROOT)),
                           'sha256':sha(path),'size':list(image.size),
                           'color_space':image.colorspace_settings.name})
        rifle = make('Frozen V16 M1',frozen['gun'],gun_uv,gun_mat,{0:0})
        arms = make('Frozen V16 continuous arms',frozen['arms'],arm_uv,arms_mat,{2:0,8:1})
        r['images'] = images
        r['mesh_attributes'] = attributes(sorted([rifle,arms],key=lambda o:o.name))
        r['material_graphs'] = [{'name':m.name,'native_material':m['native_material'],
                                 'nodes':len(m.node_tree.nodes),'links':len(m.node_tree.links)}
                                for m in gun_mat+arms_mat]
        r['early_gate_passed'] = True
        scene = bpy.context.scene
        scene.render.engine = 'BLENDER_EEVEE'
        scene.render.resolution_x,scene.render.resolution_y = 1400,1200
        scene.render.resolution_percentage = 100
        scene.render.image_settings.file_format = 'PNG'
        scene.view_settings.view_transform = 'AgX'
        scene.view_settings.look = 'AgX - Medium High Contrast'
        scene.view_settings.exposure = 0
        scene.world = bpy.data.worlds.new('Neutral material studio')
        scene.world.use_nodes = True
        bg = scene.world.node_tree.nodes['Background']
        bg.inputs[0].default_value = (.12,.12,.12,1)
        bg.inputs[1].default_value = .65
        center = Vector((-.035,-.02,-.025))
        for name,pos,power,size in [('Key',(.4,-.3,.6),18,.55),('Fill',(-.4,.2,.35),12,.65),('Rim',(0,.35,.4),8,.45)]:
            data = bpy.data.lights.new(name,'AREA')
            data.energy,data.size = power,size
            obj = bpy.data.objects.new(name,data)
            scene.collection.objects.link(obj)
            obj.location = pos
            obj.rotation_euler = (center-obj.location).to_track_quat('-Z','Y').to_euler()
        views = [('front_trigger_side',(.6,0,0)),('side_stock_end',(0,-.6,0)),('top',(0,0,.6))]
        cams = []
        for name,direction in views+[('whole_arms_context',(-1.2,-.1,.45))]:
            target,scale = (Vector((0,.12,-.1)),1.2) if name=='whole_arms_context' else (center,.26)
            data = bpy.data.cameras.new(name)
            data.type,data.ortho_scale,data.clip_start = 'ORTHO',scale,.001
            cam = bpy.data.objects.new(name,data)
            scene.collection.objects.link(cam)
            cam.location = target+Vector(direction)
            cam.rotation_euler = (target-cam.location).to_track_quat('-Z','Y').to_euler()
            scene.camera = cam
            scene.render.filepath = str(OUT/(name+'.png'))
            bpy.ops.render.render(write_still=True)
            r['renders'].append({'view':name,'path':name+'.png','target_m':list(target),
                                'camera_offset_m':list(direction),'ortho_scale_m':scale,
                                'sha256':sha(OUT/(name+'.png'))})
            cams.append(cam)
            write()
        scene.camera = cams[0]
        bpy.context.preferences.filepaths.save_version = 0
        bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'TexturedV16Inspection.blend'))
        r['blend_sha256'] = sha(OUT/'TexturedV16Inspection.blend')
        r['status'] = 'three_textured_orthographic_views_and_context_rendered'
    r['input_hashes'] = hashes
    r['inputs_unchanged'] = all(sha(ROOT/k)==v for k,v in hashes.items())
    assert r['inputs_unchanged']
except Exception:
    r['status'] = 'stopped'
    r['errors'].append(traceback.format_exc())
finally:
    r['guards_after'] = guards()
    write()
    print(json.dumps({k:r.get(k) for k in ('status','errors','geometry_max_delta_cm','early_gate_passed','inputs_unchanged','guards_after','checked_images')}),flush=True)
    if r['errors'] or r['guards_after']['mismatches']:
        raise SystemExit(1)
