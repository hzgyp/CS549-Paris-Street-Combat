"""ONE gun-only surface-height fit: fixed right thumb above the stock; other three digits non-gating."""
import sys
import hashlib
import traceback
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'WeaponTriggerPivotV12'))
from pivot_common import *

BASE = STORE / 'Evidence/WeaponThumbGunSeatV14'
PROBE = STORE / 'Evidence/WeaponTriggerPivotV12/landmarks_v1/result.json'
PREVIOUS = STORE / 'Evidence/WeaponTriggerPivotV13/pivot_20deg_v1b/result.json'
SURFACE = BASE / 'surface_probe_v1/result.json'
OUT = BASE / 'thumb_seat_v1'
assert not OUT.exists(), 'Preserve earlier experiment identities'
OUT.mkdir(parents=True)
inputs = [FBX, POSES, AUDIT, CALIB, TOPOLOGY, INDEX, PROBE, PREVIOUS, SURFACE,
          Path(__file__), Path(__file__).resolve().parents[1]/'WeaponTriggerPivotV12/pivot_common.py',
          Path(__file__).resolve().parents[1]/'WeaponWholeWristV11/wrist_common.py',
          Path(__file__).resolve().parents[1]/'WeaponTriggerAlignmentV2/blender_contact_common.py']
hashes = {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
r = {'errors':[], 'views':[], 'native_authored':False, 'candidate_count':1,
     'scope':__doc__, 'phase_s':0., 'non_gating_digits':['middle','ring','pinky']}

def write():
    (OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')

try:
    r['guards_before'] = guarded_files()
    assert not r['guards_before']['mismatches']
    d = load()
    probe = json.loads(PROBE.read_text())
    old_bones = {n:np.array(v) for n,v in probe['baseline_component_bones'].items()}
    old_gun = np.array(probe['baseline_gun_component_matrix'])
    points = evaluate(d,old_bones,old_gun)
    axis = np.array(probe['gun_local_turn_axis'])
    pivot = np.array(probe['trigger_pivot_gun_cm'])
    angle = float(probe['landmark_full_alignment_angle_deg'])
    assert 0 < angle <= 45
    change = np.eye(4)
    change[:3,:3] = np.array(Quaternion(Vector(axis),np.radians(angle)).to_matrix())
    change[:3,3] = pivot - change[:3,:3]@pivot
    mark = np.array(probe['direction_landmark']['stock_point_cm'])
    palm = np.array(probe['direction_landmark']['palm_point_cm'])
    rotated_mark = transform(mark[None],change)[0]
    # Close the actual palm-facing side laterally, not toward an invented bone center.
    translation = np.array([palm[0]+.12-rotated_mark[0],0.,0.])
    change[:3,3] += translation
    gun_points = transform(d['gp'],change)
    stock = np.array(next(c for c in d['topo']['components'] if c['id']==0)['triangle_ids'],int)
    thumb_mask = d['digits']['thumb']
    thumb_faces = d['tri'][np.all(thumb_mask[d['tri']],axis=1)]
    thumb_vertices = np.flatnonzero(thumb_mask)
    # Actual underside samples cover vertices, triangle centers and edge midpoints.
    edges = np.unique(np.sort(np.concatenate([thumb_faces[:,[0,1]],thumb_faces[:,[1,2]],thumb_faces[:,[2,0]]]),axis=1),axis=0)
    samples = np.concatenate([points[thumb_vertices],points[thumb_faces].mean(1),points[edges].mean(1)])
    tree = BVHTree.FromPolygons([Vector(p) for p in gun_points],d['gt'][stock].tolist(),all_triangles=True)
    hits = []
    for sample in samples:
        loc,normal,face,distance = tree.ray_cast(Vector((sample[0],sample[1],1000.)),Vector((0,0,-1)),2000.)
        if loc is not None:
            hits.append({'thumb_sample_cm':sample.tolist(),'stock_upper_cm':list(loc),
                         'stock_face':int(stock[face]),'vertical_gap_cm':float(sample[2]-loc.z)})
    assert len(hits)>=10, 'No broad thumb-above-stock footprint proved'
    # A single conservative surface-height placement, no angle/offset sweep.
    translation[2] = min(h['vertical_gap_cm'] for h in hits)-.10
    change[2,3] += translation[2]
    r.update(rotation_degrees=angle,extra_translation_cm=translation.tolist(),
             surface_height_sample_count=len(samples),stock_hit_count=len(hits),surface_hits=hits,
             minimum_projected_thumb_stock_gap_cm=.10)
    assert np.linalg.norm(translation)<=4., 'One surface seating exceeds bounded displacement'
    gun_points = transform(d['gp'],change)
    new_gun = old_gun@change
    component_change = new_gun@np.linalg.inv(old_gun)
    new_bones = left_chain(d,old_bones,component_change@old_bones['hand_l'])
    after = evaluate(d,new_bones,old_gun)
    pad_id = int(probe['actual_index_pad_triangle'])
    after_contact = contact(d,after,gun_points,pad_id)
    parents = d['model']['parents']
    digits = [n for n in old_bones if n.startswith(('index_','middle_','ring_','pinky_','thumb_'))]
    finger_error = max(float(np.max(abs(np.linalg.inv(old_bones[parents[n]])@old_bones[n]
                                       -np.linalg.inv(new_bones[parents[n]])@new_bones[n]))) for n in digits)
    right_error = float(np.max(np.linalg.norm(after[d['masks']['r']]-points[d['masks']['r']],axis=1)))
    right_bone_error = max(float(np.max(abs(old_bones[n]-new_bones[n]))) for n in old_bones if n.endswith('_r'))
    left_reference = transform(points,change)
    palm_mask = np.array([w.get('hand_l',0)>.98 for w in d['weights']])
    palm_faces = np.flatnonzero(np.all(palm_mask[d['tri']],axis=1))
    left_error = float(np.max(np.linalg.norm(after[d['tri'][palm_faces]]-left_reference[d['tri'][palm_faces]],axis=2)))
    arm_errors = [float(abs(np.linalg.norm(old_bones[a][:3,3]-old_bones[b][:3,3])
                               -np.linalg.norm(new_bones[a][:3,3]-new_bones[b][:3,3])))
                  for a,b in (('upperarm_l','lowerarm_l'),('lowerarm_l','hand_l'))]
    edge_result = edge_check(d,points,after)
    # Skin nearest distance is reported separately from the footprint height.
    final_tree = BVHTree.FromPolygons([Vector(p) for p in gun_points],d['gt'][stock].tolist(),all_triangles=True)
    thumb_gaps = [float(final_tree.find_nearest(Vector(p))[3]) for p in samples]
    checks = dict(right_skin_delta_cm=right_error,right_bone_matrix_delta=right_bone_error,
                  finger_local_matrix_delta=finger_error,left_palm_tracking_error_cm=left_error,
                  arm_length_errors_cm=arm_errors,thumb_nearest_stock_gap_cm=min(thumb_gaps),**edge_result)
    thumb = after_contact['digits']['thumb']
    r['early_gate_passed'] = bool(thumb['all_gun']==0 and thumb['stock']==0 and min(thumb_gaps)<=.3
                                and right_error<.0001 and right_bone_error<1e-10 and finger_error<1e-10
                                and left_error<.02 and max(arm_errors)<.001 and not edge_result['new_severe_edges'])
    r.update(checks=checks,after_contact=after_contact,
             previous_20deg_contact=json.loads(PREVIOUS.read_text())['after_contact'],
             rigid_change_gun_local=change.tolist(),
             baseline_component_bones={n:v.tolist() for n,v in old_bones.items()},
             candidate_component_bones={n:v.tolist() for n,v in new_bones.items()},
             baseline_gun_component_matrix=old_gun.tolist(),candidate_gun_component_matrix=new_gun.tolist(),
             new_gun_hand_relative_matrix=(np.linalg.inv(old_bones['hand_r'])@new_gun).tolist())
    write()
    scene = setup_scene()
    scene.render.resolution_x,scene.render.resolution_y = 1200,900
    wood = material('Wood surface diagnostic',(.21,.14,.09))
    metal = material('Metal',(.18,.21,.22))
    skinmat = material('Unmodified right hand',(.61,.42,.29))
    orange = material('Protected index', (1.,.26,.07))
    gold = material('Unmodified thumb',(.8,.53,.22))
    blue = material('Following support hand',(.19,.43,.61))
    garment = material('Original sleeve',(.23,.27,.16))
    rt = d['tri'][np.all(d['masks']['r'][d['tri']],axis=1)]
    lt = d['tri'][np.all(d['masks']['l'][d['tri']],axis=1)]
    stock_ids = set(stock)
    visible = []
    previous = json.loads(PREVIOUS.read_text())
    previous_bones = {n:np.array(v) for n,v in previous['candidate_component_bones'].items()}
    previous_points = evaluate(d,previous_bones,old_gun)
    previous_gun = transform(d['gp'],np.array(previous['rigid_pivot_change_gun_local']))
    for condition,sp,gp in [('previous20',previous_points,previous_gun),('thumb_seated',after,gun_points)]:
        for obj in visible:
            bpy.data.objects.remove(obj,do_unlink=True)
        rifle = mesh('Rifle '+condition,gp,d['gt'],[wood,metal])
        for poly in rifle.data.polygons:
            poly.material_index = int(poly.index not in stock_ids)
        right = mesh('Fixed right '+condition,sp,rt,[skinmat,orange,gold])
        for poly,face in zip(right.data.polygons,rt):
            poly.material_index = 1 if np.all(d['digits']['index'][face]) else (2 if np.all(thumb_mask[face]) else 0)
        left = mesh('Support '+condition,sp,lt,[blue])
        visible = [rifle,right,left]
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
        full = mesh('Continuous arms '+condition,sp,d['tri'],[garment,skinmat,blue])
        for poly,face in zip(full.data.polygons,d['tri']):
            poly.material_index = 1 if np.all(d['masks']['r'][face]) else (2 if np.all(d['masks']['l'][face]) else 0)
        visible.append(full)
        camera([0,.12,-.1],(-1.2,-.1,.45),1.2)
        file = condition+'_whole_arms.png'
        scene.render.filepath = str(OUT/file)
        bpy.ops.render.render(write_still=True)
        r['views'].append({'file':file,'condition':condition,'view':'whole_arms'})
        full.hide_render = True
        right.hide_render = left.hide_render = False
        write()
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'FixedHandThumbSeat.blend'))
    r['saved_comparison'] = 'FixedHandThumbSeat.blend'
    r['status'] = 'static_thumb_screen_passed_pending_multiview' if r['early_gate_passed'] else 'thumb_or_continuity_gate_failed_retained'
except Exception:
    r['status'] = 'stopped'
    r['errors'].append(traceback.format_exc())
finally:
    r['input_hashes'] = hashes
    r['inputs_unchanged'] = all(hashlib.sha256((ROOT/k).read_bytes()).hexdigest()==v for k,v in hashes.items())
    r['guards_after'] = guarded_files()
    write()
    print(json.dumps({k:r.get(k) for k in ('status','errors','rotation_degrees','extra_translation_cm',
                                          'early_gate_passed','after_contact','checks','inputs_unchanged')}))
