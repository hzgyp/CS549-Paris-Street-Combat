"""Reuse ONLY existing2.2s right-index local rotations, gun fixed at V2; no source edits."""
import sys,json,hashlib,traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from blender_contact_common import *
OUT=STORE/'Evidence/WeaponTriggerAlignmentV2/index_pose_v1';assert not OUT.exists();OUT.mkdir(parents=True)
PIVOT=STORE/'Evidence/WeaponTriggerAlignmentV2/pivot_fit_v2/result.json'
inputs=[FBX,POSES,AUDIT,CALIB,TOPOLOGY,PIVOT,Path(__file__),Path(__file__).with_name('blender_contact_common.py')]
hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
for p in inputs[-2:]:(OUT/p.name).write_bytes(p.read_bytes())
r={'scope':__doc__,'errors':[],'phases':[],'views':[],'native_modified':False,'source_clip_modified':False,'authorized_local_rotations_only':['index_01_r','index_02_r','index_03_r'],'limitations':['Offline clipped source pose evidence, not native transition/gameplay acceptance.','Blade surface crossing remains an explicit contact limitation.']}
def write():(OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n')
try:
    d=load();pivot=json.loads(PIVOT.read_text());assert not pivot['errors'] and pivot['rotation_gate_passed'] and pivot['inputs_unchanged']
    candidate=np.array(pivot['candidate']['new_hand_relative_matrix']);gp,gt=d['gp'],d['gt'];tri=d['tri'];parents=d['model']['parents']
    index=('index_01_r','index_02_r','index_03_r');_,source=posed(d,'2.2')
    target={n:np.linalg.inv(source[parents[n]])@source[n] for n in index}
    r['reused_pose']={'clip':json.loads(POSES.read_text())['clips']['owner_reload']['asset'],'phase_s':2.2,'local_transforms':{n:t.tolist() for n,t in target.items()}}
    r['gun_hand_relative_matrix']=candidate.tolist();r['source_coordinate_determinant']=d['coordinate_determinant']
    scene=setup_scene();grey=material('Gun',(.14,.17,.20));metal=material('Trigger',(.15,.65,.7));tan=material('Right hand',(.62,.42,.27));orange=material('Right index',(1,.22,.04));blue=material('Left support',(.18,.45,.65))
    gun=mesh('Frozen V2 M1',gp,gt,[grey,metal]);parts={c['id']:set(c['triangle_ids']) for c in d['topo']['components']}
    for i in parts[5]:gun.data.polygons[i].material_index=1
    righttri=tri[np.all(d['masks']['r'][tri],axis=1)];lefttri=tri[np.all(d['masks']['l'][tri],axis=1)];idxtri=tri[np.all(d['digits']['index'][tri],axis=1)]
    visible=[]
    for phase in d['poses']:
        original,b=posed(d,phase);new=dict(b);deltas={}
        for n in index:
            local=np.linalg.inv(b[parents[n]])@b[n];corrected=local.copy()
            scale=np.linalg.norm(local[:3,:3],axis=0);corrected[:3,:3]=target[n][:3,:3]/np.linalg.norm(target[n][:3,:3],axis=0)*scale
            relative_rotation=(local[:3,:3]/scale).T@(corrected[:3,:3]/scale)
            deltas[n]=float(np.degrees(np.arccos(np.clip((np.trace(relative_rotation)-1)*.5,-1,1))))
            assert np.max(abs(local[:3,3]-corrected[:3,3]))==0
            new[n]=new[parents[n]]@corrected
        others=max(float(np.max(abs(new[n]-b[n]))) for n in b if n not in index);assert others==0,'Other bones changed'
        p=skin(d['p'],d['weights'],{n:new[n]@d['invref'][n] for n in d['invref'] if n in new})
        local=transform(p,np.linalg.inv(new['hand_r']@candidate));before=transform(original,np.linalg.inv(b['hand_r']@candidate))
        pairs=intersection_pairs(local,idxtri,gp,gt)
        row={'phase_s':float(phase),'joint_rotation_change_deg':deltas,'other_bone_matrix_delta':others,'index_local_translation_scale_unchanged':True,
          'index_stock_crossing_triangles':len({i for i,j in pairs if j in parts[0]}),'index_guard_crossing_triangles':len({i for i,j in pairs if j in parts[4]}),
          'index_trigger_crossing_triangles':len({i for i,j in pairs if j in parts[5]}),'index_all_crossing_triangles':len({i for i,j in pairs})}
        # Record actual displayed pad, not just target rotation or bone equality.
        ids=np.array([pivot['landmarks']['pad_source_triangle_id']]);pad,normal,pad_id,_=project(local,tri[ids],ids,local[tri[ids]].mean((0,1)))
        bladeids=np.array(list(parts[5]));blade,bn,_,distance=project(gp,gt[bladeids],bladeids,pad);row['actual_pad_to_blade_distance_cm']=distance
        r['phases'].append(row);write()
        if phase not in ('0.0','2.2','4.1'):continue
        center=np.mean(local[d['digits']['index']],axis=0)*.01
        for condition,points in [('gun_only_v2',before),('existing_index_pose_v3',local)]:
            for o in visible:bpy.data.objects.remove(o,do_unlink=True)
            hand=mesh('Right hand '+condition,points,righttri,[tan,orange]);left=mesh('Left hand unchanged',points,lefttri,[blue]);visible=[hand,left]
            for poly,f in zip(hand.data.polygons,righttri):poly.material_index=int(np.all(d['digits']['index'][f]))
            for view,targetpoint,offset,scale in [('right',center,(.28,-.05,.10),.26),('left',center,(-.28,-.05,.10),.26),('top',center,(.02,-.04,.30),.26),('whole',[0,.22,0],(-1.2,.05,.4),1.2)]:
                camera(targetpoint,offset,scale);file=f'{phase}_{condition}_{view}.png';scene.render.filepath=str(OUT/file);bpy.ops.render.render(write_still=True);r['views'].append({'file':file,'phase_s':float(phase),'condition':condition,'view':view});write()
            left.hide_render=True;camera(center,(-.28,-.05,-.08),.24);file=f'{phase}_{condition}_right_contact_only.png';scene.render.filepath=str(OUT/file);bpy.ops.render.render(write_still=True);left.hide_render=False;r['views'].append({'file':file,'phase_s':float(phase),'condition':condition,'view':'right_contact_only'});write()
            if condition=='existing_index_pose_v3':
                hand.hide_render=True;left.hide_render=True;full=mesh('Whole arms source weights',points,tri,[tan]);visible.append(full)
                camera([0,.12,-.10],(-1.2,-.1,.45),1.2);file=f'{phase}_{condition}_full_arms.png';scene.render.filepath=str(OUT/file);bpy.ops.render.render(write_still=True);full.hide_render=True;hand.hide_render=False;left.hide_render=False;r['views'].append({'file':file,'phase_s':float(phase),'condition':condition,'view':'full_arms'});write()
    r['stock_guard_gate_passed']=all(x['index_stock_crossing_triangles']==0 and x['index_guard_crossing_triangles']==0 for x in r['phases'])
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'ExistingIndexPoseContact.blend'));r['status']='existing_pose_comparison_collected_requires_visual_review'
except Exception:r['status']='stopped';r['errors'].append(traceback.format_exc())
finally:
    r['inputs_unchanged']=all(hashlib.sha256((ROOT/k).read_bytes()).hexdigest()==v for k,v in hashes.items());r['input_hashes']=hashes;write();print(json.dumps({k:r[k] for k in ('status','errors','inputs_unchanged')}))
