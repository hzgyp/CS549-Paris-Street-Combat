"""V14: wood colour/satin response only, from protected V13; no new marks."""
import argparse, hashlib, importlib.util, json, sys
from pathlib import Path
import bpy
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'Assets/LocalWorking/Experiments/GermanRiflePilot/20261004-wood-wear-v13/finish_v2'
SOURCE_NAME='GermanRifle_CoordinatedWear_V13'
NAME='GermanRifle_DarkWood_V14'
spec=importlib.util.spec_from_file_location('v14_existing',Path(__file__).parents[1]/'GermanRifleWoodWear_v13/main.py')
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
W=M.W;H=M.H
WOOD={'V12_M1_Oiled_Walnut':'V14_Walnut_EndFaces','V13_Stock':'V14_Walnut_Stock','V13_Handguard':'V14_Walnut_Handguard'}
PIGMENT=np.array((.40,.36,.28),np.float32)

def decode(c):return np.where(c<=.04045,c/12.92,((c+.055)/1.055)**2.4)
def encode(c):return np.where(c<=.0031308,c*12.92,1.055*np.maximum(c,0)**(1/2.4)-.055)

def png_image(name,data,space):
    """Save encoded bytes, then reload exactly what will be packed/exported."""
    h,w=data.shape[:2];temp=bpy.data.images.new('Build_'+name,width=w,height=h,alpha=True)
    temp.colorspace_settings.name=space;temp.pixels.foreach_set(data.astype(np.float32).ravel())
    path=H.OUT/(name+'.png');temp.filepath_raw=str(path);temp.file_format='PNG';temp.save()
    bpy.data.images.remove(temp)
    im=bpy.data.images.load(str(path),check_existing=False);im.name=name
    im.colorspace_settings.name=space;im.pack();return im

def mask(stem,suffix):
    path=BASE/(stem+'_'+suffix+'Mask.png');assert path.is_file()
    im=bpy.data.images.load(str(path),check_existing=False);im.colorspace_settings.name='Non-Color'
    data=W.pixels(im)[:,:,0].copy();bpy.data.images.remove(im)
    return data,{'path':str(path.relative_to(ROOT)),'sha256':W.sha(path)}

def repair(mat):
    baseim,normim,ormim=M.inputs(mat);base=W.pixels(baseim);orm=W.pixels(ormim)
    oldbase=base.copy();oldorm=orm.copy();wear=np.zeros(base.shape[:2],np.float32)
    hand=np.zeros_like(wear);records=[]
    if mat.name.startswith('V13_'):
        wear,record=mask(mat.name,'Wear');records.append(record)
        scratches,record=mask(mat.name,'Scratch');records.append(record)
        hand,record=mask(mat.name,'Handling');records.append(record)
        wear=np.clip(wear+.78*scratches,0,.85)
        assert wear.max()>.1,'Existing wear mask empty'
        # Recover intact colour before V13's known additive exposure contrast.
        intact=np.clip(base[:,:,:3]-wear[:,:,None]*np.array((.23,.14,.065),np.float32),0,1)
    else:intact=base[:,:,:3].copy()
    stained=encode(decode(intact)*PIGMENT)
    # Same old mask: small islands expose lighter wood, not a new mark generator.
    raw=np.clip(intact+np.array((.12,.073,.025),np.float32),0,1)
    base[:,:,:3]=np.clip(stained*(1-wear[:,:,None])+raw*wear[:,:,None],0,1)
    # A narrower satin reflection instead of the former broad pale rough wash.
    # Sole causal response correction after preview_v1: the colour is dark in
    # unlit evidence, but default F0 + lower roughness washed broad faces white.
    orm[:,:,1]=np.clip(oldorm[:,:,1]*.87-.045+wear*.12-hand*.02,.48,.65)
    assert np.array_equal(orm[:,:,[0,2,3]],oldorm[:,:,[0,2,3]])
    new=mat.copy();new.name=WOOD[mat.name];new.diffuse_color=(.07,.024,.01,1)
    bs=new.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Specular IOR Level'].default_value=.18
    W.texture_for_input(bs,'Base Color').image=png_image(new.name+'_BaseColor',base,'sRGB')
    ormnode=W.texture_for_input(bs,'Roughness').inputs['Color'].links[0].from_node
    ormnode.image=png_image(new.name+'_ORM',orm,'Non-Color')
    assert M.inputs(new)[1]==normim
    return new,{'old_material':mat.name,'new_material':new.name,'size':list(baseim.size),
       'old_srgb_mean':oldbase[:,:,:3].mean((0,1)).tolist(),
       'new_srgb_mean':W.pixels(M.inputs(new)[0])[:,:,:3].mean((0,1)).tolist(),
       'old_roughness_mean':float(oldorm[:,:,1].mean()),'new_roughness_mean':float(orm[:,:,1].mean()),
       'normal_unchanged':normim.name,'masks':records,'specular_ior_level':bs.inputs['Specular IOR Level'].default_value,
       'coat_weight':bs.inputs['Coat Weight'].default_value}

def render_close(name,center,direction,scale,prefix='pbr'):
    scene=bpy.context.scene;scene.camera=H.camera('V14_View_'+prefix+'_'+name,center,direction,scale)
    scene.render.filepath=str(H.OUT/(prefix+'_'+name+'.png'));bpy.ops.render.render(write_still=True)

def evidence(preview):
    scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
    scene.render.resolution_x=1200;scene.render.resolution_y=729;scene.render.resolution_percentage=100
    W.HELPER.OUT=H.OUT
    W.render(['quarter','receiver'] if preview else ['right','left','quarter','top','underside','receiver'],'pbr')
    views=[('stock',(-.283,0,-.085),(.08,-1,.22),.28),('handguard',(.43,0,.007),(.1,-1,.7),.36)]
    if not preview:views += [('stock_reverse',(-.283,0,-.085),(.08,1,.22),.28),('stock_under',(-.283,0,-.085),(0,-.4,-1),.28)]
    for view in views:render_close(*view)
    originals={}
    for mat in {s.material for o in scene.objects if o.type=='MESH' for s in o.material_slots if s.material}:
        nt=mat.node_tree;bs=nt.nodes.get('Principled BSDF');out=nt.nodes.get('Material Output')
        originals[mat.name]=out.inputs['Surface'].links[0].from_socket
        em=nt.nodes.new('ShaderNodeEmission');nt.links.new(bs.inputs['Base Color'].links[0].from_socket,em.inputs['Color']);nt.links.new(em.outputs[0],out.inputs['Surface'])
    render_close(*views[0],prefix='unlit')
    for name,socket in originals.items():
        nt=bpy.data.materials[name].node_tree;nt.links.new(socket,nt.nodes.get('Material Output').inputs['Surface'])
        for n in list(nt.nodes):
            if n.type=='EMISSION':nt.nodes.remove(n)

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--stage',choices=['preview','final'],default='final');p.add_argument('--no-render',action='store_true')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);out=Path(a.out).resolve();assert not out.exists();out.mkdir(parents=True);H.OUT=out
    guard={str(BASE/(SOURCE_NAME+'.'+s)):W.sha(BASE/(SOURCE_NAME+'.'+s)) for s in ['blend','glb']}
    assert guard[str(BASE/(SOURCE_NAME+'.blend'))]=='bb730a98cfe70241fb1a6af069d2366bdce69536db813aa9bbcd5634afb0f46e'
    assert guard[str(BASE/(SOURCE_NAME+'.glb'))]=='76c557b3334c8b9a7ee178b33783376642b5c8a176a37e662ab7203714c00a81'
    bpy.ops.wm.open_mainfile(filepath=str(BASE/(SOURCE_NAME+'.blend')),load_ui=False,use_scripts=False)
    H.SCENE=bpy.context.scene;H.PIVOT=M.P.PIVOT
    before=W.geometry_fingerprint()
    used={m for o in bpy.context.scene.objects if o.type=='MESH' for m in o.data.materials if m}
    protected={im.name:M.image_hash(im) for mat in used for im in M.inputs(mat) if mat.name not in WOOD or im==M.inputs(mat)[1]}
    steel_nodes={mat.name:mat.node_tree.as_pointer() for mat in used if mat.name not in WOOD}
    changes=[];newmats={}
    for name in WOOD:
        mat,row=repair(bpy.data.materials[name]);newmats[name]=mat;changes.append(row)
    bindings={}
    for ob in bpy.context.scene.objects:
        if ob.type!='MESH':continue
        old=[m.name for m in ob.data.materials];face_ids=[f.material_index for f in ob.data.polygons]
        for i,mat in enumerate(ob.data.materials):
            if mat.name in WOOD:ob.data.materials[i]=newmats[mat.name]
        assert face_ids==[f.material_index for f in ob.data.polygons]
        bindings[ob.name]={'before':old,'after':[m.name for m in ob.data.materials],'face_slot_indices_unchanged':True}
    assert W.geometry_fingerprint()==before
    assert all(M.image_hash(bpy.data.images[n])==digest for n,digest in protected.items())
    assert all(bpy.data.materials[n].node_tree.as_pointer()==pointer for n,pointer in steel_nodes.items())
    if not a.no_render:evidence(a.stage=='preview')
    bpy.ops.object.select_all(action='DESELECT')
    for ob in bpy.context.scene.objects:
        if ob.type=='MESH' or ob.name=='RifleRoot_Centered':ob.select_set(True)
    bpy.context.view_layer.objects.active=bpy.data.objects['Receiver_Donor_Lower']
    bpy.ops.export_scene.gltf(filepath=str(out/(NAME+'.glb')),export_format='GLB',use_selection=True,
       export_yup=True,export_vertex_color='NONE',export_animations=False,export_apply=True)
    bpy.context.preferences.filepaths.save_version=0
    bpy.context.scene.camera=bpy.data.objects['View_pbr_quarter']
    bpy.ops.wm.save_as_mainfile(filepath=str(out/(NAME+'.blend')))
    assert all(W.sha(Path(f))==digest for f,digest in guard.items())
    report={'stage':a.stage,'name':NAME,'blender':bpy.app.version_string,'baseline_files':guard,
      'geometry_before':before,'geometry_after':W.geometry_fingerprint(),'geometry_exact':True,
      'pivot_shift':list(M.P.PIVOT),'changes':changes,'bindings':bindings,
      'protected_pixel_hashes':protected,'all_normals_and_nonwood_pixels_unchanged':True,
      'pigment_linear_rgb':PIGMENT.tolist(),'colour_space':'Decode sRGB to linear, pigment tint, encode to sRGB; save and reload PNG before use',
      'new_wear_locations':0,'new_normal_maps':0,'coat_extension_added':False,
      'response_correction':'One correction after preview_v1: reduce pale specular wash, moderate roughness; same base colour/masks/studio',
      'sha256_blend':W.sha(out/(NAME+'.blend')),'sha256_glb':W.sha(out/(NAME+'.glb')),
      'user_visual_approval':False,'runtime_approval':False,'shared':False,'cloud_spend':0}
    (out/'build_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({'geometry_exact':True,'changes':changes}),flush=True)
if __name__=='__main__':main()
