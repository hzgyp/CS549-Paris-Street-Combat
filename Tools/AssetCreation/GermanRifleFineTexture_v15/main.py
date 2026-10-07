"""Final native wood-detail pass; approved V14 macro appearance stays the base."""
import argparse, importlib.util, json, sys
from pathlib import Path
import bpy
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
V=module('v15_v14_helpers',Path(__file__).parents[1]/'GermanRifleWoodFinish_v14/main.py')
W=V.W;H=V.H;T=V.M.T
BASE=ROOT/'Assets/LocalWorking/Experiments/GermanRiflePilot/20261004-wood-finish-v14/finish_v1'
SOURCE_NAME='GermanRifle_DarkWood_V14';NAME='GermanRifle_FineWood_V15'
WOOD={'V14_Walnut_Stock':'V15_FineWalnut_Stock','V14_Walnut_Handguard':'V15_FineWalnut_Handguard'}
SIZES={'V14_Walnut_Stock':(4096,2048),'V14_Walnut_Handguard':(4096,1024)}
SCALE_U=4.;SCALE_V=2.;D_GAIN=1.1;N_GAIN=.65;R_GAIN=.20

def native_detail():
    images={};guard={}
    x0,y0,x1,y1=T.BOXES['wood']
    for suffix in ['D','N','ORM']:
        path=T.TEX/('T_M1_Garand_'+suffix+'.png');guard[str(path)]=W.sha(path)
        im=bpy.data.images.load(str(path),check_existing=False);im.colorspace_settings.name='sRGB' if suffix=='D' else 'Non-Color'
        data=W.pixels(im);images[suffix]=data[data.shape[0]-y1:data.shape[0]-y0,x0:x1].copy();bpy.data.images.remove(im)
    assert np.max(images['ORM'][:,:,2])<.5,'Wood source includes metallic hardware'
    lum=V.decode(images['D'][:,:,:3])@np.array((.2126,.7152,.0722),np.float32)
    logs=np.log(np.maximum(lum,1e-5))[:,:,None]
    hp=(logs-T.blur(logs,radius=5))[:,:,0];hp-=hp.mean()
    normal=images['N'][:,:,:2]*2-1;normal[:,:,1]*=-1
    normal-=T.blur(normal,radius=5);normal-=normal.mean((0,1))
    rough=images['ORM'][:,:,1:2];rough-=T.blur(rough,radius=5);rough-=rough.mean((0,1))
    return hp.astype(np.float32),normal.astype(np.float32),rough.astype(np.float32),guard

def transfer(mat,details):
    width,height=SIZES[mat.name];u,v=np.meshgrid((np.arange(width,dtype=np.float32)+.5)/width,(np.arange(height,dtype=np.float32)+.5)/height)
    baseim,normalim,ormim=V.M.inputs(mat)
    base=T.sample(W.pixels(baseim),u,v).astype(np.float32);oldbase=base.copy()
    orm=T.sample(W.pixels(ormim),u,v).astype(np.float32);oldorm=orm.copy()
    n=T.sample(W.pixels(normalim),u,v).astype(np.float32)
    su,usign=T.mirror(u*SCALE_U);sv,vsign=T.mirror(v*SCALE_V)
    # Native ends are not tile-ready: suppress high frequency at reflected seams,
    # retain the unchanged seamless low-frequency V14 underneath.
    fade=np.clip(np.minimum.reduce([su,1-su,sv,1-sv])/.025,0,1)
    hp=T.sample(details[0][:,:,None],su,sv)[:,:,0]*fade;hp-=hp.mean()
    factor=np.exp(np.clip(hp*D_GAIN,-.32,.32)).astype(np.float32)
    linear=V.decode(base[:,:,:3]);targetmean=linear.mean((0,1),dtype=np.float64)
    linear*=factor[:,:,None];linear*=np.asarray(targetmean/linear.mean((0,1),dtype=np.float64),np.float32)
    base[:,:,:3]=np.clip(V.encode(linear),0,1)
    rd=T.sample(details[2],su,sv)[:,:,0]*fade;rd-=rd.mean()
    orm[:,:,1]=np.clip(orm[:,:,1]+rd*R_GAIN,.46,.67)
    orm[:,:,1]+=float(oldorm[:,:,1].mean(dtype=np.float64)-orm[:,:,1].mean(dtype=np.float64))
    assert np.array_equal(orm[:,:,[0,2,3]],oldorm[:,:,[0,2,3]])
    fine=T.sample(details[1],su,sv);fine[:,:,0]*=usign;fine[:,:,1]*=vsign
    vec=n[:,:,:3]*2-1;vec[:,:,:2]+=fine*(fade*N_GAIN)[:,:,None]
    vec/=np.maximum(np.linalg.norm(vec,axis=2,keepdims=True),1e-6);n[:,:,:3]=vec*.5+.5;n[:,:,3]=1
    new=mat.copy();new.name=WOOD[mat.name];bs=new.node_tree.nodes.get('Principled BSDF')
    W.texture_for_input(bs,'Base Color').image=V.png_image(new.name+'_BaseColor',base,'sRGB')
    W.texture_for_input(bs,'Normal').inputs['Color'].links[0].from_node.image=V.png_image(new.name+'_Normal',n,'Non-Color')
    W.texture_for_input(bs,'Roughness').inputs['Color'].links[0].from_node.image=V.png_image(new.name+'_ORM',orm,'Non-Color')
    actual=V.decode(W.pixels(V.M.inputs(new)[0])[:,:,:3]).mean((0,1),dtype=np.float64)
    drift=np.abs(actual/targetmean-1);assert drift.max()<.025,('mean colour drift',drift.tolist())
    return new,{'old_material':mat.name,'new_material':new.name,'size':[width,height],
       'linear_colour_mean_before':targetmean.tolist(),'linear_colour_mean_after_png':actual.tolist(),
       'mean_colour_relative_drift':drift.tolist(),'roughness_mean_before':float(oldorm[:,:,1].mean()),
       'roughness_mean_after':float(orm[:,:,1].mean()),'detail_factor_range':[float(factor.min()),float(factor.max())],
       'specular_ior_level':bs.inputs['Specular IOR Level'].default_value,
       'normal_strength':W.texture_for_input(bs,'Normal').inputs['Strength'].default_value}

def evidence(preview):
    scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True
    scene.render.resolution_x=1200;scene.render.resolution_y=729;scene.render.resolution_percentage=100
    W.HELPER.OUT=H.OUT
    W.render(['quarter'] if preview else ['right','left','quarter','top','underside','receiver'],'pbr')
    views=[('stock',(-.283,0,-.085),(.08,-1,.22),.28),('handguard',(.43,0,.007),(.1,-1,.7),.36)]
    if not preview:views += [('stock_reverse',(-.283,0,-.085),(.08,1,.22),.28),('stock_under',(-.283,0,-.085),(0,-.4,-1),.28)]
    for args in views:V.render_close(*args)
    restore={}
    for mat in {s.material for o in scene.objects if o.type=='MESH' for s in o.material_slots if s.material}:
        nt=mat.node_tree;bs=nt.nodes.get('Principled BSDF');out=nt.nodes.get('Material Output')
        restore[mat.name]=out.inputs['Surface'].links[0].from_socket;em=nt.nodes.new('ShaderNodeEmission')
        nt.links.new(bs.inputs['Base Color'].links[0].from_socket,em.inputs['Color']);nt.links.new(em.outputs[0],out.inputs['Surface'])
    V.render_close(*views[0],prefix='unlit')
    for name,socket in restore.items():
        nt=bpy.data.materials[name].node_tree;nt.links.new(socket,nt.nodes.get('Material Output').inputs['Surface'])
        for n in list(nt.nodes):
            if n.type=='EMISSION':nt.nodes.remove(n)

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--stage',choices=['preview','final'],default='final');p.add_argument('--no-render',action='store_true')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);out=Path(a.out).resolve();assert not out.exists();out.mkdir(parents=True);H.OUT=out
    guard={str(BASE/(SOURCE_NAME+'.'+s)):W.sha(BASE/(SOURCE_NAME+'.'+s)) for s in ['blend','glb']}
    assert guard[str(BASE/(SOURCE_NAME+'.blend'))]=='5372fa3f4d85a7ee6c15bd476daa6b6fe42efdc22bf0a5d22743e312d2a53917'
    assert guard[str(BASE/(SOURCE_NAME+'.glb'))]=='9ca471321bd2b684d324cd094eb50d2e3ae0b0adaf174f3ea19dd8b30b0d3c80'
    bpy.ops.wm.open_mainfile(filepath=str(BASE/(SOURCE_NAME+'.blend')),load_ui=False,use_scripts=False)
    H.SCENE=bpy.context.scene;H.PIVOT=V.M.P.PIVOT;before=W.geometry_fingerprint()
    used={m for o in bpy.context.scene.objects if o.type=='MESH' for m in o.data.materials if m}
    protected={im.name:V.M.image_hash(im) for mat in used if mat.name not in WOOD for im in V.M.inputs(mat)}
    hp,n,r,inputs=native_detail();guard.update(inputs);details=(hp,n,r)
    changes=[];newmats={}
    for name in WOOD:
        mat,row=transfer(bpy.data.materials[name],details);newmats[name]=mat;changes.append(row)
    bindings={}
    for ob in bpy.context.scene.objects:
        if ob.type!='MESH':continue
        old=[m.name for m in ob.data.materials];indices=[f.material_index for f in ob.data.polygons]
        for i,mat in enumerate(ob.data.materials):
            if mat.name in WOOD:ob.data.materials[i]=newmats[mat.name]
        assert indices==[f.material_index for f in ob.data.polygons]
        bindings[ob.name]={'before':old,'after':[m.name for m in ob.data.materials],'face_slot_indices_unchanged':True}
    assert W.geometry_fingerprint()==before
    assert all(V.M.image_hash(bpy.data.images[name])==sha for name,sha in protected.items())
    if not a.no_render:evidence(a.stage=='preview')
    bpy.ops.object.select_all(action='DESELECT')
    for ob in bpy.context.scene.objects:
        if ob.type=='MESH' or ob.name=='RifleRoot_Centered':ob.select_set(True)
    bpy.context.view_layer.objects.active=bpy.data.objects['Receiver_Donor_Lower']
    bpy.ops.export_scene.gltf(filepath=str(out/(NAME+'.glb')),export_format='GLB',use_selection=True,export_yup=True,export_vertex_color='NONE',export_animations=False,export_apply=True)
    bpy.context.preferences.filepaths.save_version=0;bpy.context.scene.camera=bpy.data.objects['View_pbr_quarter']
    bpy.ops.wm.save_as_mainfile(filepath=str(out/(NAME+'.blend')))
    assert all(W.sha(Path(f))==sha for f,sha in guard.items())
    report={'stage':a.stage,'name':NAME,'blender':bpy.app.version_string,'baseline_files':guard,'geometry_before':before,
      'geometry_after':W.geometry_fingerprint(),'geometry_exact':True,'pivot_shift':list(H.PIVOT),'changes':changes,'bindings':bindings,
      'protected_pixel_hashes':protected,'all_nonwood_and_caps_pixels_unchanged':True,
      'native_patch_box_top_left':T.BOXES['wood'],'native_size':[723,434],'sampling':[SCALE_U,SCALE_V],
      'native_longitudinal_density_px_m':722*SCALE_U/1.105,'detail_gains':[D_GAIN,N_GAIN,R_GAIN],
      'added_wear_locations':0,'new_random_noise':False,'user_visual_approval':False,'runtime_approval':False,'shared':False,'cloud_spend':0,
      'sha256_blend':W.sha(out/(NAME+'.blend')),'sha256_glb':W.sha(out/(NAME+'.glb'))}
    (out/'build_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(changes),flush=True)
if __name__=='__main__':main()
