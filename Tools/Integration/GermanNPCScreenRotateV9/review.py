"""Fresh exact V9 diagnostic rendering, no previous fitting launcher executed."""
from pathlib import Path

p = Path(__file__).resolve().parents[1] / 'GermanNPCTriggerLowerV7/review.py'
source = p.read_text(encoding='utf-8-sig')
replacements = {
    "BASE=STORE/'Evidence/GermanNPCTriggerLowerV7'":
    "BASE=STORE/'Evidence/GermanNPCScreenRotateV9'",
    "FIT=BASE/'stock_down_v2/result.json'": "FIT=BASE/'extra_two_v1/result.json'",
    "assert fit['status']=='failed_preserved' and fit['rotation_deg']==8":
    "assert fit['status']=='extra_two_degree_comparison_requires_human_review' and fit['rotation_deg']==2 and fit['cumulative_rotation_deg']==6",
    "for p in (FIT,DATA,Path(__file__))":
    "for p in (FIT,DATA,Path(__file__),ROOT/'Tools/Integration/GermanNPCTriggerLowerV7/review.py')",
    "r['status']='retained_directional_comparison_views_not_full_contact_acceptance'":
    "r['status']='extra_two_degree_views_not_full_contact_acceptance'",
}
for a, b in replacements.items():
    assert source.count(a) == 1, (a, source.count(a))
    source = source.replace(a, b)
needle = '    # Gray/orange display only; exact full source topology and winding parity.'
extra = """    saved=np.load(FIT.parent/'diagnostic_geometry.npz')
    r['fresh_skin_before_cm']=float(np.linalg.norm(p0-saved['before_skin'],axis=1).max())
    r['fresh_skin_after_cm']=float(np.linalg.norm(p1-saved['skin'],axis=1).max())
    r['fresh_gun_before_cm']=float(np.linalg.norm(g0-saved['gun_before_cm'],axis=1).max())
    r['fresh_gun_after_cm']=float(np.linalg.norm(g1-saved['gun_after_cm'],axis=1).max())
    assert max(r[k] for k in ('fresh_skin_before_cm','fresh_skin_after_cm','fresh_gun_before_cm','fresh_gun_after_cm'))<.01
""" + needle
assert source.count(needle) == 1
source = source.replace(needle, extra)
exec(compile(source, str(Path(__file__)), 'exec'))
