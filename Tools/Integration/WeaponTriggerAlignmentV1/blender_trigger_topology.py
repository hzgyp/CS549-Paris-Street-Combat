"""Read-only actual M1 topology/semantic-landmark evidence; no production edits."""
import bpy, hashlib, json, traceback
import numpy as np
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[3]
STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
OUT=STORE/'Evidence/WeaponTriggerAlignmentV1/topology_v1'
FBX=STORE/'Evidence/ReloadIndexContactV6/contact_exchange_v1/Sm_M1_Garand.fbx'
FIT=STORE/'Evidence/ReloadIndexContactV6/target_grip_fit_v1/result.json'
assert not OUT.exists(); OUT.mkdir(parents=True)
(OUT/'source.py').write_bytes(Path(__file__).read_bytes())
hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (FBX,FIT)}
r={'scope':__doc__,'errors':[],'source_mesh_modified':False,'components':[],'views':[]}
def write(): (OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n')
try:
    fit=np.array(json.loads(FIT.read_text())['coordinate_fit'])
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(FBX),automatic_bone_orientation=False,use_anim=False)
    objects=[o for o in bpy.data.objects if o.type=='MESH']
    r['objects']=[{'name':o.name,'vertices':len(o.data.vertices),'materials':[m.name if m else None for m in o.data.materials]} for o in objects]
    pts=[];tri=[];slots=[]
    for o in objects:
        base=len(pts); p=np.array([list(o.matrix_world@v.co)+[1] for v in o.data.vertices])@fit
        pts.extend(p.tolist()); o.data.calc_loop_triangles()
        for t in o.data.loop_triangles:
            tri.append([base+i for i in t.vertices]);slots.append(o.data.materials[t.material_index].name if o.data.materials and o.data.materials[t.material_index] else None)
        o.hide_render=True
    p=np.array(pts);t=np.array(tri);r['bounds_cm']={'min':p.min(0).tolist(),'max':p.max(0).tolist()}
    # Position-weld only the ANALYSIS adjacency, never source vertices/UVs.
    keys={};ids=[]
    for v in p:
        k=tuple(np.round(v,5));ids.append(keys.setdefault(k,len(keys)))
    parents=list(range(len(keys)))
    def root(i):
        while parents[i]!=i: parents[i]=parents[parents[i]];i=parents[i]
        return i
    def join(a,b): parents[root(b)]=root(a)
    for f in t:
        join(ids[f[0]],ids[f[1]]);join(ids[f[1]],ids[f[2]])
    groups={}
    for i,f in enumerate(t):groups.setdefault(root(ids[f[0]]),[]).append(i)
    groups=sorted(groups.values(),key=lambda x:(p[np.unique(t[x])][:,1].min(),len(x)))
    palette=[(.17,.45,.72),(.7,.15,.08),(.12,.65,.2),(.7,.5,.06),(.45,.1,.65),(.06,.5,.5),(.65,.25,.5),(.3,.4,.08)]
    materials=[]
    for i,color in enumerate(palette):
        m=bpy.data.materials.new('Component color '+str(i));m.diffuse_color=(*color,1);m.use_nodes=True
        bsdf=m.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Base Color'].default_value=(*color,1);bsdf.inputs['Roughness'].default_value=.7;materials.append(m)
    mesh=bpy.data.meshes.new('Actual triangles diagnostic');mesh.from_pydata((p*.01).tolist(),[],t.tolist());mesh.update()
    gun=bpy.data.objects.new('Actual M1 diagnostic',mesh);bpy.context.collection.objects.link(gun)
    for m in materials:mesh.materials.append(m)
    for n,g in enumerate(groups):
        q=p[np.unique(t[g])]
        r['components'].append({'id':n,'triangles':len(g),'triangle_ids':g,'bbox_min_cm':q.min(0).tolist(),'bbox_max_cm':q.max(0).tolist(),'centroid_cm':q.mean(0).tolist(),'material_slots':sorted(set(str(slots[i]) for i in g))})
        for i in g:mesh.polygons[i].material_index=n%len(materials)
    r['gun_points_cm']=p.tolist();r['gun_triangles']=t.tolist();write()
    scene=bpy.context.scene;scene.render.engine='BLENDER_EEVEE';scene.render.resolution_x=1200;scene.render.resolution_y=850;scene.render.resolution_percentage=100
    scene.world=bpy.data.worlds.new('World');scene.world.use_nodes=True;scene.world.node_tree.nodes.get('Background').inputs[0].default_value=(.18,.18,.18,1)
    scene.world.node_tree.nodes.get('Background').inputs[1].default_value=.5
    for n,loc,power in [('Key',(.4,-.2,.5),20),('Fill',(-.4,.1,.3),12)]:
        l=bpy.data.lights.new(n,'AREA');l.energy=power;l.size=.6;o=bpy.data.objects.new(n,l);bpy.context.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,-.05,-.02))-o.location).to_track_quat('-Z','Y').to_euler()
    cd=bpy.data.cameras.new('Camera');c=bpy.data.objects.new('Camera',cd);bpy.context.collection.objects.link(c);scene.camera=c;cd.type='ORTHO'
    for name,target,delta,scale in [('left',[0,-.03,-.015],[-.4,0,.02],.30),('right',[0,-.03,-.015],[.4,0,.02],.30),('under',[0,-.03,-.04],[0,0,-.4],.30)]:
        c.location=Vector(target)+Vector(delta);c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();cd.ortho_scale=scale
        scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True);r['views'].append(name+'.png');write()
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'ActualM1Topology.blend'))
    r['status']='actual_topology_collected_semantic_trigger_requires_visual_identification'
except Exception:r['errors'].append(traceback.format_exc());r['status']='failed'
finally:
    r['inputs_unchanged']=all(hashlib.sha256((ROOT/k).read_bytes()).hexdigest()==v for k,v in hashes.items());r['input_hashes']=hashes;write();print(json.dumps({k:r[k] for k in ('status','errors','inputs_unchanged')}))
