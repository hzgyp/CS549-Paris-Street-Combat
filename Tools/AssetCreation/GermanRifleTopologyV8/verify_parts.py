"""Independent fresh-import corner/topology/material/pivot checks."""
import argparse,collections,hashlib,json,math,sys
from pathlib import Path
import bpy,numpy as np
from mathutils.kdtree import KDTree
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import setup,camera,pbr
from parts import VIEWS

def extract(o):
    m=o.data;m.calc_loop_triangles();uv=m.uv_layers.active.data
    pts=np.array([tuple(o.matrix_world@v.co) for v in m.vertices])
    ff=np.array([list(t.vertices) for t in m.loop_triangles]);loops=np.array([list(t.loops) for t in m.loop_triangles])
    uvs=np.array([[tuple(uv[i].uv) for i in ls] for ls in loops]);rot=o.matrix_world.to_3x3().inverted().transposed()
    normals=np.array([[tuple((rot@m.corner_normals[i].vector).normalized()) for i in ls] for ls in loops])
    materials=[]
    for mat in m.materials:
        bs=mat.node_tree.nodes.get('Principled BSDF')
        materials.append({'color':list(bs.inputs['Base Color'].default_value),'metallic':bs.inputs['Metallic'].default_value,'roughness':bs.inputs['Roughness'].default_value})
    return {'pts':pts,'ff':ff,'uvs':uvs,'normals':normals,'origin':np.array(o.location),'materials':materials}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--repeat',required=True);p.add_argument('--output',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);src=Path(a.input).resolve();rep=Path(a.repeat).resolve();out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=False)
    n='Kar98k_StandaloneMechanical_V8C';blend=src/(n+'.blend');glb=src/(n+'.glb')
    bpy.ops.wm.open_mainfile(filepath=str(blend),load_ui=False,use_scripts=False)
    original={o.name:extract(o) for o in bpy.context.scene.objects if o.type=='MESH'}
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));fresh={o.name:o for o in bpy.context.scene.objects if o.type=='MESH'}
    assert set(original)==set(fresh),'mesh names differ'
    rows=[]
    for name,o in fresh.items():
        r=original[name];f=extract(o);tree=KDTree(len(r['pts']))
        for i,pt in enumerate(r['pts']):tree.insert(pt,i)
        tree.balance();mapping=[];dist=[]
        for pt in f['pts']:
            _,i,d=tree.find(pt);mapping.append(i);dist.append(d)
        assert max(dist)<1e-7
        mapped=np.array(mapping)[f['ff']];source={tuple(sorted(tri.tolist())):i for i,tri in enumerate(r['ff'])};assert len(source)==len(r['ff'])
        assert collections.Counter(tuple(sorted(t.tolist())) for t in mapped)==collections.Counter(source.keys())
        uv_error=0.;normal_error=0.
        for j,tri in enumerate(mapped):
            k=source[tuple(sorted(tri.tolist()))];st=r['ff'][k]
            # Cyclic orientation must survive; mirrored/reversed winding fails.
            assert any(np.array_equal(tri,np.roll(st,z)) for z in range(3))
            for c,vi in enumerate(tri):
                sc=list(st).index(vi);uv_error=max(uv_error,float(np.max(np.abs(f['uvs'][j,c]-r['uvs'][k,sc]))))
                dot=float(np.dot(f['normals'][j,c],r['normals'][k,sc]));normal_error=max(normal_error,math.degrees(math.acos(np.clip(dot,-1,1))))
        mat_error=float(np.max(np.abs(np.array([[*m['color'],m['metallic'],m['roughness']] for m in r['materials']])-np.array([[*m['color'],m['metallic'],m['roughness']] for m in f['materials']]))))
        origin_error=float(np.max(np.abs(f['origin']-r['origin'])))
        assert uv_error<1e-6 and normal_error<.5 and mat_error<1e-6 and origin_error<1e-7
        rows.append({'name':name,'triangles':len(mapped),'max_position_error_m':max(dist),'max_uv_error':uv_error,'max_normal_error_deg':normal_error,'max_material_error':mat_error,'max_pivot_error_m':origin_error,'topology_and_winding_match':True})
    sh=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    equal=sh(glb)==sh(rep/(n+'.glb'));assert equal,'clean rebuild GLB mismatch'
    report={'all_pass':True,'standalone_only':True,'glb_sha256':sh(glb),'clean_rebuild_glb_byte_exact':equal,'source_meshes':len(original),'parts':rows}
    (out/'audit.json').write_text(json.dumps(report,indent=2))
    s,_=setup();pbr()
    for name,e,t,sc in VIEWS:
        s.camera=camera('Fresh_'+name,e,t,sc);s.render.filepath=str(out/('fresh_'+name+'.png'));bpy.ops.render.render(write_still=True)
    print(json.dumps({'all_pass':True,'meshes':len(rows),'triangles':sum(r['triangles'] for r in rows),'max_position_error_m':max(r['max_position_error_m'] for r in rows),'max_normal_error_deg':max(r['max_normal_error_deg'] for r in rows),'glb_sha256':report['glb_sha256']}),flush=True)
