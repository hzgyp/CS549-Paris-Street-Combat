"""Independent whole-assembly clean reproduction and fresh GLB corner/image review."""
import argparse,hashlib,json,sys
from pathlib import Path
import bpy,numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from barrel import ROOT,setup,pbr

def snapshot():
    result={}
    for o in bpy.context.scene.objects:
        if o.type!='MESH':continue
        m=o.data;m.calc_loop_triangles();pos=np.array([tuple(o.matrix_world@v.co) for v in m.vertices],dtype=np.float32)
        ff=np.array([tuple(t.vertices) for t in m.loop_triangles]);uv=np.array([[tuple(m.uv_layers.active.data[l].uv) for l in t.loops] for t in m.loop_triangles],dtype=np.float32)
        result[o.name]={'pos':pos,'ff':ff,'uv':uv,'materials':[mat.name for mat in m.materials],'pivot':list(o.location)}
    used={node.image for o in bpy.context.scene.objects if o.type=='MESH' for mat in o.data.materials for node in mat.node_tree.nodes if node.type=='TEX_IMAGE' and node.image is not None}
    images=sorted(hashlib.sha256(bytes(im.packed_file.data)).hexdigest() for im in used if im.packed_file)
    return result,images

def corners(d):
    q=np.concatenate((d['pos'][d['ff']],d['uv']),axis=2);pts=q[:,:,:3];first=np.zeros(len(q),dtype=int)
    for c in (1,2):
        prev=pts[np.arange(len(q)),first];n=pts[:,c];less=(n[:,0]<prev[:,0])|((n[:,0]==prev[:,0])&(n[:,1]<prev[:,1]))|((n[:,0]==prev[:,0])&(n[:,1]==prev[:,1])&(n[:,2]<prev[:,2]));first[less]=c
    q=q[np.arange(len(q))[:,None],(first[:,None]+np.arange(3))%3].reshape(-1,15)
    return q[np.lexsort([q[:,i] for i in reversed([0,1,2,5,6,7,10,11,12,3,4,8,9,13,14])])]

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--candidate',required=True);p.add_argument('--repeat',required=True);p.add_argument('--output',required=True);p.add_argument('--front-only',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=False)
    candidate=Path(a.candidate).resolve();repeat=Path(a.repeat).resolve();name='Kar98k_ManualFront_V9' if a.front_only else 'Kar98k_ManualAssembly_V9';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
    bpy.ops.wm.open_mainfile(filepath=str(candidate/(name+'.blend')),load_ui=False,use_scripts=False);source,images=snapshot()
    bpy.ops.wm.open_mainfile(filepath=str(repeat/(name+'.blend')),load_ui=False,use_scripts=False);again,ri=snapshot();assert source.keys()==again.keys() and ri==images
    exact=all(all(np.array_equal(source[n][k],again[n][k]) for k in ('pos','ff','uv')) and source[n]['materials']==again[n]['materials'] and source[n]['pivot']==again[n]['pivot'] for n in source);assert exact
    byte_exact=sha(candidate/(name+'.glb'))==sha(repeat/(name+'.glb'));assert byte_exact
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(candidate/(name+'.glb')));fresh,fi=snapshot();assert source.keys()==fresh.keys() and images==fi,('names/images mismatch',images,fi)
    rows=[]
    for n,s in source.items():
        f=fresh[n];aa,bb=corners(s),corners(f);assert aa.shape==bb.shape;err=float(np.max(np.abs(aa-bb)));assert err<2e-7,(n,err)
        pe=float(np.max(np.abs(np.array(s['pivot'])-f['pivot'])));assert pe<1e-7
        rows.append({'name':n,'triangles':len(aa),'position_uv_corner_error_max':err,'pivot_error_m':pe,'finite':bool(np.isfinite(bb).all()),'triangle_multiset_and_cyclic_winding_match':True})
    result={'all_pass':True,'fresh_import_meshes':len(rows),'triangles':sum(r['triangles'] for r in rows),'objects':rows,'own_source_packed_images_exact':images,'clean_rebuild_geometry_uv_material_pivot_exact':exact,'clean_rebuild_glb_byte_exact':byte_exact,'glb_sha256':sha(candidate/(name+'.glb')),'production_baseline':False,'receiver_complete_mechanics':False,'ue_runtime_tested':False}
    (out/'audit.json').write_text(json.dumps(result,indent=2));s,cams=setup();pbr()
    for n in ('whole_right','whole_left','whole_top','whole_bottom','quarter','reverse','top_detail','muzzle'):
        s.camera=cams[n];s.render.filepath=str(out/('fresh_'+n+'.png'));bpy.ops.render.render(write_still=True)
    bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'FreshImportReview.blend'));print(json.dumps(result),flush=True)
