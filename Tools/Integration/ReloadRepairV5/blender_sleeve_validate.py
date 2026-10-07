"""Fresh import and render frozen local sleeve experiment; no weight re-authoring."""
import bpy, hashlib, json, traceback
import numpy as np
from collections import Counter
from pathlib import Path
from mathutils import Quaternion, Vector
from mathutils.kdtree import KDTree

ROOT=Path(__file__).resolve().parents[3]
STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
BASE=STORE/'Evidence/ReloadRepairV5/sleeve_weights_offline_v2'
OUT=STORE/'Evidence/ReloadRepairV5/sleeve_weights_validate_v1';assert not OUT.exists();OUT.mkdir()
(OUT/'source.py').write_bytes(Path(__file__).read_bytes())
FBX=BASE/'SK_PC_SleeveWeightsV5.fbx'
ORIGINAL=STORE/'Evidence/ContinuousArmsV3/exchange_v1/SK_PC_ContinuousArmsV3.fbx'
frozen={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (FBX,ORIGINAL,BASE/'SleeveWeightsV5.blend')}
r={'scope':__doc__,'errors':[],'renders':[],'native_changed':False,'visual_acceptance':False}

def matrix(t):
    if 't' in t:t={'translation':t['t'],'rotation':t['q'],'scale':t['s']}
    x,y,z,w=t['rotation'];m=Quaternion((w,x,y,z)).to_matrix().to_4x4()
    for j in range(3):
        for i in range(3):m[i][j]*=t['scale'][j]
    m.translation=Vector(t['translation']);return np.array(m,dtype=float)

def read_mesh(path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(path),automatic_bone_orientation=False,use_anim=False,use_custom_normals=True)
    o=next(o for o in bpy.data.objects if o.type=='MESH');rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
    mesh={'vertices':[list(o.matrix_world@v.co) for v in o.data.vertices],
       'faces':[list(p.vertices) for p in o.data.polygons],
       'material_indices':[p.material_index for p in o.data.polygons],
       'materials':[m.name for m in o.data.materials],
       'uvs':[[list(x.uv) for x in layer.data] for layer in o.data.uv_layers],
       'weights':[{o.vertex_groups[g.group].name:float(g.weight) for g in v.groups if g.weight>1e-6} for v in o.data.vertices]}
    bones={b.name:{'parent':b.parent.name if b.parent else None,'matrix':[list(row) for row in rig.matrix_world@b.matrix_local]} for b in rig.data.bones}
    return mesh,bones

def skin(pos,weights,deform):
    h=np.column_stack([pos,np.ones(len(pos))]);result=np.zeros_like(pos)
    for i,w in enumerate(weights):
        for n,a in w.items():result[i]+=a*(deform[n]@h[i])[:3]
        result[i]/=sum(w.values())
    return result

try:
    expected=json.loads((BASE/'expected.json').read_text());result=json.loads((BASE/'result.json').read_text())
    assert result['early_edge_gate'] and result['geometry_uv_material_rig_exact'] and result['finger_hand_weights_exact']
    mesh,bones=read_mesh(FBX);e=expected['mesh'];eb=expected['bones']
    assert set(bones)==set(eb) and all(bones[n]['parent']==eb[n]['parent'] for n in bones)
    r['world_bone_matrix_max_delta']=max(abs(a-b) for n in bones for ra,rb in zip(bones[n]['matrix'],eb[n]['matrix']) for a,b in zip(ra,rb))
    assert r['world_bone_matrix_max_delta']<1e-5
    assert len(mesh['vertices'])==len(e['vertices']) and mesh['faces']==e['faces'],'Fresh topology/order differs'
    r['max_position_m']=float(np.linalg.norm(np.array(mesh['vertices'])-np.array(e['vertices']),axis=1).max())
    r['max_weight_delta']=max(abs(a.get(n,0)-b.get(n,0)) for a,b in zip(mesh['weights'],e['weights']) for n in set(a)|set(b))
    r['uv_max_delta']=max(abs(a-b) for la,lb in zip(mesh['uvs'],e['uvs']) for va,vb in zip(la,lb) for a,b in zip(va,vb))
    assert len(mesh['uvs'])==len(e['uvs']) and r['uv_max_delta']<1e-5
    assert mesh['materials']==e['materials'] and mesh['material_indices']==e['material_indices']
    assert r['max_position_m']<2e-5 and r['max_weight_delta']<1e-5
    assert all(abs(sum(w.values())-1)<.001 and len(w)<=4 for w in mesh['weights'])
    assert not bpy.data.actions;r['fresh_import_pass']=True
    original,original_bones=read_mesh(ORIGINAL)
    audit=json.loads((STORE/'Evidence/ReloadSleeveAdaptationV2/bone_audit_v1/result.json').read_text());model=audit['models']['owner']
    direct=json.loads((STORE/'Evidence/ReloadSleeveAdaptationV2/skin_probe_v3/result.json').read_text())
    rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');names=[n for n in model['ref_component'] if n in rig.data.bones]
    src=np.array([list(rig.matrix_world@rig.data.bones[n].head_local)+[1] for n in names]);dst=np.array([model['ref_component'][n]['translation'] for n in names])
    fit=np.linalg.lstsq(src,dst,rcond=None)[0];assert np.linalg.norm(src@fit-dst,axis=1).max()<.01
    pos=np.column_stack([original['vertices'],np.ones(len(original['vertices']))])@fit
    ref={n:matrix(t) for n,t in model['ref_component'].items()};inv={n:np.linalg.inv(t) for n,t in ref.items()}
    views=[('neutral',pos,pos)]
    samples=[('reload_'+p,raw,False) for p,raw in audit['clips']['failed']['samples'].items()]
    samples+=[('actual_2_20',direct['components']['owner']['bones_component'],True)]
    for label,raw,actual in samples:
        component={}
        def bone(n):
            if n not in component:
                local=matrix(raw.get(n,model['ref_local'][n]));parent=model['parents'][n]
                component[n]=bone(parent)@local if parent in ref else local
            return component[n]
        deform={n:(matrix(raw[n]) if actual else bone(n))@inv[n] for n in ref}
        views.append((label,skin(pos,original['weights'],deform),skin(pos,e['weights'],deform)))
    bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene
    scene.world=bpy.data.worlds.new('diagnostic_world');scene.world.color=(.06,.06,.06)
    scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=900;scene.render.resolution_y=650;scene.render.resolution_percentage=100
    shade=scene.display.shading;shade.light='STUDIO';shade.color_type='MATERIAL';shade.show_shadows=True;shade.show_cavity=True;shade.background_type='WORLD'
    material=bpy.data.materials.new('diagnostic_clay');material.diffuse_color=(.53,.58,.63,1)
    data=bpy.data.meshes.new('render_only');data.from_pydata(pos.tolist(),[],original['faces']);data.materials.append(material)
    display=bpy.data.objects.new('render_only_skin',data);scene.collection.objects.link(display)
    camdata=bpy.data.cameras.new('diagnostic');camera=bpy.data.objects.new('diagnostic',camdata);scene.collection.objects.link(camera);scene.camera=camera;camdata.type='ORTHO';camdata.ortho_scale=85
    center=Vector((0,0,140));directions={'front':(0,-180,0),'profile':(180,0,0),'back':(0,180,0),'three_quarter':(130,-130,40)}
    for label,a,b in views:
        for angle in (directions if label=='neutral' else ('front','profile')):
            camera.location=center+Vector(directions[angle]);camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
            for version,points in (('before',a),('after',b)):
                for v,p in zip(data.vertices,points):v.co=Vector(p)
                data.update();name=label+'_'+angle+'_'+version+'.png';scene.render.filepath=str(OUT/name)
                bpy.ops.render.render(write_still=True);r['renders'].append(name)
    r['status']='fresh_import_pass_clay_views_require_inspection'
except Exception:r['errors'].append(traceback.format_exc());r['status']='failed_preserve_stop'
finally:
    r['inputs_unchanged']=all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in frozen.items());r['input_hashes']=frozen
    (OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n');print('CS549_SLEEVE_VALIDATE',json.dumps({k:r[k] for k in ('status','errors','inputs_unchanged')}))
