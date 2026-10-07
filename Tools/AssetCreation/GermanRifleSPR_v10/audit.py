"""Fresh authored/GLB comparison plus actual imported-asset views."""
import argparse, collections, hashlib, json, math, struct, sys
from pathlib import Path
import bpy, numpy as np
from mathutils import Vector
from mathutils.kdtree import KDTree

def snapshot():
    result={};deps=bpy.context.evaluated_depsgraph_get()
    for obj in bpy.context.scene.objects:
        if obj.type!='MESH':continue
        ev=obj.evaluated_get(deps);me=ev.to_mesh();me.calc_loop_triangles()
        world=obj.matrix_world;rotation=world.to_3x3().inverted().transposed()
        pos=np.array([tuple(world@v.co) for v in me.vertices]);corners=[]
        uv=me.uv_layers.active;norm=me.corner_normals
        for lp in me.loops:
            corners.append((lp.vertex_index,tuple(uv.data[lp.index].uv),tuple((rotation@norm[lp.index].vector).normalized())))
        triangles=[tuple(t.vertices) for t in me.loop_triangles]
        areas=[]
        edges=collections.Counter()
        keys=[tuple(np.round(v,8)) for v in pos]
        for t in triangles:
            q=pos[list(t)];areas.append(float(np.linalg.norm(np.cross(q[1]-q[0],q[2]-q[0]))*.5))
            for x,y in zip(t,(t[1],t[2],t[0])):edges[tuple(sorted((keys[x],keys[y])))]+=1
        result[obj.name]={'pos':pos,'corners':corners,'triangles':len(triangles),
                          'min_area':min(areas),'zero_area_count':sum(v<1e-12 for v in areas),
                          'boundary_edges':sum(n==1 for n in edges.values()),'overfull_edges':sum(n>2 for n in edges.values()),
                          'materials':[m.name for m in me.materials if m],'uv_layers':len(me.uv_layers)}
        ev.to_mesh_clear()
    return result

def compact(snap):
    return {name:{k:v for k,v in row.items() if k not in ('pos','corners')}|{
        'bounds':[row['pos'].min(axis=0).tolist(),row['pos'].max(axis=0).tolist()]} for name,row in snap.items()}

def compare(a,b):
    assert set(a)==set(b),(set(a)-set(b),set(b)-set(a));rows=[]
    for name,src in a.items():
        dst=b[name];assert src['triangles']==dst['triangles'],name
        assert dst['uv_layers']>0 and np.isfinite(dst['pos']).all(),name
        kd=KDTree(len(dst['pos']))
        for i,p in enumerate(dst['pos']):kd.insert(Vector(p),i)
        kd.balance();attrib=collections.defaultdict(list)
        for vi,uv,n in dst['corners']:attrib[vi].append((np.array(uv),np.array(n)))
        maxp=maxu=maxn=0
        for vi,uv,n in src['corners']:
            p=src['pos'][vi];near=kd.find_range(Vector(p),5e-7);assert near,(name,'position not preserved',p.tolist())
            candidates=[(float(np.linalg.norm(np.array(uv)-u)),float(math.degrees(math.acos(max(-1,min(1,float(np.dot(n,nn))))))))
                        for _,idx,_ in near for u,nn in attrib[idx]]
            best=min(candidates,key=lambda x:x[0]+x[1]*1e-5)
            maxp=max(maxp,kd.find(Vector(p))[2]);maxu=max(maxu,best[0]);maxn=max(maxn,best[1])
        assert maxu<2e-5,(name,'UV',maxu)
        assert maxn<.5,(name,'normal degrees',maxn)
        rows.append({'name':name,'position_max_m':maxp,'uv_max':maxu,'normal_max_degrees':maxn})
    return rows

p=argparse.ArgumentParser();p.add_argument('--candidate',required=True);p.add_argument('--out',required=True);p.add_argument('--render',action='store_true');p.add_argument('--compare-glb')
p.add_argument('--name',default='GermanRifle_SPR_V10');p.add_argument('--geometry-baseline');p.add_argument('--pbr-only',action='store_true')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);cand=Path(a.candidate).resolve();out=Path(a.out).resolve()
assert not out.exists(),'Use new audit identity';out.mkdir(parents=True)
report={'passed':False,'candidate':str(cand),'errors':[]}
try:
    bpy.ops.wm.open_mainfile(filepath=str(cand/(a.name+'.blend')),load_ui=False,use_scripts=False)
    source=snapshot();report['authored']=compact(source)
    assert len(source)==24,len(source)
    # Require closed clean authored new solids after positional seam identification.
    for name,row in source.items():
        if '_Donor' not in name:
            assert row['zero_area_count']==0,(name,'tiny triangle',row['zero_area_count'])
            assert row['overfull_edges']==0,(name,'overfull edge')
            assert row['boundary_edges']==0,(name,'open new shell',row['boundary_edges'])
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(cand/(a.name+'.glb')))
    imported=snapshot();report['imported']=compact(imported);report['comparison']=compare(source,imported)
    assert not bpy.data.actions,'Unexpected animation'
    allpos=np.concatenate([x['pos'] for x in imported.values()]);bounds=np.array([allpos.min(axis=0),allpos.max(axis=0)])
    dims=bounds[1]-bounds[0];report['dimensions_m']=dims.tolist();report['bounds_center_m']=bounds.mean(axis=0).tolist()
    assert abs(dims[0]-1.107304)<.002,dims.tolist();assert np.max(abs(bounds.mean(axis=0)))<5e-5
    report['triangles']=sum(r['triangles'] for r in imported.values());assert report['triangles']<40000
    report['images']=[{'name':im.name,'size':list(im.size),'packed':bool(im.packed_file)} for im in bpy.data.images]
    assert all(im.size[0]>0 and im.size[1]>0 for im in bpy.data.images),'Missing image pixels'
    raw=(cand/(a.name+'.glb')).read_bytes();length=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+length])
    assert all('bufferView' in im and 'uri' not in im for im in doc['images']),'External image dependency'
    report['embedded_images']=len(doc['images']);report['sha256_glb']=hashlib.sha256(raw).hexdigest()
    if a.geometry_baseline:
        previous=Path(a.geometry_baseline).resolve()
        bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(previous))
        report['baseline_geometry_comparison']=compare(snapshot(),imported)
        bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(cand/(a.name+'.glb')))
    if a.compare_glb:
        assert not a.render,'Cross-export check is numerical only'
        def image_hashes(payload):
            size=struct.unpack_from('<I',payload,12)[0];d=json.loads(payload[20:20+size]);binary=payload[28+size:];ans={}
            for im in d['images']:
                view=d['bufferViews'][im['bufferView']];begin=view.get('byteOffset',0)
                ans[im['name']]=hashlib.sha256(binary[begin:begin+view['byteLength']]).hexdigest()
            return ans
        previous=Path(a.compare_glb).resolve();prior=previous.read_bytes()
        report['cross_export_images_identical']=image_hashes(raw)==image_hashes(prior)
        assert report['cross_export_images_identical'],'Different packed image bytes'
        bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(previous))
        report['cross_export_comparison']=compare(snapshot(),imported)
        report['cross_export_byte_identical']=raw==prior
    report['passed']=True
    if a.render:
        import importlib.util
        spec=importlib.util.spec_from_file_location('v10source',Path(__file__).with_name('main.py'));mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
        mod.OUT=out;mod.SCENE=bpy.context.scene;mod.PIVOT=Vector(json.loads((cand/'build_report.json').read_text())['pivot_shift'])
        scene=mod.SCENE;scene.world=bpy.data.worlds.new('Fresh_Studio');scene.world.use_nodes=True
        scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.12,.12,.12,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.7
        for i,(loc,energy,size) in enumerate([((.1,-1,1.5),170,1.4),((.2,1,1),110,1.2),((.4,-.5,-1),45,1)]):
            light=bpy.data.objects.new('FreshLight'+str(i),bpy.data.lights.new('FreshLight'+str(i),'AREA'));scene.collection.objects.link(light);light.location=Vector(loc)-mod.PIVOT
            light.rotation_euler=(Vector((.17,0,-.03))-mod.PIVOT-light.location).to_track_quat('-Z','Y').to_euler();light.data.energy=energy;light.data.shape='DISK';light.data.size=size
        scene.view_settings.view_transform='AgX'
        if not a.pbr_only:mod.evidence('fresh_gray','BLENDER_WORKBENCH')
        mod.evidence('fresh_pbr','CYCLES')
except Exception as e:
    report['passed']=False;report['errors'].append(repr(e));raise
finally:
    (out/'audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({k:report[k] for k in ['passed','triangles','dimensions_m','embedded_images','sha256_glb']}),flush=True)
