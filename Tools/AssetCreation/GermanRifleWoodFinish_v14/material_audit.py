"""Fresh V14 material/PNG/response gates; original V13 remains read-only."""
import argparse, hashlib, importlib.util, json, struct, sys
from pathlib import Path
import bpy
import numpy as np
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent))
import main as M

def embedded(path):
    raw=path.read_bytes();size=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+size]);binary=raw[28+size:]
    images={}
    for im in doc['images']:
        v=doc['bufferViews'][im['bufferView']];offset=v.get('byteOffset',0)
        images[im['name']]=hashlib.sha256(binary[offset:offset+v['byteLength']]).hexdigest()
    return images,doc

def bindings():
    rows={};deps=bpy.context.evaluated_depsgraph_get()
    for ob in bpy.context.scene.objects:
        if ob.type!='MESH':continue
        ev=ob.evaluated_get(deps);me=ev.to_mesh();me.calc_loop_triangles();counts={}
        for tri in me.loop_triangles:
            name=me.materials[tri.material_index].name
            p=np.array([tuple(ob.matrix_world@me.vertices[i].co) for i in tri.vertices])
            row=counts.setdefault(name,{'triangles':0,'area_m2':0})
            row['triangles']+=1;row['area_m2']+=float(np.linalg.norm(np.cross(p[1]-p[0],p[2]-p[0]))*.5)
        rows[ob.name]=counts;ev.to_mesh_clear()
    return rows

def main():
    p=argparse.ArgumentParser();p.add_argument('--candidate',required=True);p.add_argument('--out',required=True);p.add_argument('--render',action='store_true')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);cand=Path(a.candidate).resolve();out=Path(a.out).resolve();assert not out.exists();out.mkdir(parents=True)
    report={'passed':False}
    try:
        source=cand/(M.NAME+'.blend');glb=cand/(M.NAME+'.glb')
        guard={str(f):M.W.sha(f) for f in [source,glb,M.BASE/(M.SOURCE_NAME+'.blend'),M.BASE/(M.SOURCE_NAME+'.glb')]}
        bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);authored=bindings()
        bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));fresh=bindings()
        assert authored.keys()==fresh.keys()
        for name,row in authored.items():
            assert row.keys()==fresh[name].keys(),(name,'material names')
            for mat,count in row.items():
                assert count['triangles']==fresh[name][mat]['triangles'],(name,mat,'triangles')
                assert abs(count['area_m2']-fresh[name][mat]['area_m2'])<1e-7,(name,mat,'area')
        old,old_doc=embedded(M.BASE/(M.SOURCE_NAME+'.glb'));current,doc=embedded(glb)
        allowed={name+'_'+channel for name in M.WOOD for channel in ['BaseColor','ORM']}
        protected=[name for name in old if name not in allowed]
        assert len(protected)==30,len(protected)
        for name in protected:assert current.get(name)==old[name],(name,'protected PNG changed')
        expected={new+'_'+channel for new in M.WOOD.values() for channel in ['BaseColor','ORM']}
        assert set(current)==set(protected)|expected,(set(current),expected)
        assert 'KHR_materials_specular' in doc.get('extensionsUsed',[]),'Response extension missing'
        for name in M.WOOD.values():
            mat=next(m for m in doc['materials'] if m['name']==name)
            factor=mat['extensions']['KHR_materials_specular']['specularFactor']
            assert abs(factor-.36)<1e-6,(name,factor)
            bs=bpy.data.materials[name].node_tree.nodes.get('Principled BSDF')
            assert abs(bs.inputs['Specular IOR Level'].default_value-.18)<1e-6
            assert bs.inputs['Coat Weight'].default_value==0
        # Compare complete nonwood material definitions, resolving texture indices
        # to image names so exporter reindexing is not mistaken for a material edit.
        def signature(document,mat):
            def walk(value):
                if isinstance(value,list):return [walk(x) for x in value]
                if isinstance(value,dict):
                    ans={k:walk(v) for k,v in value.items()}
                    if 'index' in value:
                        tex=document['textures'][value['index']]
                        ans['index']=document['images'][tex['source']]['name']
                    return ans
                return value
            return walk(mat)
        oldmats={m['name']:m for m in old_doc['materials']};newmats={m['name']:m for m in doc['materials']}
        nonwood=sorted(set(oldmats)-set(M.WOOD))
        for name in nonwood:assert signature(old_doc,oldmats[name])==signature(doc,newmats[name]),(name,'nonwood material definition changed')
        if a.render:
            H=M.H;H.OUT=out;H.SCENE=scene=bpy.context.scene;H.PIVOT=M.M.P.PIVOT
            scene.world=bpy.data.worlds.new('V14_Fresh_Studio');scene.world.use_nodes=True
            scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.12,.12,.12,1)
            scene.world.node_tree.nodes['Background'].inputs[1].default_value=.7
            for i,(loc,energy,size) in enumerate([((.1,-1,1.5),170,1.4),((.2,1,1),110,1.2),((.4,-.5,-1),45,1)]):
                ob=bpy.data.objects.new('V14_FreshLight'+str(i),bpy.data.lights.new('V14_FreshLight'+str(i),'AREA'));scene.collection.objects.link(ob)
                ob.location=Vector(loc)-H.PIVOT;ob.rotation_euler=(Vector((.17,0,-.03))-H.PIVOT-ob.location).to_track_quat('-Z','Y').to_euler()
                ob.data.energy=energy;ob.data.shape='DISK';ob.data.size=size
            scene.view_settings.view_transform='AgX';scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
            scene.render.resolution_x=1200;scene.render.resolution_y=729;scene.render.resolution_percentage=100
            for args in [('stock',(-.283,0,-.085),(.08,-1,.22),.28),('handguard',(.43,0,.007),(.1,-1,.7),.36)]:M.render_close(*args,prefix='fresh')
        assert all(M.W.sha(Path(f))==s for f,s in guard.items())
        report.update({'passed':True,'authored_bindings':authored,'fresh_bindings':fresh,
          'protected_png_payloads':protected,'all_protected_embedded_bytes_exact':True,
          'nonwood_material_definitions_exact':nonwood,'wood_specular_factor':.36,
          'fresh_wood_specular_ior_level':.18,'extensions_used':doc.get('extensionsUsed',[]),
          'material_count':len(doc['materials']),'primitive_count':sum(len(m['primitives']) for m in doc['meshes']),
          'embedded_images':len(current),'input_files':guard})
    finally:(out/'material_audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({k:report[k] for k in ['passed','material_count','primitive_count','embedded_images']}),flush=True)
if __name__=='__main__':main()
