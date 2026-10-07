"""One authorized local FP sleeve weight experiment; unchanged geometry/rig/fingers."""
import bpy, hashlib, json, os, traceback
import numpy as np
from pathlib import Path
from mathutils import Quaternion, Vector

ROOT=Path(__file__).resolve().parents[3]
STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
OUT=STORE/'Evidence/ReloadRepairV5'/os.environ.get('CS549_RELOAD_SLEEVE_ID','sleeve_weights_offline_v1')
assert not OUT.exists();OUT.mkdir(parents=True)
(OUT/'source.py').write_bytes(Path(__file__).read_bytes())
FBX=STORE/'Evidence/ContinuousArmsV3/exchange_v1/SK_PC_ContinuousArmsV3.fbx'
AUDIT=STORE/'Evidence/ReloadSleeveAdaptationV2/bone_audit_v1/result.json'
DIRECT=STORE/'Evidence/ReloadSleeveAdaptationV2/skin_probe_v3/result.json'
r={'scope':__doc__,'errors':[],'native_changed':False,'visual_acceptance':False,
   'rule':'Only spine_03 share -> existing dominant same-side upperarm influence, |X|>=18 Z125..150cm; no distal influences.',
   'limits':['Recorded raw phase transforms may differ from native translation retarget modes.',
             'Offline clay comparison does not clear actual FP camera/contact or gameplay.']}
hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (FBX,AUDIT,DIRECT)}

def matrix(t):
    if 't' in t:t={'translation':t['t'],'rotation':t['q'],'scale':t['s']}
    x,y,z,w=t['rotation'];m=Quaternion((w,x,y,z)).to_matrix().to_4x4()
    for j in range(3):
        for i in range(3):m[i][j]*=t['scale'][j]
    m.translation=Vector(t['translation']);return np.array(m,dtype=float)

def mesh_snapshot(o):
    return {'vertices':[list(o.matrix_world@v.co) for v in o.data.vertices],
       'faces':[list(p.vertices) for p in o.data.polygons],
       'material_indices':[p.material_index for p in o.data.polygons],
       'materials':[m.name for m in o.data.materials],
       'uvs':[[list(x.uv) for x in layer.data] for layer in o.data.uv_layers],
       'weights':[{o.vertex_groups[g.group].name:float(g.weight) for g in v.groups if g.weight>1e-6} for v in o.data.vertices]}

def skeleton(rig):
    return {b.name:{'parent':b.parent.name if b.parent else None,
            'matrix':[list(row) for row in rig.matrix_world@b.matrix_local]} for b in rig.data.bones}

def skin(pos,weights,deform):
    h=np.column_stack([pos,np.ones(len(pos))]);result=np.zeros_like(pos)
    for i,ws in enumerate(weights):
        assert abs(sum(ws.values())-1)<.001 and len(ws)<=4
        for n,w in ws.items():result[i]+=w*(deform[n]@h[i])[:3]
        result[i]/=sum(ws.values())
    return result

def edges_metric(pos,posed,edges):
    rest=np.linalg.norm(pos[edges[:,0]]-pos[edges[:,1]],axis=1)
    cur=np.linalg.norm(posed[edges[:,0]]-posed[edges[:,1]],axis=1);valid=rest>.05
    return {'max_extra_cm':float((cur-rest)[valid].max()),
            'p99_ratio':float(np.percentile(cur[valid]/rest[valid],99)),
            'over3x_extra2cm':int(np.sum(valid&(cur>3*rest)&(cur-rest>2)))}

try:
    assert hashes[str(FBX.relative_to(ROOT))]=='1eca576ef40357af58ecdc315b1006ed6a25140932555c04d72df2fa7c686bb9'
    audit=json.loads(AUDIT.read_text());direct=json.loads(DIRECT.read_text())
    assert not audit['errors'] and not direct.get('errors',[]);model=audit['models']['owner']
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(FBX),automatic_bone_orientation=False,use_anim=False,use_custom_normals=True)
    rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
    meshes=[o for o in bpy.data.objects if o.type=='MESH'];assert len(meshes)==1
    o=meshes[0];before=mesh_snapshot(o);bones=skeleton(rig)
    names=[n for n in model['ref_component'] if n in rig.data.bones]
    src=np.array([list(rig.matrix_world@rig.data.bones[n].head_local)+[1] for n in names])
    dst=np.array([model['ref_component'][n]['translation'] for n in names]);fit=np.linalg.lstsq(src,dst,rcond=None)[0]
    r['rest_alignment_max_cm']=float(np.linalg.norm(src@fit-dst,axis=1).max());assert r['rest_alignment_max_cm']<.01
    pos=np.column_stack([np.array(before['vertices']),np.ones(len(before['vertices']))])@fit
    selected=[]
    for i,w in enumerate(before['weights']):
        if not (abs(pos[i,0])>=18 and 125<=pos[i,2]<=150 and w.get('spine_03',0)>1e-6):continue
        if any(any(k in n for k in ('lowerarm','hand','thumb','index','middle','ring','pinky')) for n in w):continue
        sides=[s for s in ('l','r') if any(n.startswith('upperarm') and n.endswith('_'+s) for n in w)]
        if len(sides)!=1:continue
        arm={n:x for n,x in w.items() if n.startswith('upperarm') and n.endswith('_'+sides[0])}
        target=max(arm,key=arm.get);amount=w['spine_03']
        o.vertex_groups[target].add([i],w[target]+amount,'REPLACE');o.vertex_groups['spine_03'].remove([i])
        selected.append({'vertex':i,'position_cm':pos[i].tolist(),'target':target,'transferred':amount})
    assert selected,'No authorized sleeve vertices selected'
    after=mesh_snapshot(o)
    assert all(before[k]==after[k] for k in before if k!='weights') and bones==skeleton(rig)
    changed={x['vertex'] for x in selected}
    assert all(before['weights'][i]==after['weights'][i] for i in range(len(pos)) if i not in changed)
    r['selected']=selected;r['selected_count']=len(selected)
    r['finger_hand_weights_exact']=all(before['weights'][i]==after['weights'][i] for i,w in enumerate(before['weights']) if any(any(k in n for k in ('hand','thumb','index','middle','ring','pinky')) for n in w))
    assert r['finger_hand_weights_exact'];r['geometry_uv_material_rig_exact']=True
    edges=np.array([list(e.vertices) for e in o.data.edges]);ref={n:matrix(t) for n,t in model['ref_component'].items()}
    inv={n:np.linalg.inv(t) for n,t in ref.items()};r['phases']=[];views=[]
    samples=[('reload_'+phase,raw,False) for phase,raw in audit['clips']['failed']['samples'].items()]
    samples+=[('actual_2_20',direct['components']['owner']['bones_component'],True)]
    for label,raw,actual in samples:
        component={}
        def bone(n):
            if n not in component:
                local=matrix(raw.get(n,model['ref_local'][n]));parent=model['parents'][n]
                component[n]=bone(parent)@local if parent in ref else local
            return component[n]
        deform={n:(matrix(raw[n]) if actual else bone(n))@inv[n] for n in ref}
        a=skin(pos,before['weights'],deform);b=skin(pos,after['weights'],deform)
        r['phases'].append({'phase':label,'before':edges_metric(pos,a,edges),'after':edges_metric(pos,b,edges)})
        views.append((label,a,b))
    actual=next(x for x in r['phases'] if x['phase']=='actual_2_20')
    r['early_edge_gate']=actual['after']['over3x_extra2cm']<=actual['before']['over3x_extra2cm']*.5 and all(x['after']['max_extra_cm']<=x['before']['max_extra_cm']+1e-5 for x in r['phases'])
    bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);o.select_set(True);bpy.context.view_layer.objects.active=rig
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'SleeveWeightsV5.blend'))
    bpy.ops.export_scene.fbx(filepath=str(OUT/'SK_PC_SleeveWeightsV5.fbx'),use_selection=True,object_types={'ARMATURE','MESH'},add_leaf_bones=False,bake_anim=False,mesh_smooth_type='OFF',path_mode='RELATIVE',use_mesh_modifiers=False)
    (OUT/'expected.json').write_text(json.dumps({'mesh':after,'bones':bones})+'\n')
    # Render-only explicit skin replicas. They never enter exported mesh or source blend.
    bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene
    scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=900;scene.render.resolution_y=650;scene.render.resolution_percentage=100
    scene.world.color=(.06,.06,.06);shade=scene.display.shading;shade.light='STUDIO';shade.color_type='MATERIAL';shade.show_shadows=True;shade.show_cavity=True;shade.background_type='WORLD'
    material=bpy.data.materials.new('diagnostic_clay');material.diffuse_color=(.53,.58,.63,1)
    data=bpy.data.meshes.new('render_only');data.from_pydata(pos.tolist(),[],before['faces']);data.materials.append(material)
    display=bpy.data.objects.new('render_only_skin',data);scene.collection.objects.link(display)
    camdata=bpy.data.cameras.new('diagnostic');camera=bpy.data.objects.new('diagnostic',camdata);scene.collection.objects.link(camera);scene.camera=camera;camdata.type='ORTHO';camdata.ortho_scale=85
    center=Vector((0,0,140));r['renders']=[]
    views=[('neutral',pos,pos)]+views
    directions={'front':(0,-180,0),'profile':(180,0,0),'back':(0,180,0),'three_quarter':(130,-130,40)}
    for label,a,b in views:
        for angle in (directions if label=='neutral' else ('front','profile')):
            camera.location=center+Vector(directions[angle]);camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
            for version,points in (('before',a),('after',b)):
                for v,p in zip(data.vertices,points):v.co=Vector(p)
                data.update();name=label+'_'+angle+'_'+version+'.png';scene.render.filepath=str(OUT/name)
                bpy.ops.render.render(write_still=True);r['renders'].append(name)
    r['status']='offline_numeric_gate_pass_visual_and_fresh_import_pending' if r['early_edge_gate'] else 'failed_single_rule_stop_no_native_import'
except Exception:r['errors'].append(traceback.format_exc());r['status']='failed_preserve_stop'
finally:
    r['inputs_unchanged']=all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items());r['input_hashes']=hashes
    r['artifacts']=[{'file':p.name,'size_bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in OUT.iterdir() if p.suffix in ('.fbx','.blend')]
    (OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n')
    print('CS549_SLEEVE_WEIGHTS',json.dumps({k:r[k] for k in ('status','errors','inputs_unchanged')}))
