"""ONE fixed stock-grip pivot rotation raises the muzzle toward the unchanged index."""
import sys
import hashlib
import traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'WeaponTriggerPivotV12'))
from pivot_common import *

BASE = STORE/'Evidence/WeaponGripPivotV15'
PREVIOUS = STORE/'Evidence/WeaponThumbGunSeatV14/thumb_seat_v1/result.json'
LANDMARK = STORE/'Evidence/WeaponTriggerPivotV12/landmarks_v1/result.json'
OUT = BASE/'grip_raise_v1'
assert not OUT.exists()
OUT.mkdir(parents=True)
inputs = [FBX,POSES,AUDIT,CALIB,TOPOLOGY,INDEX,PREVIOUS,LANDMARK,Path(__file__),
          Path(__file__).resolve().parents[1]/'WeaponTriggerPivotV12/pivot_common.py',
          Path(__file__).resolve().parents[1]/'WeaponWholeWristV11/wrist_common.py',
          Path(__file__).resolve().parents[1]/'WeaponTriggerAlignmentV2/blender_contact_common.py']
hashes = {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
r = {'errors':[],'views':[],'native_authored':False,'candidate_count':1,'scope':__doc__,'phase_s':0.}
def write():
    (OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')

try:
    r['guards_before'] = guarded_files()
    assert not r['guards_before']['mismatches']
    d = load()
    previous = json.loads(PREVIOUS.read_text())
    landmark = json.loads(LANDMARK.read_text())
    assert not previous['errors']
    bones = {n:np.array(v) for n,v in previous['baseline_component_bones'].items()}
    gun0 = np.array(previous['baseline_gun_component_matrix'])
    change0 = np.array(previous['rigid_change_gun_local'])
    points = evaluate(d,bones,gun0)
    gun_before = transform(d['gp'],change0)
    stock_ids = np.array(next(c for c in d['topo']['components'] if c['id']==0)['triangle_ids'],int)
    thumb_ids = np.flatnonzero(np.all(d['digits']['thumb'][d['tri']],axis=1))
    centers = points[d['tri'][thumb_ids]].mean(1)
    _,areas = normals(points,d['tri'])
    tree = BVHTree.FromPolygons([Vector(p) for p in gun_before],d['gt'][stock_ids].tolist(),all_triangles=True)
    pairs = []
    for face,point in zip(thumb_ids,centers):
        q,n,wood,gap = tree.find_nearest(Vector(point))
        if gap<=.35:
            qlocal = transform(np.array(q)[None],np.linalg.inv(change0))[0]
            pairs.append({'thumb_triangle':int(face),'stock_triangle':int(stock_ids[wood]),
                          'stock_point_current_cm':list(q),'stock_point_local_cm':qlocal.tolist(),
                          'skin_point_cm':point.tolist(),'area':float(areas[face]),'gap_cm':float(gap)})
    assert len(pairs)>=3,'No actual seated thumb/wood contact patch'
    section_y = float(np.average([p['stock_point_local_cm'][1] for p in pairs],weights=[p['area'] for p in pairs]))
    section = []
    for tri_id in stock_ids:
        tri = d['gp'][d['gt'][tri_id]]
        for a,b in ((0,1),(1,2),(2,0)):
            pa,pb = tri[a],tri[b]
            if (pa[1]-section_y)*(pb[1]-section_y)<0:
                q = pa+(pb-pa)*(section_y-pa[1])/(pb[1]-pa[1])
                section.append(q)
    section = np.unique(np.round(section,8),axis=0)
    assert len(section)>=6,'Stock transverse section not established'
    low,high = section.min(0),section.max(0)
    pivot_local = (low+high)/2
    pivot_local[1] = section_y
    pivot = transform(pivot_local[None],change0)[0]
    pad_id = int(landmark['actual_index_pad_triangle'])
    target = points[d['tri'][pad_id]].mean(0)
    # Known actual blade landmark, not hand socket hollow or trigger-guard center.
    blade_local = np.array(landmark['trigger_pivot_gun_cm'])
    blade_before = transform(blade_local[None],change0)[0]
    a,b = blade_before-pivot,target-pivot
    angle = float(np.degrees(np.arccos(np.clip(a@b/(np.linalg.norm(a)*np.linalg.norm(b)),-1,1))))
    rotation = swing(a,b)
    raise_change = np.eye(4)
    raise_change[:3,:3] = rotation
    raise_change[:3,3] = pivot-rotation@pivot
    change = raise_change@change0
    gun_after = transform(d['gp'],change)
    new_gun = gun0@change
    component_change = new_gun@np.linalg.inv(gun0)
    new_bones = left_chain(d,bones,component_change@bones['hand_l'])
    after = evaluate(d,new_bones,gun0)
    tip_id = int(np.argmax(d['gp'][:,1]))
    muzzle_raise = float(gun_after[tip_id,2]-gun_before[tip_id,2])
    r.update(additional_rotation_degrees=angle,thumb_contact_pairs=pairs,
             stock_section_y_local_cm=section_y,stock_section_local_cm=section.tolist(),
             grip_pivot_local_cm=pivot_local.tolist(),grip_pivot_baseline_frame_cm=pivot.tolist(),
             blade_landmark_before_cm=blade_before.tolist(),index_target_cm=target.tolist(),
             blade_landmark_after_cm=transform(blade_local[None],change)[0].tolist(),
             radial_distance_difference_cm=float(abs(np.linalg.norm(a)-np.linalg.norm(b))),
             muzzle_height_increase_cm=muzzle_raise,rigid_change_gun_local=change.tolist(),
             additional_grip_rotation_matrix=raise_change.tolist())
    assert angle<=30 and muzzle_raise>0,'Derived rotation is not bounded muzzle raising'
    parent = d['model']['parents']
    digit_names = [n for n in bones if n.startswith(('index_','middle_','ring_','pinky_','thumb_'))]
    finger_error = max(float(np.max(abs(np.linalg.inv(bones[parent[n]])@bones[n]
                                       -np.linalg.inv(new_bones[parent[n]])@new_bones[n]))) for n in digit_names)
    right_error = float(np.max(np.linalg.norm(after[d['masks']['r']]-points[d['masks']['r']],axis=1)))
    left_reference = transform(points,change)
    left_mask = np.array([w.get('hand_l',0)>.98 for w in d['weights']])
    left_faces = np.flatnonzero(np.all(left_mask[d['tri']],axis=1))
    left_error = float(np.max(np.linalg.norm(after[d['tri'][left_faces]]-left_reference[d['tri'][left_faces]],axis=2)))
    arm_errors = [float(abs(np.linalg.norm(bones[a][:3,3]-bones[b][:3,3])
                               -np.linalg.norm(new_bones[a][:3,3]-new_bones[b][:3,3])))
                  for a,b in (('upperarm_l','lowerarm_l'),('lowerarm_l','hand_l'))]
    edge_result = edge_check(d,points,after)
    after_contact = contact(d,after,gun_after,pad_id)
    final_stock = BVHTree.FromPolygons([Vector(p) for p in gun_after],d['gt'][stock_ids].tolist(),all_triangles=True)
    thumb_samples = np.concatenate([points[d['digits']['thumb']],centers])
    gap = min(float(final_stock.find_nearest(Vector(p))[3]) for p in thumb_samples)
    pivot_error = float(np.linalg.norm(transform(pivot[None],raise_change)[0]-pivot))
    idx = after_contact['digits']['index']
    r['early_gate_passed'] = bool(pivot_error<.001 and right_error<.0001 and finger_error<1e-10
                                 and after_contact['digits']['thumb']['all_gun']==0 and gap<=.3
                                 and idx['stock']==0 and idx['guard']==0
                                 and after_contact['index_pad_to_blade_cm']<=.2
                                 and max(arm_errors)<.001 and not edge_result['new_severe_edges']
                                 and left_error<=previous['checks']['left_palm_tracking_error_cm']+.01)
    r.update(after_contact=after_contact,previous_contact=previous['after_contact'],
             checks=dict(pivot_error_cm=pivot_error,right_skin_delta_cm=right_error,
                         finger_local_matrix_delta=finger_error,left_palm_tracking_error_cm=left_error,
                         previous_left_palm_tracking_error_cm=previous['checks']['left_palm_tracking_error_cm'],
                         arm_length_errors_cm=arm_errors,thumb_nearest_stock_gap_cm=gap,**edge_result),
             baseline_component_bones={n:v.tolist() for n,v in bones.items()},
             candidate_component_bones={n:v.tolist() for n,v in new_bones.items()},
             baseline_gun_component_matrix=gun0.tolist(),candidate_gun_component_matrix=new_gun.tolist(),
             new_gun_hand_relative_matrix=(np.linalg.inv(bones['hand_r'])@new_gun).tolist())
    write()
    scene = setup_scene()
    scene.render.resolution_x,scene.render.resolution_y = 1200,900
    mats = [material('Wood',(.21,.14,.09)),material('Metal',(.18,.21,.22)),
            material('Unchanged right hand',(.61,.42,.29)),material('Unchanged index',(1.,.26,.07)),
            material('Unchanged thumb',(.8,.53,.22)),material('Left support',(.19,.43,.61)),
            material('Source sleeve',(.23,.27,.16))]
    rt = d['tri'][np.all(d['masks']['r'][d['tri']],axis=1)]
    lt = d['tri'][np.all(d['masks']['l'][d['tri']],axis=1)]
    stock_set = set(stock_ids)
    previous_bones = {n:np.array(v) for n,v in previous['candidate_component_bones'].items()}
    previous_points = evaluate(d,previous_bones,gun0)
    objects = []
    for condition,sp,gp in [('seated_v14',previous_points,gun_before),('raised_v15',after,gun_after)]:
        for obj in objects:
            bpy.data.objects.remove(obj,do_unlink=True)
        rifle = mesh('Rifle '+condition,gp,d['gt'],mats[:2])
        for poly in rifle.data.polygons:
            poly.material_index = int(poly.index not in stock_set)
        right = mesh('Fixed right '+condition,sp,rt,mats[2:5])
        for poly,face in zip(right.data.polygons,rt):
            poly.material_index = 1 if np.all(d['digits']['index'][face]) else (2 if np.all(d['digits']['thumb'][face]) else 0)
        left = mesh('Support '+condition,sp,lt,[mats[5]])
        objects = [rifle,right,left]
        for view,offset in [('right',(.28,-.05,.10)),('opposite',(-.28,-.05,-.08)),
                            ('top',(.02,-.04,.30)),('bottom',(.02,-.04,-.30)),('oblique',(-.20,-.25,.20))]:
            camera([-.035,-.02,-.025],offset,.26)
            file = condition+'_'+view+'.png'
            scene.render.filepath = str(OUT/file)
            bpy.ops.render.render(write_still=True)
            r['views'].append({'file':file,'condition':condition,'view':view})
        camera([0,.225,-.02],(-.25,.02,.20),.36)
        file = condition+'_left_support.png'
        scene.render.filepath = str(OUT/file)
        bpy.ops.render.render(write_still=True)
        r['views'].append({'file':file,'condition':condition,'view':'left_support'})
        right.hide_render = left.hide_render = True
        full = mesh('Continuous arms '+condition,sp,d['tri'],[mats[6],mats[2],mats[5]])
        for poly,face in zip(full.data.polygons,d['tri']):
            poly.material_index = 1 if np.all(d['masks']['r'][face]) else (2 if np.all(d['masks']['l'][face]) else 0)
        objects.append(full)
        camera([0,.12,-.1],(-1.2,-.1,.45),1.2)
        file = condition+'_whole_arms.png'
        scene.render.filepath = str(OUT/file)
        bpy.ops.render.render(write_still=True)
        r['views'].append({'file':file,'condition':condition,'view':'whole_arms'})
        full.hide_render = True
        right.hide_render = left.hide_render = False
        write()
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'FixedGripMuzzleRaise.blend'))
    r['saved_comparison'] = 'FixedGripMuzzleRaise.blend'
    r['status'] = 'static_contact_screen_passed_pending_visual' if r['early_gate_passed'] else 'contact_or_continuity_gate_failed_retained'
except Exception:
    r['status'] = 'stopped'
    r['errors'].append(traceback.format_exc())
finally:
    r['input_hashes'] = hashes
    r['inputs_unchanged'] = all(hashlib.sha256((ROOT/k).read_bytes()).hexdigest()==v for k,v in hashes.items())
    r['guards_after'] = guarded_files()
    write()
    print(json.dumps({k:r.get(k) for k in ('status','errors','additional_rotation_degrees',
                                          'radial_distance_difference_cm','muzzle_height_increase_cm',
                                          'early_gate_passed','after_contact','checks','inputs_unchanged')}))
