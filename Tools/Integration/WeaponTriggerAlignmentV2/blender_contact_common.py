"""Offline immutable input loading and pure contact/diagnostic helpers."""
import bpy,json
import numpy as np
from pathlib import Path
from mathutils import Quaternion,Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[3]
STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
FBX=STORE/'Evidence/ContinuousArmsV3/exchange_v1/SK_PC_ContinuousArmsV3.fbx'
POSES=STORE/'Evidence/ReloadIndexContactV6/contact_exchange_v1/result.json'
AUDIT=STORE/'Evidence/ReloadSleeveAdaptationV2/bone_audit_v1/result.json'
CALIB=STORE/'Evidence/ReloadContactBindingV3/binding_proof_author_v2/result.json'
TOPOLOGY=STORE/'Evidence/WeaponTriggerAlignmentV1/topology_v1/result.json'
V1=STORE/'Evidence/WeaponTriggerAlignmentV1/trigger_fit_v1/result.json'
def mat(t):
    if 'translation' in t:t={'t':t['translation'],'q':t['rotation'],'s':t['scale']}
    x,y,z,w=t['q'];m=np.array(Quaternion((w,x,y,z)).to_matrix().to_4x4(),float)
    m[:3,:3]*=np.array(t.get('s',[1,1,1]));m[:3,3]=t['t'];return m
def transform(p,m):return (np.column_stack([p,np.ones(len(p))])@m.T)[:,:3]
def skin(p,weights,deform):
    h=np.column_stack([p,np.ones(len(p))]);out=np.zeros_like(p)
    for i,w in enumerate(weights):
        for n,v in w.items():out[i]+=v*(deform[n]@h[i])[:3]
        out[i]/=sum(w.values())
    return out
def normals(p,t):
    cross=np.cross(p[t[:,1]]-p[t[:,0]],p[t[:,2]]-p[t[:,0]]);area=np.linalg.norm(cross,axis=1)
    # FBX Blender-world -> native UE basis has NEGATIVE determinant. Cross
    # products reverse under reflection; account for the validated parity.
    return -cross/np.maximum(area[:,None],1e-12),area
def project(p,t,ids,target):
    tree=BVHTree.FromPolygons([Vector(q) for q in p],t.tolist(),all_triangles=True)
    loc,normal,idx,distance=tree.find_nearest(Vector(target));assert loc is not None
    return np.array(loc),-np.array(normal),int(ids[idx]),float(distance)
def load():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(FBX),automatic_bone_orientation=False,use_anim=False)
    rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');source=next(o for o in bpy.data.objects if o.type=='MESH')
    model=json.loads(AUDIT.read_text())['models']['owner'];names=[n for n in model['ref_component'] if n in rig.data.bones]
    src=np.array([list(rig.matrix_world@rig.data.bones[n].head_local)+[1] for n in names]);dst=np.array([model['ref_component'][n]['translation'] for n in names]);fit=np.linalg.lstsq(src,dst,rcond=None)[0]
    error=float(np.linalg.norm(src@fit-dst,axis=1).max());assert error<.01
    assert np.linalg.det(fit[:3,:])<0,'Native coordinate reflection parity must be reviewed'
    p=np.array([list(source.matrix_world@v.co)+[1] for v in source.data.vertices])@fit
    weights=[{source.vertex_groups[g.group].name:float(g.weight) for g in v.groups if g.weight>1e-6} for v in source.data.vertices]
    assert all(abs(sum(w.values())-1)<.001 for w in weights)
    source.data.calc_loop_triangles();tri=np.array([list(t.vertices) for t in source.data.loop_triangles],int)
    mask={side:np.array([sum(v for n,v in w.items() if n=='hand_'+side or (n.endswith('_'+side) and n.startswith(('index_','middle_','ring_','pinky_','thumb_'))))>.5 for w in weights]) for side in ('r','l')}
    digit={d:np.array([sum(v for n,v in w.items() if n.startswith(d+'_') and n.endswith('_r'))>.1 for w in weights]) for d in ('index','middle','ring','pinky','thumb')}
    topo=json.loads(TOPOLOGY.read_text());gp=np.array(topo['gun_points_cm']);gt=np.array(topo['gun_triangles'],int)
    poses=json.loads(POSES.read_text())['clips']['owner_reload']['samples'];invref={n:np.linalg.inv(mat(t)) for n,t in model['ref_component'].items()}
    relative=mat(json.loads(CALIB.read_text())['audit_phase0_hand_relative'])
    source.hide_render=True;rig.hide_render=True
    return dict(p=p,weights=weights,tri=tri,masks=mask,digits=digit,topo=topo,gp=gp,gt=gt,poses=poses,invref=invref,relative=relative,ref_error=error,rig=rig,source=source,model=model,coordinate_determinant=float(np.linalg.det(fit[:3,:])))
def posed(data,phase):
    bones={n:mat(t) for n,t in data['poses'][str(phase)]['bones_component'].items()}
    p=skin(data['p'],data['weights'],{n:bones[n]@data['invref'][n] for n in data['invref'] if n in bones})
    return p,bones
def material(name,color):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    bsdf=m.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Base Color'].default_value=(*color,1);bsdf.inputs['Roughness'].default_value=.7;return m
def mesh(name,p,t,mats):
    # Render-only winding correction in this mirrored diagnostic coordinate
    # basis. Source indices/geometry/native assets are never changed.
    md=bpy.data.meshes.new(name);md.from_pydata((p*.01).tolist(),[],t[:,::-1].tolist());md.update();o=bpy.data.objects.new(name,md);bpy.context.collection.objects.link(o)
    for m in mats:md.materials.append(m)
    return o
def setup_scene():
    scene=bpy.context.scene;scene.render.engine='BLENDER_EEVEE';scene.render.resolution_x=1000;scene.render.resolution_y=800;scene.render.resolution_percentage=100
    scene.world=bpy.data.worlds.new('World');scene.world.use_nodes=True;scene.world.node_tree.nodes.get('Background').inputs[0].default_value=(.18,.18,.18,1);scene.world.node_tree.nodes.get('Background').inputs[1].default_value=.5
    for n,loc,power in [('Key',(.4,-.3,.6),17.5),('Fill',(-.4,.2,.35),10)]:
        ld=bpy.data.lights.new(n,'AREA');ld.energy=power;ld.size=.7;o=bpy.data.objects.new(n,ld);bpy.context.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,-.03,0))-o.location).to_track_quat('-Z','Y').to_euler()
    cd=bpy.data.cameras.new('Camera');cam=bpy.data.objects.new('Camera',cd);bpy.context.collection.objects.link(cam);scene.camera=cam;cd.type='ORTHO'
    scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG';return scene
def camera(target,offset,scale):
    c=bpy.context.scene.camera;c.location=Vector(target)+Vector(offset);c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=scale
def crosses(a,b,t):
    v0,v1,v2=t;d=b-a;e1=v1-v0;e2=v2-v0;p=np.cross(d,e2);det=np.dot(e1,p)
    if abs(det)<1e-10:return False
    f=1/det;s=a-v0;u=f*np.dot(s,p)
    if u<-1e-7 or u>1+1e-7:return False
    q=np.cross(s,e1);v=f*np.dot(d,q)
    if v<-1e-7 or u+v>1+1e-7:return False
    z=f*np.dot(e2,q);return -1e-7<=z<=1+1e-7
def intersection_pairs(p,t,gp,gt):
    a=BVHTree.FromPolygons([Vector(x) for x in p],t.tolist(),all_triangles=True);b=BVHTree.FromPolygons([Vector(x) for x in gp],gt.tolist(),all_triangles=True)
    pairs=[]
    for ia,ib in a.overlap(b):
        x=p[t[ia]];y=gp[gt[ib]]
        if any(crosses(x[j],x[(j+1)%3],y) or crosses(y[j],y[(j+1)%3],x) for j in range(3)):pairs.append((int(ia),int(ib)))
    return pairs
