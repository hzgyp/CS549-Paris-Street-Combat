"""Offline actual index/gun surface review. Read-only source; no production mesh/pose edits."""
import bpy,hashlib,json,os,traceback
import numpy as np
from pathlib import Path
from mathutils import Matrix,Quaternion,Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[3]
STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
OUT=STORE/'Evidence/ReloadIndexContactV6'/os.environ.get('CS549_INDEX_OFFLINE_ID','surface_audit_v1')
assert not OUT.exists();OUT.mkdir(parents=True)
(OUT/'source.py').write_bytes(Path(__file__).read_bytes())
FBX=STORE/'Evidence/ContinuousArmsV3/exchange_v1/SK_PC_ContinuousArmsV3.fbx'
NATIVE=STORE/'Evidence/ReloadIndexContactV6/contact_exchange_v1'
AUDIT=STORE/'Evidence/ReloadSleeveAdaptationV2/bone_audit_v1/result.json'
DIRECT=STORE/'Evidence/ReloadSleeveAdaptationV2/skin_probe_v3/result.json'
CALIB=STORE/'Evidence/ReloadContactBindingV3/binding_proof_author_v2/result.json'
inputs=(FBX,NATIVE/'Sm_M1_Garand.fbx',NATIVE/'result.json',AUDIT,DIRECT,CALIB)
hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
r={'scope':__doc__,'status':'starting','errors':[],'phases':[],'views':[],
   'native_or_source_modified':False,'limitations':['Clay diagnostic cutouts do not modify production geometry.',
   'Compressed single-clip poses and fixed native reload attachment, not actual transition blend/owner framing.',
   'Surface crossing is measured; signed nearest distance alone is not solid containment for open meshes.']}
def write():(OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n')
def mat(t):
    if 'translation' in t:t={'t':t['translation'],'q':t['rotation'],'s':t['scale']}
    x,y,z,w=t['q'];m=Quaternion((w,x,y,z)).to_matrix().to_4x4()
    for j in range(3):
        for i in range(3):m[i][j]*=t.get('s',[1,1,1])[j]
    m.translation=Vector(t['t']);return np.array(m,dtype=float)
def skin(p,ws,deform):
    h=np.column_stack([p,np.ones(len(p))]);out=np.zeros_like(p)
    for i,w in enumerate(ws):
        for name,weight in w.items():out[i]+=weight*(deform[name]@h[i])[:3]
        out[i]/=sum(w.values())
    return out
def material(name,color):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    n=m.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(*color,1);n.inputs['Roughness'].default_value=.65
    return m
def create_mesh(name,p,faces):
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(p.tolist(),[],faces);mesh.update()
    o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);return o
def camera(target,delta,scale):
    c=bpy.context.scene.camera;c.location=Vector(target)+Vector(delta)
    c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=scale
def crosses(a,b,t):
    v0,v1,v2=t;d=b-a;e1=v1-v0;e2=v2-v0;p=np.cross(d,e2);det=np.dot(e1,p)
    if abs(det)<1e-10:return False
    f=1/det;s=a-v0;u=f*np.dot(s,p)
    if u<-1e-7 or u>1+1e-7:return False
    q=np.cross(s,e1);v=f*np.dot(d,q)
    if v<-1e-7 or u+v>1+1e-7:return False
    z=f*np.dot(e2,q);return -1e-7<=z<=1+1e-7
def intersecting(index_points,index_triangles,gun_points,gun_triangles,gbvh):
    tree=BVHTree.FromPolygons([Vector(x) for x in index_points],index_triangles,all_triangles=True,epsilon=0)
    found=set()
    for ia,ib in tree.overlap(gbvh):
        a=index_points[index_triangles[ia]];b=gun_points[gun_triangles[ib]]
        if any(crosses(a[j],a[(j+1)%3],b) or crosses(b[j],b[(j+1)%3],a) for j in range(3)):found.add(ia)
    return len(found)
try:
    data=json.loads((NATIVE/'result.json').read_text());assert not data['errors'] and data['protected_current528_unchanged']
    model=json.loads(AUDIT.read_text())['models']['owner']
    direct=json.loads(DIRECT.read_text())['components']['owner']['bones_component']
    poses=data['clips']['owner_reload']['samples']
    r['compressed_vs_recorded_native_2_2_max_bone_position_cm']=max(np.linalg.norm(mat(v)[:3,3]-mat(direct[n])[:3,3]) for n,v in poses['2.2']['bones_component'].items() if n in direct)
    r['compressed_vs_sleeve_copy_max_bone_position_cm']=max(np.linalg.norm(mat(v)[:3,3]-mat(data['clips']['sleeve_copy_reload']['samples'][phase]['bones_component'][n])[:3,3]) for phase,row in poses.items() for n,v in row['bones_component'].items())
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(FBX),automatic_bone_orientation=False,use_anim=False,use_custom_normals=True)
    rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');source=next(o for o in bpy.data.objects if o.type=='MESH')
    names=[n for n in model['ref_component'] if n in rig.data.bones]
    src=np.array([list(rig.matrix_world@rig.data.bones[n].head_local)+[1] for n in names])
    dst=np.array([model['ref_component'][n]['translation'] for n in names]);fit=np.linalg.lstsq(src,dst,rcond=None)[0]
    r['rest_alignment_max_cm']=float(np.linalg.norm(src@fit-dst,axis=1).max());assert r['rest_alignment_max_cm']<.01
    r['coordinate_fit']=fit.tolist()
    original=np.array([list(source.matrix_world@v.co)+[1] for v in source.data.vertices])@fit
    weights=[{source.vertex_groups[g.group].name:float(g.weight) for g in v.groups if g.weight>1e-6} for v in source.data.vertices]
    assert all(abs(sum(w.values())-1)<.001 for w in weights)
    keep=[i for i,w in enumerate(weights) if sum(v for n,v in w.items() if n=='hand_r' or (n.endswith('_r') and n.startswith(('index_','middle_','ring_','pinky_','thumb_'))))>.5]
    remap={i:j for j,i in enumerate(keep)};hand_faces=[[remap[i] for i in f.vertices] for f in source.data.polygons if all(i in remap for i in f.vertices)]
    index_mask=[sum(v for n,v in weights[i].items() if n.startswith('index_') and n.endswith('_r'))>.1 for i in keep]
    index_faces=[f for f in hand_faces if all(index_mask[i] for i in f)]
    index_triangles=np.array([(f[0],f[i],f[i+1]) for f in index_faces for i in range(1,len(f)-1)],dtype=int)
    r['hand_vertices']=len(keep);r['hand_faces']=len(hand_faces);r['index_surface_triangles']=len(index_triangles)
    source.hide_render=True;rig.hide_render=True
    existing=set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=str(NATIVE/'Sm_M1_Garand.fbx'),automatic_bone_orientation=False,use_anim=False,use_custom_normals=True)
    gun_objects=[o for o in bpy.data.objects if o not in existing and o.type=='MESH'];assert gun_objects
    gun_points=[];gun_tri=[]
    for o in gun_objects:
        base=len(gun_points);local=np.array([list(o.matrix_world@v.co)+[1] for v in o.data.vertices])@fit
        gun_points.extend(local.tolist())
        o.data.calc_loop_triangles();gun_tri.extend([[base+i for i in t.vertices] for t in o.data.loop_triangles]);o.hide_render=True
    gun_points=np.array(gun_points);gun_tri=np.array(gun_tri,dtype=int)
    r['gun_bounds_cm']={'min':gun_points.min(axis=0).tolist(),'max':gun_points.max(axis=0).tolist()};r['gun_triangles']=len(gun_tri)
    assert 80<np.ptp(gun_points[:,1])<130 and max(np.ptp(gun_points[:,0]),np.ptp(gun_points[:,2]))<30,'M1 coordinate/scale gate'
    grey=material('Gun diagnostic only',(.14,.17,.20));tan=material('Hand diagnostic only',(.65,.46,.29));orange=material('Index highlight only',(1.,.20,.025))
    gun=create_mesh('Actual M1 geometry',gun_points*.01,gun_tri.tolist());gun.data.materials.append(grey)
    gbvh=BVHTree.FromPolygons([Vector(x) for x in gun_points],gun_tri.tolist(),all_triangles=True,epsilon=0)
    cdata=bpy.data.cameras.new('Contact camera');c=bpy.data.objects.new('Contact camera',cdata);bpy.context.collection.objects.link(c);bpy.context.scene.camera=c;cdata.type='ORTHO';cdata.lens=50
    scene=bpy.context.scene;engines=scene.render.bl_rna.properties['engine'].enum_items.keys()
    scene.render.engine='BLENDER_EEVEE' if 'BLENDER_EEVEE' in engines else 'BLENDER_EEVEE_NEXT'
    scene.render.resolution_x=1000;scene.render.resolution_y=800;scene.render.resolution_percentage=100
    scene.world=bpy.data.worlds.new('Diagnostic world');scene.world.use_nodes=True;scene.world.node_tree.nodes.get('Background').inputs[0].default_value=(.18,.18,.18,1);scene.world.node_tree.nodes.get('Background').inputs[1].default_value=.5
    for name,location,power in [('Key',(.4,-.3,.6),17.5),('Fill',(-.4,.2,.35),10)]:
        l=bpy.data.lights.new(name,'AREA');l.energy=power;l.shape='DISK';l.size=.7;o=bpy.data.objects.new(name,l);bpy.context.collection.objects.link(o);o.location=location;o.rotation_euler=(Vector((0,-.08,0))-o.location).to_track_quat('-Z','Y').to_euler()
    scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
    inverse_ref={n:np.linalg.inv(mat(t)) for n,t in model['ref_component'].items()}
    relative=mat(json.loads(CALIB.read_text())['audit_phase0_hand_relative'])
    if os.environ.get('CS549_INDEX_CALIB_TARGET')=='1':
        b0={n:mat(t) for n,t in poses['0.0']['bones_component'].items()}
        def hollow(side):
            fingers=('middle','ring','pinky','thumb') if side=='r' else ('index','middle','ring','pinky','thumb')
            return np.mean([b0[f+'_0'+str(i)+'_'+side][:3,3] for f in fingers for i in (2,3)],axis=0)
        right,left=hollow('r'),hollow('l');d=left-right
        yaw=np.arctan2(d[1],d[0])-np.pi/2;pitch=np.arctan2(d[2],np.hypot(d[0],d[1]))
        rz=np.array([[np.cos(yaw),-np.sin(yaw),0],[np.sin(yaw),np.cos(yaw),0],[0,0,1]])
        rx=np.array([[1,0,0],[0,np.cos(pitch),-np.sin(pitch)],[0,np.sin(pitch),np.cos(pitch)]])
        candidate=np.eye(4);candidate[:3,:3]=rz@rx;candidate[:3,3]=right-candidate[:3,:3]@np.array([-.5,-8.,0.])
        newrelative=np.linalg.inv(b0['hand_r'])@candidate
        r['single_target_calibration']={'method':'Same V3 two-hollow rule/anchor, applied to actual target at phase0; no parameter search',
          'old_relative_matrix':relative.tolist(),'new_relative_matrix':newrelative.tolist(),
          'right_hollow_cm':right.tolist(),'left_hollow_cm':left.tolist(),
          'translation_change_cm':float(np.linalg.norm(newrelative[:3,3]-relative[:3,3]))}
        relative=newrelative;poses={k:poses[k] for k in ('0.0','2.2','4.1')}
    preview=None
    for phase,row in poses.items():
        bones={n:mat(t) for n,t in row['bones_component'].items()};deform={n:bones[n]@inverse_ref[n] for n in inverse_ref if n in bones}
        posed=skin(original,weights,deform);gun_transform=bones['hand_r']@relative;inverse_gun=np.linalg.inv(gun_transform)
        hand_gun=(np.column_stack([posed[keep],np.ones(len(keep))])@inverse_gun.T)[:,:3]
        idx_ids=np.where(index_mask)[0];nearest=[];signed=[]
        for p in hand_gun[idx_ids]:
            loc,normal,_,distance=gbvh.find_nearest(Vector(p));nearest.append(float(distance));signed.append(float((Vector(p)-loc).dot(normal)))
        crossings=intersecting(hand_gun,index_triangles,gun_points,gun_tri,gbvh)
        phase_result={'phase_s':row['phase'],'surface_crossing_index_triangles':crossings,'nearest_min_cm':min(nearest),
          'negative_nearest_normal_vertex_count':sum(d<-.02 for d in signed),'negative_normal_max_cm':max(0,-min(signed)),
          'index_bones_gun_local_cm':{n:(inverse_gun@np.r_[bones[n][:3,3],1])[:3].tolist() for n in ('index_01_r','index_02_r','index_03_r')},
          'hand_relative_gun_transform':{'t':relative[:3,3].tolist()},'gun_attachment_is_constant_in_hand_frame':True}
        r['phases'].append(phase_result);write()
        if preview:bpy.data.objects.remove(preview,do_unlink=True)
        preview=create_mesh('Unmodified posed right hand',hand_gun*.01,hand_faces);preview.data.materials.append(tan);preview.data.materials.append(orange)
        for p in preview.data.polygons:p.material_index=int(all(index_mask[i] for i in p.vertices))
        target=np.mean(hand_gun[idx_ids],axis=0)*.01
        for view,delta in [('right',(.28,-.05,.10)),('left',(-.28,-.05,.10)),('top',(.02,-.04,.30))]:
            camera(target,delta,.22);file='phase_'+phase+'_'+view+'.png';scene.render.filepath=str(OUT/file);bpy.ops.render.render(write_still=True)
            r['views'].append({'file':file,'phase_s':row['phase'],'view':view,'diagnostic_only':True});write()
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'IndexContactDiagnosis.blend'))
    r['status']='surface_crossing_and_views_collected_requires_inspection_no_repair_authored'
except Exception:r['status']='failed_offline_contact_gate';r['errors'].append(traceback.format_exc())
finally:
    r['inputs_unchanged']=all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items());r['input_hashes']=hashes;write()
    print(json.dumps({k:r[k] for k in ('status','errors','inputs_unchanged')}))
