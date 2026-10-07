"""Fresh read-only thumb comparison; optional retained failed-grasp views."""
import sys
from pathlib import Path
failed='--failure' in sys.argv
p=Path(__file__).resolve().parents[1]/'GermanNPCTriggerLowerV7/review.py'
source=p.read_text(encoding='utf-8-sig')
changes={
    "BASE=STORE/'Evidence/GermanNPCTriggerLowerV7';OUT=BASE/'review_v1'":
    "BASE=STORE/'Evidence/GermanNPCThumbCurlV10';OUT=BASE/"+repr('failure_views_v1' if failed else 'review_v1'),
    "FIT=BASE/'stock_down_v2/result.json'":
    "FIT=BASE/"+repr(('distal_reuse_v1' if failed else 'surface_limit_v2')+'/result.json'),
    "assert fit['status']=='failed_preserved' and fit['rotation_deg']==8":
    "assert fit['status']=="+repr('failed_preserved' if failed else 'surface_limited_distal_grasp_requires_actual_views'),
    "for p in (FIT,DATA,Path(__file__))":
    "for p in (FIT,DATA,Path(__file__),ROOT/'Tools/Integration/GermanNPCTriggerLowerV7/review.py')",
    "leftids=[j for j,n in enumerate(names) if n.startswith(('upperarm_','lowerarm_','hand_','thumb_','index_','middle_','ring_','pinky_')) and n.endswith('_l')]":
    "leftids=[names.index(n) for n in fit['changed_local_rotation_deg']]",
    "rightids=[j for j,n in enumerate(names) if n.startswith(('hand_','thumb_','index_','middle_','ring_','pinky_')) and n.endswith('_r')]":
    "rightids=[j for j,n in enumerate(names) if n.startswith(('hand_','thumb_','index_','middle_','ring_','pinky_')) and n not in fit['changed_local_rotation_deg']]",
    "right_protected_bones=[n for n in names if n.endswith('_r')]":
    "right_protected_bones=[n for n in names if n not in fit['changed_local_rotation_deg']]",
    "true_zero_left_influence_skin_cm": "true_zero_changed_thumb_influence_skin_cm",
    "right_hand_weight": "unchanged_hand_bone_weight",
    "left_arm_weight": "changed_thumb_weight",
    "assert len(r['shared_hand_vertices'])==6":
    "r['mixed_hand_vertex_count']=len(r['shared_hand_vertices'])",
    "six_shared_vertices_are_not_fixed": "mixed_weight_vertices_are_not_fixed",
    "r['status']='retained_directional_comparison_views_not_full_contact_acceptance'":
    "r['status']="+repr('retained_failed_grasp_views_only' if failed else 'distal_thumb_views_local_improvement_not_full_contact_acceptance'),
}
for a,b in changes.items():
    expected=2 if a=='true_zero_left_influence_skin_cm' else 1
    assert source.count(a)==expected,(a,source.count(a));source=source.replace(a,b)
needle='    # Gray/orange display only; exact full source topology and winding parity.'
extra="""    saved=np.load(FIT.parent/'diagnostic_geometry.npz')
    r['fresh_skin_before_cm']=float(np.linalg.norm(p0-saved['before_skin'],axis=1).max())
    r['fresh_skin_after_cm']=float(np.linalg.norm(p1-saved['skin'],axis=1).max())
    r['fresh_gun_before_cm']=float(np.linalg.norm(g0-saved['gun_before_cm'],axis=1).max())
    r['fresh_gun_after_cm']=float(np.linalg.norm(g1-saved['gun_after_cm'],axis=1).max())
    assert max(r[k] for k in ('fresh_skin_before_cm','fresh_skin_after_cm','fresh_gun_before_cm','fresh_gun_after_cm'))<.01
    r['gun_exact']=fit['before_gun_world']==fit['after_gun_world']
    assert r['gun_exact']
"""+needle
assert source.count(needle)==1;source=source.replace(needle,extra)
if failed:
    start=source.index("        for name,offset,width,target in [")
    end=source.index(":\n            center=",start)
    source=source[:start]+"        for name,offset,width,target in [('right',(0,-.4,.12),.25,thumbcenter),('context',(0,-2,.25),1.25,handcenter)]"+source[end:]
exec(compile(source,str(Path(__file__)),'exec'))
