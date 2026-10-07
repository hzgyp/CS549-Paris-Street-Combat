"""Unoccluded static hand views; full body retained separately, no pose edit."""
import sys,traceback
from pathlib import Path
import bpy,numpy as np
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'GermanNPCGripV1'))
from common import ROOT,STORE,read,write,row,sha,guards
sys.path.insert(0,str(ROOT/'Tools/Integration/WeaponTriggerAlignmentV2'))
from blender_contact_common import mat,transform
BASE=STORE/'Evidence/GermanNPCAlliedGripV13';OUT=BASE/('presentation_v2' if '--reframe' in sys.argv else 'presentation_v1')
BLEND=BASE/'textured_v3/GermanGraspDiagnostic.blend';PROOF=BASE/'textured_v3/result.json'
GD=STORE/'Evidence/GermanNPCOrderedGripV4/offline_v6/geometry.npz'
FITS={'transfer':BASE/'transfer_fit_v2/result.json','seating':BASE/'seating_v3/result.json'}
assert not OUT.exists();OUT.mkdir(parents=True)
r={'status':'starting','errors':[],'guards_before':guards(),'inputs':[row(p) for p in (BLEND,PROOF,GD,*FITS.values(),Path(__file__))],
   'source_modified':False,'formal_selected':False,'native_tested':False,'images':[],
   'isolation_is_presentation_only':True,'full_body_context_retained':True,'portable_jacket_not_native_camo_parity':True}
try:
    proof=read(PROOF);assert not proof['errors'];d=np.load(GD);w=d['weights'];tri=d['skin_triangles']
    fits={s:read(p) for s,p in FITS.items()};names=fits['seating']['bone_names'];origin=mat(fits['seating']['after_bones']['hand_r'])[:3,3]
    bpy.ops.wm.open_mainfile(filepath=str(BLEND),load_ui=False,use_scripts=False)
    body=bpy.data.objects['Full German source topology - diagnostic ONLY'];gun=bpy.data.objects['Actual German rifle original topology']
    hands_weight=w[:,[j for j,n in enumerate(names) if n.startswith(('hand_','thumb_','index_','middle_','ring_','pinky_'))]].sum(1)
    ids=np.flatnonzero(np.any((hands_weight>.5)[tri],axis=1));assert len(ids)>1000
    md=bpy.data.meshes.new('Unchanged existing hand triangles');md.from_pydata([list(v.co) for v in body.data.vertices],[],tri[ids,::-1].tolist());md.update()
    obj=bpy.data.objects.new('Hand closeup isolation - NOT a runtime asset',md);bpy.context.collection.objects.link(obj)
    for m in body.data.materials:md.materials.append(m)
    for poly,orig in zip(md.polygons,ids):poly.material_index=body.data.polygons[int(orig)].material_index;poly.use_smooth=True
    for uv in body.data.uv_layers:
        layer=md.uv_layers.new(name=uv.name)
        coords=np.array([[list(uv.data[i].uv) for i in body.data.polygons[int(orig)].loop_indices] for orig in ids]).reshape(-1,2)
        for item,co in zip(layer.data,coords):item.uv=co
    r['isolation_triangles']=len(ids);scene=bpy.context.scene;cam=scene.camera
    for stage,fit in fits.items():
        saved=np.load(FITS[stage].parent/'geometry.npz');p=saved['skin'];g=saved['gun_after_cm']
        for o,pts in ((body,p),(obj,p),(gun,g)):
            for vert,co in zip(o.data.vertices,(pts-origin)*.01):vert.co=co
            o.data.update()
        bones={n:mat(v) for n,v in fit['after_bones'].items()};right=bones['hand_r'][:3,3];left=bones['hand_l'][:3,3]
        idx=(bones['index_02_r'][:3,3]+bones['index_03_r'][:3,3])/2
        right_mask=w[:,[j for j,n in enumerate(names) if n.endswith('_r') and n.startswith(('hand_','thumb_','index_','middle_','ring_','pinky_'))]].sum(1)>.5
        right_center=p[right_mask].mean(0)
        left_mask=w[:,[j for j,n in enumerate(names) if n.endswith('_l') and n.startswith(('hand_','thumb_','index_','middle_','ring_','pinky_'))]].sum(1)>.5
        left_center=p[left_mask].mean(0)
        r.setdefault('camera_centers_cm',{})[stage]={'right':right_center.tolist(),'left':left_center.tolist()}
        for name,offset,width,target in [('right',(0,-.5,.06),.33,right_center),('reverse',(0,.5,.06),.33,right_center),('top',(0,0,.5),.36,right_center),
            ('under',(0,0,-.5),.36,right_center),
            ('trigger',(0,-.5,.06),.16,idx),('support',(0,-.5,.08),.38,left_center),('context',(0,-2,.28),1.3,(right+left)/2)]:
            body.hide_render=name!='context';obj.hide_render=name=='context'
            center=Vector((target-origin)*.01);cam.location=center+Vector(offset);cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=width
            dest=OUT/(stage+'_'+name+'.png');scene.render.filepath=str(dest);bpy.ops.render.render(write_still=True);r['images'].append(row(dest));write(OUT/'result.json',r)
    body.hide_render=False;obj.hide_render=True
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'GermanGraspPresentationDiagnostic.blend'))
    r['status']='unoccluded_textured_hand_comparison_not_contact_or_native_acceptance'
except Exception:r['status']='presentation_failed_preserved';r['errors'].append(traceback.format_exc())
finally:
    r['guards_after']=guards();r['inputs_unchanged']=all(sha(ROOT/e['path'])==e['sha256'] for e in r['inputs']);write(OUT/'result.json',r)
    print(r['status'],r['errors'])
