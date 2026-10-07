"""ONE authorized +2deg from V8; reviewed V8 checks reused, no old fit rerun."""
from pathlib import Path

p = Path(__file__).resolve().parents[1] / 'GermanNPCScreenRotateV8/fit.py'
source = p.read_text(encoding='utf-8-sig')
replacements = {
    "BASE=STORE/'Evidence/GermanNPCScreenRotateV8';OUT=BASE/'screen_turn_v1'":
    "BASE=STORE/'Evidence/GermanNPCScreenRotateV9';OUT=BASE/'extra_two_v1'",
    "PREV=STORE/'Evidence/GermanNPCTriggerLowerV7/stock_down_v2/result.json'":
    "PREV=STORE/'Evidence/GermanNPCScreenRotateV8/screen_turn_v1/result.json'",
    "GLB,MARK,Path(__file__),ROOT/":
    "GLB,MARK,Path(__file__),ROOT/'Tools/Integration/GermanNPCScreenRotateV8/fit.py',ROOT/",
    "assert old['rotation_deg']==8 and not checked['errors']":
    "assert old['rotation_deg']==4 and not old['errors'] and not checked['errors']",
    "assert checked['status']=='retained_directional_comparison_views_not_full_contact_acceptance'":
    "assert checked['status']=='screen_turn_views_not_full_contact_acceptance'",
    "v7_reproduction_": "v8_reproduction_",
    "r.update(rotation_deg=4,axis_world=axis.tolist()":
    "r.update(rotation_deg=2,cumulative_rotation_deg=6,axis_world=axis.tolist()",
    "r['status']='toward_camera_directional_comparison_requires_human_review'":
    "r['status']='extra_two_degree_comparison_requires_human_review'",
}
for a, b in replacements.items():
    expected = 4 if a == 'v7_reproduction_' else 1
    assert source.count(a) == expected, (a, source.count(a))
    source = source.replace(a, b)

# Use actual V8 landmarks/axis unchanged. Do not rerun its screenshot raycast.
start = source.index('    # The reverse camera stayed centered')
end = source.index('    rot=np.array(Quaternion', start)
source = source[:start] + """    toward=np.array([0.,40.,12.]);toward/=np.linalg.norm(toward)
    u,v=old['screenshot_normalized_uv'];face=old['inferred_marked_stock_face']
    marked=np.array(old['marked_stock_world_after_cm'],float)
    pivot=transform(np.array([old['trigger_pivot_gun_cm']]),g0)[0]
    axis=np.array(old['axis_world'],float)
    assert abs(np.linalg.norm(axis)-1)<1e-10
    angle=math.radians(2)
    r['recorded_v8_axis_reused_exactly']=True
    r['independent_translation_or_scale']=False
""" + source[end:]

needle = '    write(OUT/\'result.json\',r)\n    assert r[\'trigger_pivot_error_cm\']'
extra = """    def actual_degrees(matrix):
        u,s,vh=np.linalg.svd(matrix[:3,:3]);rot=u@vh
        return math.degrees(math.acos(float(np.clip((np.trace(rot)-1)/2,-1,1))))
    r['measured_extra_rotation_deg']=actual_degrees(change)
    r['measured_cumulative_from_v7_deg']=actual_degrees(g1@np.linalg.inv(mat(old['before_gun_world'])))
    r['marked_cumulative_toward_camera_cm']=float((marked1-np.array(old['marked_stock_world_before_cm']))@toward)
    r['axis_difference_from_v8']=float(np.max(abs(axis-np.array(old['axis_world']))))
    assert abs(r['measured_extra_rotation_deg']-2)<.01
    assert abs(r['measured_cumulative_from_v7_deg']-6)<.01
    assert r['axis_difference_from_v8']==0
""" + needle
assert source.count(needle) == 1
source = source.replace(needle, extra)
exec(compile(source, str(Path(__file__)), 'exec'))
