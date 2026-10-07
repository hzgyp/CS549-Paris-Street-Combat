"""Fresh GLB face-material counts/areas, protected PNG layers and close views."""
import sys,argparse,json,struct,hashlib
from pathlib import Path
import bpy
import numpy as np
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent))
import main as M

def bindings():
    rows={};deps=bpy.context.evaluated_depsgraph_get()
    for ob in bpy.context.scene.objects:
        if ob.type!='MESH':continue
        ev=ob.evaluated_get(deps);me=ev.to_mesh();me.calc_loop_triangles();counts={}
        for tri in me.loop_triangles:
            name=me.materials[tri.material_index].name
            p=np.array([tuple(ob.matrix_world@me.vertices[i].co) for i in tri.vertices])
            area=float(np.linalg.norm(np.cross(p[1]-p[0],p[2]-p[0]))*.5)
            row=counts.setdefault(name,{'triangles':0,'area_m2':0});row['triangles']+=1;row['area_m2']+=area
        rows[ob.name]=counts;ev.to_mesh_clear()
    return rows

def embedded(path):
    raw=path.read_bytes();size=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+size]);binary=raw[28+size:]
    images={}
    for im in doc['images']:
        view=doc['bufferViews'][im['bufferView']];start=view.get('byteOffset',0)
        images[im['name']]=hashlib.sha256(binary[start:start+view['byteLength']]).hexdigest()
    return images,len(doc['materials']),sum(len(m['primitives']) for m in doc['meshes'])

p=argparse.ArgumentParser();p.add_argument('--candidate',required=True);p.add_argument('--out',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);cand=Path(a.candidate).resolve();out=Path(a.out).resolve();assert not out.exists();out.mkdir(parents=True)
report={'passed':False}
try:
    source=cand/(M.NAME+'.blend');glb=cand/(M.NAME+'.glb');guard={str(f):M.W.sha(f) for f in [source,glb]}
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
    authored=bindings()
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb))
    fresh=bindings();assert authored.keys()==fresh.keys()
    for name,row in authored.items():
        assert row.keys()==fresh[name].keys(),(name,'material names')
        for mat,count in row.items():
            assert count['triangles']==fresh[name][mat]['triangles'],(name,mat,'triangles')
            assert abs(count['area_m2']-fresh[name][mat]['area_m2'])<1e-7,(name,mat,'area')
    baseline,_,_=embedded(M.BASE/'GermanRifle_M1Texture_V12.glb');current,mats,primitives=embedded(glb)
    normal_names=[n for n in baseline if n.endswith('_Normal')]
    for n in normal_names:assert current.get(n)==baseline[n],(n,'original normal PNG missing/changed')
    # Unchanged materials on caps/trigger/sights retain all their original image bytes.
    protected=[n for n in baseline if n.startswith('V12_M1_New_BluedSteel') or n.startswith('V12_M1_DonorSteel_2')]
    for n in protected:assert current.get(n)==baseline[n],(n,'outside-scope image changed')
    M.H.OUT=out;M.H.SCENE=scene=bpy.context.scene;M.H.PIVOT=M.P.PIVOT
    scene.world=bpy.data.worlds.new('V13_Fresh_Studio');scene.world.use_nodes=True
    scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.12,.12,.12,1)
    scene.world.node_tree.nodes['Background'].inputs[1].default_value=.7
    for i,(loc,energy,size) in enumerate([((.1,-1,1.5),170,1.4),((.2,1,1),110,1.2),((.4,-.5,-1),45,1)]):
        ob=bpy.data.objects.new('V13_FreshLight'+str(i),bpy.data.lights.new('V13_FreshLight'+str(i),'AREA'));scene.collection.objects.link(ob)
        ob.location=Vector(loc)-M.P.PIVOT;ob.rotation_euler=(Vector((.17,0,-.03))-M.P.PIVOT-ob.location).to_track_quat('-Z','Y').to_euler()
        ob.data.energy=energy;ob.data.shape='DISK';ob.data.size=size
    scene.view_settings.view_transform='AgX';scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
    scene.render.resolution_x=1200;scene.render.resolution_y=729;scene.render.resolution_percentage=100
    for args in [('stock',(-.283,0,-.085),(.08,-1,.22),.28),('handguard',(.43,0,.007),(.1,-1,.7),.36),
                 ('barrel',(.650,0,.005),(.2,-1,.65),.23),('muzzle',(.708,0,.006),(1,-1,.6),.09)]:M.render_view(*args,prefix='fresh')
    assert all(M.W.sha(Path(f))==s for f,s in guard.items())
    report.update({'passed':True,'authored_bindings':authored,'fresh_bindings':fresh,'protected_normal_pngs':normal_names,
                   'protected_other_pngs':protected,'all_protected_embedded_bytes_exact':True,
                   'material_count':mats,'primitive_count':primitives,'embedded_images':len(current),'input_files':guard})
finally:(out/'details_audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({k:report[k] for k in ['passed','material_count','primitive_count','embedded_images']}),flush=True)
