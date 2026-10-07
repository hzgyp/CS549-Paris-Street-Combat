"""One actual-trigger/finger-pad rigid translation; unchanged hands/source/gun rotation/scale."""
import bpy,hashlib,json,traceback
import numpy as np
from pathlib import Path
from mathutils import Quaternion,Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[3]
STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
OUT=STORE/'Evidence/WeaponTriggerAlignmentV1/trigger_fit_v1'
FBX=STORE/'Evidence/ContinuousArmsV3/exchange_v1/SK_PC_ContinuousArmsV3.fbx'
POSES=STORE/'Evidence/ReloadIndexContactV6/contact_exchange_v1/result.json'
AUDIT=STORE/'Evidence/ReloadSleeveAdaptationV2/bone_audit_v1/result.json'
CALIB=STORE/'Evidence/ReloadContactBindingV3/binding_proof_author_v2/result.json'
TOPOLOGY=STORE/'Evidence/WeaponTriggerAlignmentV1/topology_v1/result.json'
assert not OUT.exists();OUT.mkdir(parents=True);(OUT/'source.py').write_bytes(Path(__file__).read_bytes())
inputs=(FBX,POSES,AUDIT,CALIB,TOPOLOGY)
hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
r={'scope':__doc__,'errors':[],'phases':[],'views':[],'native_modified':False,
 'limits':['Compressed fixed reload-clip poses, not full native blending/gameplay.','Diagnostic hand cutouts only; production topology unchanged.','Nearest-normal sign is NOT closed-volume penetration.']}
def write():(OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n')
def mat(t):
    if 'translation' in t:t={'t':t['translation'],'q':t['rotation'],'s':t['scale']}
    x,y,z,w=t['q'];m=np.array(Quaternion((w,x,y,z)).to_matrix().to_4x4(),float)
    m[:3,:3]*=np.array(t.get('s',[1,1,1]));m[:3,3]=t['t'];return m
def transform(p,m):return (np.column_stack([p,np.ones(len(p))])@m.T)[:,:3]
def skin(p,ws,deform):
    h=np.column_stack([p,np.ones(len(p))]);out=np.zeros_like(p)
    for i,w in enumerate(ws):
        for n,v in w.items():out[i]+=v*(deform[n]@h[i])[:3]
        out[i]/=sum(w.values())
    return out
def normals(p,t):
    cross=np.cross(p[t[:,1]]-p[t[:,0]],p[t[:,2]]-p[t[:,0]]);area=np.linalg.norm(cross,axis=1)
    return cross/np.maximum(area[:,None],1e-12),area
def crosses(a,b,t):
    v0,v1,v2=t;d=b-a;e1=v1-v0;e2=v2-v0;p=np.cross(d,e2);det=np.dot(e1,p)
    if abs(det)<1e-10:return False
    f=1/det;s=a-v0;u=f*np.dot(s,p)
    if u<-1e-7 or u>1+1e-7:return False
    q=np.cross(s,e1);v=f*np.dot(d,q)
    if v<-1e-7 or u+v>1+1e-7:return False
    z=f*np.dot(e2,q);return -1e-7<=z<=1+1e-7
def intersections(p,t,gp,gt,gb):
    tree=BVHTree.FromPolygons([Vector(x) for x in p],t.tolist(),all_triangles=True)
    found=set()
    for ia,ib in tree.overlap(gb):
        a=p[t[ia]];b=gp[gt[ib]]
        if any(crosses(a[j],a[(j+1)%3],b) or crosses(b[j],b[(j+1)%3],a) for j in range(3)):found.add(ia)
    return len(found)
def material(name,color):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    n=m.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(*color,1);n.inputs['Roughness'].default_value=.7;return m
def mesh(name,p,t,mats):
    d=bpy.data.meshes.new(name);d.from_pydata((p*.01).tolist(),[],t.tolist());d.update();o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o)
    for m in mats:d.materials.append(m)
    return o
def camera(target,delta,scale):
    c=bpy.context.scene.camera;c.location=Vector(target)+Vector(delta);c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=scale
try:
    topo=json.loads(TOPOLOGY.read_text());assert topo['inputs_unchanged'] and not topo['errors']
    gp=np.array(topo['gun_points_cm']);gt=np.array(topo['gun_triangles'],int)
    # Topology component5 is the inspected curved blade, component4 the guard.
    trigger=next(c for c in topo['components'] if c['id']==5);guard=next(c for c in topo['components'] if c['id']==4)
    assert trigger['triangles']==62 and guard['triangles']==126
    trigger_ids=np.array(trigger['triangle_ids']);trigger_tri=gt[trigger_ids]
    tn,ta=normals(gp,trigger_tri);tc=gp[trigger_tri].mean(axis=1)
    # Front-facing lower blade surface. Pad pulls rearward (-gunY).
    select=(tn[:,1]>.35)&(tc[:,2]<-1.0)
    assert select.any(),'Actual forward trigger surface unavailable'
    blade_face_ids=trigger_ids[select];target=np.average(tc[select],axis=0,weights=ta[select])
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(FBX),automatic_bone_orientation=False,use_anim=False)
    rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');source=next(o for o in bpy.data.objects if o.type=='MESH')
    model=json.loads(AUDIT.read_text())['models']['owner'];names=[n for n in model['ref_component'] if n in rig.data.bones]
    src=np.array([list(rig.matrix_world@rig.data.bones[n].head_local)+[1] for n in names]);dst=np.array([model['ref_component'][n]['translation'] for n in names]);fit=np.linalg.lstsq(src,dst,rcond=None)[0]
    r['rest_alignment_max_cm']=float(np.linalg.norm(src@fit-dst,axis=1).max());assert r['rest_alignment_max_cm']<.01
    p=np.array([list(source.matrix_world@v.co)+[1] for v in source.data.vertices])@fit
    weights=[{source.vertex_groups[g.group].name:float(g.weight) for g in v.groups if g.weight>1e-6} for v in source.data.vertices]
    source.data.calc_loop_triangles();tri=np.array([list(t.vertices) for t in source.data.loop_triangles],int)
    right=[sum(v for n,v in w.items() if n=='hand_r' or (n.endswith('_r') and n.startswith(('index_','middle_','ring_','pinky_','thumb_'))))>.5 for w in weights]
    left=[sum(v for n,v in w.items() if n=='hand_l' or (n.endswith('_l') and n.startswith(('index_','middle_','ring_','pinky_','thumb_'))))>.5 for w in weights]
    digit={d:np.array([sum(v for n,v in w.items() if n.startswith(d+'_') and n.endswith('_r'))>.1 for w in weights]) for d in ('index','middle','ring','pinky','thumb')}
    right_tri=tri[np.all(np.array(right)[tri],axis=1)];left_tri=tri[np.all(np.array(left)[tri],axis=1)]
    digit_tri={d:tri[np.all(mask[tri],axis=1)] for d,mask in digit.items()}
    distal=np.array([w.get('index_03_r',0)>.5 for w in weights]);pad_tri=tri[np.all(distal[tri],axis=1)]
    invref={n:np.linalg.inv(mat(t)) for n,t in model['ref_component'].items()};poses=json.loads(POSES.read_text())['clips']['owner_reload']['samples']
    relative=mat(json.loads(CALIB.read_text())['audit_phase0_hand_relative'])
    b={n:mat(t) for n,t in poses['2.2']['bones_component'].items()};deform={n:b[n]@invref[n] for n in invref if n in b}
    posed=skin(p,weights,deform);gun=b['hand_r']@relative;local=transform(posed,np.linalg.inv(gun))
    pn,pa=normals(local,pad_tri);pc=local[pad_tri].mean(1)
    # Actual distal-index pad-side faces opposing the trigger front, not bone head.
    chosen=pn[:,1]<-.35;assert chosen.any(),'Distal pad opposing trigger not identified'
    pad=np.average(pc[chosen],axis=0,weights=pa[chosen]);pad_face_ids=[int(np.flatnonzero(np.all(tri==t,axis=1))[0]) for t in pad_tri[chosen]]
    # Place actual blade near the pad with .3mm surface clearance; orientation fixed.
    clearance=.03;delta=pad-target-np.array([0.,clearance,0.])
    candidate=relative.copy();candidate[:3,3]+=relative[:3,:3]@delta
    r['landmarks']={'trigger_component':5,'guard_component':4,'blade_triangle_ids':blade_face_ids.tolist(),'blade_contact_cm':target.tolist(),
       'distal_pad_original_triangle_ids':pad_face_ids,'pad_contact_original_gun_local_cm':pad.tolist(),'clearance_cm':clearance,
       'method':'Area-weighted forward lower-blade faces and actual rear-facing distal-index pad faces; inspected topology, one translation only'}
    r['candidate']={'old_hand_relative_matrix':relative.tolist(),'new_hand_relative_matrix':candidate.tolist(),'gun_local_delta_cm':delta.tolist(),
       'hand_relative_delta_cm':(candidate[:3,3]-relative[:3,3]).tolist(),'rotation_max_delta':float(np.max(abs(candidate[:3,:3]-relative[:3,:3]))),'scale_unchanged':True}
    source.hide_render=True;rig.hide_render=True
    grey=material('Gun diagnostic',(.14,.17,.20));metal=material('Actual trigger',(.15,.65,.7));tan=material('Hand',(.62,.42,.27));orange=material('Index',(1,.22,.04));blue=material('Support hand',(.18,.45,.65))
    gunob=mesh('Actual unchanged M1',gp,gt,[grey,metal])
    for i in trigger_ids:gunob.data.polygons[int(i)].material_index=1
    cdata=bpy.data.cameras.new('Contact camera');c=bpy.data.objects.new('Contact camera',cdata);bpy.context.collection.objects.link(c);bpy.context.scene.camera=c;cdata.type='ORTHO'
    scene=bpy.context.scene;scene.render.engine='BLENDER_EEVEE';scene.render.resolution_x=1000;scene.render.resolution_y=800;scene.render.resolution_percentage=100
    scene.world=bpy.data.worlds.new('World');scene.world.use_nodes=True;scene.world.node_tree.nodes.get('Background').inputs[0].default_value=(.18,.18,.18,1);scene.world.node_tree.nodes.get('Background').inputs[1].default_value=.5
    for n,loc,power in [('Key',(.4,-.3,.6),17.5),('Fill',(-.4,.2,.35),10)]:
        ld=bpy.data.lights.new(n,'AREA');ld.energy=power;ld.size=.7;o=bpy.data.objects.new(n,ld);bpy.context.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,-.03,0))-o.location).to_track_quat('-Z','Y').to_euler()
    scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG'
    gb=BVHTree.FromPolygons([Vector(x) for x in gp],gt.tolist(),all_triangles=True)
    visible=[]
    for phase in ('0.0','2.2','4.1'):
        bones={n:mat(t) for n,t in poses[phase]['bones_component'].items()};posed=skin(p,weights,{n:bones[n]@invref[n] for n in invref if n in bones})
        oldlocal=transform(posed,np.linalg.inv(bones['hand_r']@relative));newlocal=transform(posed,np.linalg.inv(bones['hand_r']@candidate))
        row={'phase_s':float(phase),'conditions':{}}
        # Same gun-local camera for paired views; comparison isolates registration.
        center=(np.mean(oldlocal[digit['index']],axis=0)+np.mean(newlocal[digit['index']],axis=0))*.005
        for condition,points in [('before',oldlocal),('after',newlocal)]:
            row['conditions'][condition]={'right_surface_crossing_triangles':{d:intersections(points,t,gp,gt,gb) for d,t in digit_tri.items()},
               'right_hand_crossing_triangles':intersections(points,right_tri,gp,gt,gb),'left_hand_crossing_triangles':intersections(points,left_tri,gp,gt,gb),
               'right_digit_surface_nearest_cm':{d:float(np.median([gb.find_nearest(Vector(q))[3] for q in points[mask]])) for d,mask in digit.items()}}
            for o in visible:bpy.data.objects.remove(o,do_unlink=True)
            hand=mesh('Unchanged right hand '+condition,points,right_tri,[tan,orange]);support=mesh('Unchanged left hand '+condition,points,left_tri,[blue]);visible=[hand,support]
            for poly,f in zip(hand.data.polygons,right_tri):poly.material_index=int(np.all(digit['index'][f]))
            for view,offset in [('right',(.28,-.05,.10)),('left',(-.28,-.05,.10)),('top',(.02,-.04,.30))]:
                camera(center,offset,.26);filename=f'{phase}_{condition}_{view}.png';scene.render.filepath=str(OUT/filename);bpy.ops.render.render(write_still=True);r['views'].append({'file':filename,'phase_s':float(phase),'condition':condition,'view':view});write()
            camera([0,.22,0],[-1.2,.05,.4],1.2);filename=f'{phase}_{condition}_whole.png';scene.render.filepath=str(OUT/filename);bpy.ops.render.render(write_still=True);r['views'].append({'file':filename,'phase_s':float(phase),'condition':condition,'view':'whole'});write()
        r['phases'].append(row);write()
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'TriggerAlignmentCandidate.blend'));r['status']='one_rigid_translation_collected_requires_contact_review_no_native_selection'
except Exception:r['status']='failed';r['errors'].append(traceback.format_exc())
finally:
    r['inputs_unchanged']=all(hashlib.sha256((ROOT/k).read_bytes()).hexdigest()==v for k,v in hashes.items());r['input_hashes']=hashes;write();print(json.dumps({k:r[k] for k in ('status','errors','inputs_unchanged')}))
