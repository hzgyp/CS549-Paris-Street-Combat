"""Bounded V13 material repair, real-surface owned masks, protected V12 shape.

Run proof first, inspect it, then final. All outputs use new identities.
No cloud, UE, source-asset write or release. Existing structural normals are
retained byte-for-byte; wood micro-scratches are the only normal composition.
"""
import argparse, hashlib, json, sys
from pathlib import Path
import bpy
import numpy as np
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).parent))
import preflight as P
W=P.W
H=P.module('v13_helpers',Path(__file__).parents[1]/'GermanRifleSPR_v10/main.py')
T=P.module('v12_sample',Path(__file__).parents[1]/'GermanRifleM1Transfer_v12/main.py')
NAME='GermanRifle_CoordinatedWear_V13'
BASE=P.BASE
RECORD=[]

def image_hash(im):
    return hashlib.sha256(W.pixels(im).tobytes()).hexdigest()

def inputs(mat):
    bs=mat.node_tree.nodes.get('Principled BSDF')
    base=W.texture_for_input(bs,'Base Color').image
    nm=W.texture_for_input(bs,'Normal').inputs['Color'].links[0].from_node.image
    orm=W.texture_for_input(bs,'Roughness').inputs['Color'].links[0].from_node.image
    return base,nm,orm

def positions(ob):
    return np.array([tuple(ob.matrix_world@v.co+P.PIVOT) for v in ob.data.vertices],np.float32)

def anchor(ob,x,j=None,ring=None,target=None):
    pos=positions(ob)
    if j is not None:
        ids=np.arange(j,len(pos),ring);idx=int(ids[np.argmin(abs(pos[ids,0]-x))])
    else:idx=int(np.argmin(np.linalg.norm(pos-np.array(target),axis=1)))
    faces=[f.index for f in ob.data.polygons if idx in f.vertices]
    RECORD.append({'object':ob.name,'vertex':idx,'faces':faces,'design_position_m':pos[idx].tolist()})
    return pos[idx]

def stamp(xyz,center,long=.012,wide=.0025,strength=.7):
    """Elliptical distance to an actual surface vertex, metric in metres."""
    d=xyz-center
    t=(d[:,:,0]/long)**2+(d[:,:,1]**2+d[:,:,2]**2)/wide**2
    rough=.72+.18*np.sin(d[:,:,0]*2900+d[:,:,2]*3700)+.10*np.sin(d[:,:,1]*5400-d[:,:,0]*1900)
    return np.nan_to_num(np.exp(-t*1.5)*rough*strength)

def stroke(xyz,a,b,width,strength):
    vec=b-a;length2=float(vec@vec)
    if length2<1e-10:return np.zeros(xyz.shape[:2],np.float32)
    d=xyz-a;t=np.clip(np.sum(d*vec,axis=2)/length2,0,1)
    nearest=a+t[:,:,None]*vec
    dist2=np.sum((xyz-nearest)**2,axis=2)
    taper=np.clip(np.sin(t*np.pi)*2,0,1)
    irregular=.85+.15*np.sin(t*53+np.nan_to_num(xyz[:,:,0])*1100)
    return np.nan_to_num(np.exp(-dist2/(width*width))*taper*irregular*strength)

def pad(mask,valid,steps=5):
    """Extend only mask values into atlas padding; source grain is not replaced."""
    m=mask.copy();v=valid.copy()
    for _ in range(steps):
        total=np.zeros_like(m);count=np.zeros_like(m)
        for dy,dx in [(0,1),(0,-1),(1,0),(-1,0)]:
            vv=np.roll(v,(dy,dx),(0,1));mm=np.roll(m,(dy,dx),(0,1))
            if dy==1:vv[0]=False
            if dy==-1:vv[-1]=False
            if dx==1:vv[:,0]=False
            if dx==-1:vv[:,-1]=False
            total+=mm*vv;count+=vv
        add=(~v)&(count>0);m[add]=total[add]/count[add];v[add]=True
    return m

def mask_image(name,m):
    rgba=np.ones((*m.shape,4),np.float32);rgba[:,:,:3]=m[:,:,None]
    return H.image_data(name,rgba,'Non-Color')

def derivative(ob,faces,stem,size,wear,scratch,handling=None,wood=False,conflict=None):
    old=ob.data.materials[0];bi,ni,oi=inputs(old)
    width,height=(size,size) if isinstance(size,int) else size
    u,v=np.meshgrid((np.arange(width)+.5)/width,(np.arange(height)+.5)/height)
    base=T.sample(W.pixels(bi),u,v).astype(np.float32)
    orm=T.sample(W.pixels(oi),u,v).astype(np.float32)
    # Shared source normal is a read-only layer. No steel normal synthesis.
    normal=ni
    if wood:
        hand=np.zeros_like(wear) if handling is None else handling
        base[:,:,:3]*=(1-hand*.13)[:,:,None]
        amount=np.clip(wear+scratch*.78,0,.85)
        # One diagnosed contrast correction: prior raw-wood colour nearly matched
        # the intact V12 sample. A local warm increase preserves the grain itself.
        # Masks/positions/quantity/lighting are unchanged; no global brightening.
        raw=np.clip(base[:,:,:3]+np.array((.23,.14,.065),np.float32),0,1)
        base[:,:,:3]=base[:,:,:3]*(1-amount[:,:,None])+raw*amount[:,:,None]
        orm[:,:,1]=np.clip(orm[:,:,1]+wear*.08+scratch*.045-hand*.06,.52,.87)
        orm[:,:,2]=0
        n=T.sample(W.pixels(ni),u,v).astype(np.float32)
        dv,du=np.gradient(scratch)
        n[:,:,0]-=du*.025;n[:,:,1]-=dv*.025
        vec=n[:,:,:3]*2-1;vec/=np.maximum(np.linalg.norm(vec,axis=2,keepdims=True),1e-6)
        n[:,:,:3]=vec*.5+.5
        normal=H.image_data(stem+'_Normal',n,'Non-Color')
    else:
        # Dark irregular residue/abrasion, not a uniform silver or rusty tube.
        dirt=np.zeros_like(wear) if handling is None else handling
        base[:,:,:3]*=(1-dirt*.36)[:,:,None]
        amount=np.clip(wear+scratch*.65,0,.65)
        raw=base[:,:,:3]*.40+np.array((.105,.112,.12),np.float32)*.60
        base[:,:,:3]=base[:,:,:3]*(1-amount[:,:,None])+raw*amount[:,:,None]
        orm[:,:,1]=np.clip(orm[:,:,1]+dirt*.19-wear*.06-scratch*.025,.36,.72)
        # Exposed steel keeps original metallic; fine oil/grime is not black mud.
    base[:,:,3]=orm[:,:,3]=1
    new=H.principled(stem,(.15,.08,.03) if wood else (.17,.19,.21),0 if wood else 1,.55,
                     H.image_data(stem+'_BaseColor',np.clip(base,0,1)),normal,
                     H.image_data(stem+'_ORM',orm,'Non-Color'))
    slot=len(ob.data.materials);ob.data.materials.append(new)
    for fi in faces:ob.data.polygons[fi].material_index=slot
    mask_image(stem+'_WearMask',wear);mask_image(stem+'_ScratchMask',scratch)
    if handling is not None:mask_image(stem+'_HandlingMask',handling)
    return {'object':ob.name,'old_material':old.name,'new_material':new.name,'new_slot':slot,
            'faces':sorted(faces),'texture_size':[width,height],
            'changed_channels':['BaseColor','Roughness']+(['wood micro Normal'] if wood else []),
            'underlying_normal':{'name':ni.name,'sha256_float_pixels':image_hash(ni)},
            'overlap_excluded_pixels':int(conflict.sum()) if conflict is not None else 0,
            'wear_max':float(wear.max()),'scratch_max':float(scratch.max())}

def wood(ob,proof):
    caps={f.index for f in ob.data.polygons if len(f.vertices)>4}
    faces=set(range(len(ob.data.polygons)))-caps
    xyz,ids,conf=P.raster(ob,faces,2048)
    assert not conf.any(),(ob.name,'side UV conflict')
    valid=ids>=0;wear=np.zeros(valid.shape,np.float32);scr=np.zeros_like(wear);hand=np.zeros_like(wear)
    stock=ob.name=='Wood_ContinuousStock';ring=80 if stock else 50
    if stock:
        # Butt cap/side real convex adjacency, exposed lower perimeter segments.
        for j,x,l,w,s in [(12,-.374,.006,.003,.8),(16,-.373,.007,.003,.85),(22,-.373,.005,.0025,.65)]:
            wear=np.maximum(wear,stamp(xyz,anchor(ob,x,j,ring),l,w,s))
        if not proof:
            for j,x,l,w,s in [(0,-.322,.019,.0025,.65),(0,-.248,.011,.002,.48),
                              (32,-.298,.013,.0024,.68),(16,-.252,.017,.0026,.7),
                              (16,-.178,.008,.002,.55),(32,-.156,.011,.002,.44),
                              (0,-.035,.013,.002,.5),(32,-.017,.009,.0018,.6),
                              (0,.082,.012,.0015,.4),(32,.176,.017,.0018,.55),
                              (0,.309,.018,.0018,.4),(32,.455,.010,.0017,.48)]:
                wear=np.maximum(wear,stamp(xyz,anchor(ob,x,j,ring),l,w,s))
            for j in (7,25):hand=np.maximum(hand,stamp(xyz,anchor(ob,-.085,j,ring),.035,.022,.7))
    elif not proof:
        for j,x,l,w,s in [(0,.315,.018,.0017,.6),(24,.370,.017,.0017,.65),
                          (12,.483,.017,.0018,.48),(24,.511,.011,.0018,.55),
                          (0,.570,.007,.002,.55)]:
            wear=np.maximum(wear,stamp(xyz,anchor(ob,x,j,ring),l,w,s))
    if not proof:
        rng=np.random.default_rng(1310 if stock else 1320)
        # Deliberate side-surface regions. No random all-UV line field or mirror.
        zones=[(-.345,-.17,6,11,12),(-.34,-.19,21,27,8),(-.11,-.03,6,10,3),
               (.025,.39,4,10,9),(.03,.51,23,29,7)] if stock else [(.275,.409,4,9,7),(.445,.537,15,22,6)]
        for lo,hi,j0,j1,count in zones:
            for _ in range(count):
                x=float(rng.uniform(lo,hi));j=int(rng.integers(j0,j1));length=float(rng.uniform(.010,.039))
                a=anchor(ob,x,j,ring);b=anchor(ob,x+length,j+int(rng.integers(-1,2)),ring)
                scr=np.maximum(scr,stroke(xyz,a,b,float(rng.uniform(.00055,.0009)),float(rng.uniform(.38,.78))))
    wear=pad(wear,valid);scr=pad(scr,valid);hand=pad(hand,valid)
    row=derivative(ob,faces,'V13_'+('Stock' if stock else 'Handguard'),2048,wear,scr,hand,True)
    row['isolated_cap_faces_retaining_original_material']=sorted(caps)
    return row

def steel(ob,proof=False,faces=None,stem=None,anchors=None):
    faces=set(range(len(ob.data.polygons))) if faces is None else set(faces)
    bi,_,_=inputs(ob.data.materials[0]);size=tuple(bi.size)
    xyz,ids,conf=P.raster(ob,faces,size);valid=(ids>=0)&~conf
    wear=np.zeros(valid.shape,np.float32);scr=np.zeros_like(wear);dirt=np.zeros_like(wear)
    if anchors:
        for x,y,z,l,w,s in anchors:
            wear=np.maximum(wear,stamp(xyz,anchor(ob,x,target=(x,y,z)),l,w,s))
    name=ob.name
    if name=='Barrel_Donor_Tapered':
        # Only outer surface beyond fore-end, locally interrupted lengthwise rubs.
        for x,y,z,l,w,s in [( .641,-.009,.002,.016,.0015,.40),(.690,.003,.007,.009,.0012,.5)]:
            wear=np.maximum(wear,stamp(xyz,anchor(ob,x,target=(x,y,z)),l,w,s))
        for x,y,z in [(.621,-.008,.001),(.663,.003,.009),(.697,-.006,.002)]:
            a=anchor(ob,x,target=(x,y,z));b=anchor(ob,x+.025,target=(x+.025,y,z+.001))
            scr=np.maximum(scr,stroke(xyz,a,b,.0004,.6))
        if not proof:
            for x,y,z in [(.604,-.009,-.001),(.648,.005,.004),(.712,-.003,-.005)]:
                dirt=np.maximum(dirt,stamp(xyz,anchor(ob,x,target=(x,y,z)),.024,.005,.5))
    elif name=='Muzzle_Donor_Insert':
        # Only actual crown's outer radius. Bore gets no paint or geometry edit.
        radius=np.sqrt(xyz[:,:,1]**2+xyz[:,:,2]**2)
        wear*=np.clip((radius-.0058)/.001,0,1)
    if not proof and name in {'Receiver_Donor_Lower','Bolt_Donor_HandleCaps','Bolt_Donor_TubeSafety'}:
        pos=positions(ob);lo,hi=pos.min(0),pos.max(0)
        for f in [.25,.68]:
            pt=(lo+hi)*.5;pt[0]=lo[0]+f*(hi[0]-lo[0]);pt[1]=lo[1];pt[2]=hi[2]*.6
            dirt=np.maximum(dirt,stamp(xyz,anchor(ob,pt[0],target=pt),.017,.007,.55))
        rng=np.random.default_rng(1340+len(name))
        for _ in range(5):
            pt=lo+(hi-lo)*rng.uniform(.15,.85,3);pt[1]=lo[1]
            a=anchor(ob,pt[0],target=pt);pt[0]+=.012;b=anchor(ob,pt[0],target=pt)
            scr=np.maximum(scr,stroke(xyz,a,b,.00035,.45))
    # Conflicting donor UV regions remain V12 response, never average positions.
    wear*=valid;scr*=valid;dirt*=valid
    wear=pad(wear,ids>=0);scr=pad(scr,ids>=0);dirt=pad(dirt,ids>=0)
    return derivative(ob,faces,stem or 'V13_'+name,size,wear,scr,dirt,False,conf)

def render_view(name,center,direction,scale,prefix='pbr'):
    scene=bpy.context.scene;scene.camera=H.camera('V13_View_'+prefix+'_'+name,center,direction,scale)
    scene.render.filepath=str(H.OUT/(prefix+'_'+name+'.png'));bpy.ops.render.render(write_still=True)

def evidence(proof):
    scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
    scene.render.resolution_x=1200;scene.render.resolution_y=729;scene.render.resolution_percentage=100
    views=[('stock',(-.283,0,-.085),(.08,-1,.22),.28),('stock_reverse',(-.283,0,-.085),(.08,1,.22),.28),
           ('stock_under',(-.283,0,-.085),(0,-.4,-1),.28),('barrel',(.650,0,.005),(.2,-1,.65),.23)]
    if not proof:
        W.HELPER.OUT=H.OUT
        W.render(['right','left','quarter','top','underside','receiver'],'pbr')
        views += [('handguard',(.43,0,.007),(.1,-1,.7),.36),('muzzle',(.708,0,.006),(1,-1,.6),.09)]
    for view in views:render_view(*view)
    # Actual unlit colour/mask render, not a relit beauty image.
    originals={}
    for mat in {s.material for o in scene.objects if o.type=='MESH' for s in o.material_slots if s.material}:
        nt=mat.node_tree;bs=nt.nodes.get('Principled BSDF');out=nt.nodes.get('Material Output')
        originals[mat.name]=(out.inputs['Surface'].links[0].from_socket)
        em=nt.nodes.new('ShaderNodeEmission');nt.links.new(bs.inputs['Base Color'].links[0].from_socket,em.inputs['Color']);nt.links.new(em.outputs[0],out.inputs['Surface'])
    render_view('stock',(-.283,0,-.085),(.08,-1,.22),.28,'unlit')
    render_view('barrel',(.650,0,.005),(.2,-1,.65),.23,'unlit')
    for name,socket in originals.items():
        nt=bpy.data.materials[name].node_tree;nt.links.new(socket,nt.nodes.get('Material Output').inputs['Surface'])
        for n in list(nt.nodes):
            if n.type=='EMISSION':nt.nodes.remove(n)
    old=[(o,o.data.energy) for o in scene.objects if o.type=='LIGHT']
    for o,_ in old:o.data.energy*=.45 if o.name=='StudioLight0' else 1.6
    render_view('stock',(-.283,0,-.085),(.08,-1,.22),.28,'alternate')
    render_view('barrel',(.650,0,.005),(.2,-1,.65),.23,'alternate')
    for o,energy in old:o.data.energy=energy

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--stage',choices=['proof','final'],required=True);p.add_argument('--no-render',action='store_true')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);out=Path(a.out).resolve();assert not out.exists();out.mkdir(parents=True)
    H.OUT=out;source=BASE/'GermanRifle_M1Texture_V12.blend'
    guard={str(f):W.sha(f) for f in [source,BASE/'GermanRifle_M1Texture_V12.glb']}
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
    H.SCENE=bpy.context.scene;H.PIVOT=P.PIVOT
    before=W.geometry_fingerprint();proof=a.stage=='proof';changes=[]
    allnormals={im.name:image_hash(im) for mat in bpy.data.materials if mat.name.startswith('V12_') for im in [inputs(mat)[1]]}
    changes.append(wood(bpy.data.objects['Wood_ContinuousStock'],proof))
    if not proof:changes.append(wood(bpy.data.objects['Wood_UpperHandguard'],False))
    changes.append(steel(bpy.data.objects['Barrel_Donor_Tapered'],proof))
    changes.append(steel(bpy.data.objects['Muzzle_Donor_Insert'],proof,anchors=[(.726,-.005,.003,.004,.001,.6)]))
    if not proof:
        for name in ['Receiver_Donor_Lower','Bolt_Donor_HandleCaps','Bolt_Donor_TubeSafety']:
            pos=positions(bpy.data.objects[name]);hi=pos.max(0);lo=pos.min(0)
            anchors=[(float((lo[0]+hi[0])*.5),float(lo[1]),float(hi[2]),.010,.002,.4)]
            changes.append(steel(bpy.data.objects[name],anchors=anchors))
        # Existing band's r1-r2 faces are outer shell, separate from r0/r3 inner folds.
        for name in ['Furniture_RearBand','Furniture_FrontBand']:
            ob=bpy.data.objects[name];xyz,ids,conf=P.raster(ob,set(range(58,116)),256)
            assert not conf.any(),(name,'outer shell conflict')
            x=float(positions(ob)[:,0].mean())
            changes.append(steel(ob,faces=range(58,116),anchors=[(x,-.02,-.027,.008,.003,.5),(x,.012,.014,.008,.003,.4)]))
        # Rear plate's external cap is independent; side's tiny out-of-range UV stays read-only.
        ob=bpy.data.objects['Furniture_ButtPlate'];cap=next(f.index for f in ob.data.polygons if f.normal.x<-.9)
        changes.append(steel(ob,faces={cap},anchors=[(-.381,-.015,-.135,.006,.009,.5),(-.381,.014,-.026,.005,.006,.5)]))
        # Guard side UV conflicts disappear when its two overlapping end caps are excluded.
        ob=bpy.data.objects['Guard_OpenBow'];faces={f.index for f in ob.data.polygons if len(f.vertices)==4}
        changes.append(steel(ob,faces=faces,anchors=[(.025,-.005,-.082,.010,.003,.55),(.065,.003,-.065,.007,.002,.4)]))
        # Ambiguous sight/profile UVs are not guessed; original material is protected.
    assert W.geometry_fingerprint()==before,'Protected form changed'
    assert all(image_hash(bpy.data.images[n])==s for n,s in allnormals.items()),'Source structural normal changed'
    if not a.no_render:evidence(proof)
    if not proof:
        bpy.ops.object.select_all(action='DESELECT')
        for ob in bpy.context.scene.objects:
            if ob.type=='MESH' or ob.name=='RifleRoot_Centered':ob.select_set(True)
        bpy.context.view_layer.objects.active=bpy.data.objects['Receiver_Donor_Lower']
        bpy.ops.export_scene.gltf(filepath=str(out/(NAME+'.glb')),export_format='GLB',use_selection=True,
                                 export_yup=True,export_vertex_color='NONE',export_animations=False,export_apply=True)
    bpy.context.preferences.filepaths.save_version=0
    bpy.context.scene.camera=bpy.data.objects['View_pbr_quarter']
    bpy.ops.wm.save_as_mainfile(filepath=str(out/(NAME+'.blend')))
    assert all(W.sha(Path(f))==s for f,s in guard.items())
    report={'stage':a.stage,'name':NAME,'blender':bpy.app.version_string,'baseline_files':guard,'geometry_before':before,
            'geometry_after':W.geometry_fingerprint(),'geometry_exact':True,'pivot_shift':list(P.PIVOT),'changes':changes,
            'anchors':RECORD,'source_normal_hashes':allnormals,'source_normals_unchanged':True,
            'protected_ambiguous_parts':['Sight_RearBed','Sight_FrontBed','Sight_FrontBlade'],
            'limitation':'Original ambiguous sight UV response retained; no localized marks claimed there.',
            'material_correction':'One local contrast correction after finish_v1; same masks, geometry, light and mark count.',
            'user_visual_approval':False,'runtime_approval':False,'shared':False,'cloud_spend':0}
    for suffix in ['blend','glb']:
        path=out/(NAME+'.'+suffix)
        if path.exists():report['sha256_'+suffix]=W.sha(path)
    (out/'build_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({k:report[k] for k in ['stage','geometry_exact','source_normals_unchanged']}),flush=True)
if __name__=='__main__':main()
