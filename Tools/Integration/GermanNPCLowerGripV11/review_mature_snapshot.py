"""Fresh read-only full-skin review, no fitting or native asset authoring."""
import sys
from pathlib import Path
failed='--source-failure' in sys.argv
p=Path(__file__).resolve().parents[1]/'GermanNPCTriggerLowerV7/review.py'
source=p.read_text(encoding='utf-8-sig')
changes={
 "BASE=STORE/'Evidence/GermanNPCTriggerLowerV7';OUT=BASE/'review_v1'":
 "BASE=STORE/'Evidence/GermanNPCLowerGripV11';OUT=BASE/"+repr('failure_views_v1' if failed else 'review_v1'),
 "FIT=BASE/'stock_down_v2/result.json'":
 "FIT=BASE/"+repr(('mature_reuse_v1' if failed else 'nearest_surface_v3')+'/result.json'),
 "assert fit['status']=='failed_preserved' and fit['rotation_deg']==8":
 "assert fit['status']=="+repr('failed_preserved' if failed else 'stock_section_lower_grasp_requires_actual_views'),
 "for p in (FIT,DATA,Path(__file__))":
 "for p in (FIT,DATA,Path(__file__),ROOT/'Tools/Integration/GermanNPCTriggerLowerV7/review.py')",
 "leftids=[j for j,n in enumerate(names) if n.startswith(('upperarm_','lowerarm_','hand_','thumb_','index_','middle_','ring_','pinky_')) and n.endswith('_l')]":
 "leftids=[names.index(n) for n in fit['changed_local_rotation_deg']]",
 "rightids=[j for j,n in enumerate(names) if n.startswith(('hand_','thumb_','index_','middle_','ring_','pinky_')) and n.endswith('_r')]":
 "rightids=[j for j,n in enumerate(names) if n.startswith(('hand_','thumb_','index_','middle_','ring_','pinky_')) and n not in fit['changed_local_rotation_deg']]",
 "right_protected_bones=[n for n in names if n.endswith('_r')]":
 "right_protected_bones=[n for n in names if n not in fit['changed_local_rotation_deg']]",
 "true_zero_left_influence_skin_cm":"true_zero_changed_influence_skin_cm",
 "right_hand_weight":"unchanged_hand_bone_weight",
 "left_arm_weight":"changed_lower_digit_weight",
 "assert len(r['shared_hand_vertices'])==6":"r['mixed_hand_vertex_count']=len(r['shared_hand_vertices'])",
 "six_shared_vertices_are_not_fixed":"mixed_weight_vertices_are_not_fixed",
 "r['status']='retained_directional_comparison_views_not_full_contact_acceptance'":
 "r['status']="+repr('retained_failed_source_grasp_views_only' if failed else 'lower_grasp_static_views_require_human_review'),
}
for a,b in changes.items():
    assert source.count(a)==(2 if a=='true_zero_left_influence_skin_cm' else 1),(a,source.count(a))
    source=source.replace(a,b)
needle='    # Gray/orange display only; exact full source topology and winding parity.'
extra="""    saved=np.load(FIT.parent/'diagnostic_geometry.npz')
    for label,actual,key in (('skin_before',p0,'before_skin'),('skin_after',p1,'skin'),('gun_before',g0,'gun_before_cm'),('gun_after',g1,'gun_after_cm')):
        r['fresh_'+label+'_cm']=float(np.linalg.norm(actual-saved[key],axis=1).max())
        assert r['fresh_'+label+'_cm']<.01
    r['gun_exact']=fit['before_gun_world']==fit['after_gun_world'];assert r['gun_exact']
"""+needle
assert source.count(needle)==1;source=source.replace(needle,extra)
needle="    scene=bpy.context.scene;scene.render.engine="
extra="""    lower_materials=[material('Middle diagnostic',(.85,.68,.32)),material('Ring diagnostic',(.60,.42,.65)),material('Little diagnostic',(.30,.68,.45))]
    for m in lower_materials:body.data.materials.append(m)
    masks=[w[:,[names.index(digit+'_'+i+'_r') for i in ('01','02','03')]].sum(1)>.5 for digit in ('middle','ring','pinky')]
    for i,poly in enumerate(body.data.polygons):
        for j,mask in enumerate(masks):
            if np.all(mask[tri[i]]):poly.material_index=4+j;break
"""+needle
assert source.count(needle)==1;source=source.replace(needle,extra)
needle="    handcenter=(origin+poses['before']['hand_l'][:3,3])/2"
source=source.replace(needle,needle+"\n    lowercenter=np.mean([poses['before'][digit+'_'+i+'_r'][:3,3] for digit in ('middle','ring','pinky') for i in ('01','03')],axis=0)",1)
start=source.index('        for name,offset,width,target in [')
end=source.index(':\n            center=',start)
source=source[:start]+"        for name,offset,width,target in [('reverse',(0,.4,.12),.29,lowercenter),('right',(0,-.4,.12),.29,lowercenter),('top',(0,0,.5),.32,lowercenter),('underside',(0,0,-.5),.32,lowercenter),('oblique',(0,.4,-.1),.30,lowercenter),('context',(0,-2,.25),1.25,handcenter)]"+source[end:]
exec(compile(source,str(Path(__file__)),'exec'))
