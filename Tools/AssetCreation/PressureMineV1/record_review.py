"""Freeze private authored asset and reviewed stage evidence, never vendor pixels."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[3]
asset=ROOT/'Assets/LocalWorking/Experiments/PressureMine/20261011-v1'
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
review=ROOT/'tmp/g1-tactical-equipment-20261010/checks/mine_visual_v2'
assert json.loads((review/'RESULT.json').read_text('utf-8-sig'))['status'].startswith('pass')
out=asset/'ASSET_REVIEW.json';assert not out.exists()
files=[]
for folder in ['geometry_v2','finish_v2','verify_v2']:
    for p in sorted((asset/folder).iterdir()):
        if p.is_file():files.append(dict(path=p.relative_to(ROOT).as_posix(),size_bytes=p.stat().st_size,sha256=sha(p)))
obj=dict(status='local_candidate_art_review_pass_manual_selection_pending',blender='5.2.2 LTS',triangles=10809,
    exterior='Fictional WWII-style 28cm pressure disc, rolled shell/plate seams, sealed centre, six bolts, supported carry loop; no historical model or internals claim',
    stage_review='Geometry v2, PBR finish v2 and fresh GLB import: matching top/side/rear/three-quarter reviewed. No checker/default gray, smooth outline, attached handle and readable stencil. UE v1 darkness rejected, v2 exact same baked maps with corrected native triangle winding reviewed.',
    texture='1024 albedo sRGB; ORM and normal linear; same mesh export/UV/material as fresh GLB',
    rights='Original project procedural geometry/paint/stencil/bake. Museum/inert commercial-prop images observed only; no reference pixels embedded or redistributed.',
    reference_notes='Tools/AssetCreation/PressureMineV1/reference_notes.md',
    runtime_review='tmp/g1-tactical-equipment-20261010/checks/mine_visual_v2',files=files,
    scope='Authoring/export/render validation only. User art/play approval and publication remain pending.')
out.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
review_obj=dict(status='pass',scope='Actual UE normal90deg/detail40deg fixture pictures, held NPCs; not user view or natural play acceptance',
    observations='Olive paint and stencil visible; rounded disc/stepped plate/seam/handle present, rests on original street; original hands/rifle/HUD present. Visible position/range marker; no added debug highlight.',
    files=[dict(name=p.name,size_bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(review.glob('*.png'))])
(review/'VISUAL_REVIEW.json').write_text(json.dumps(review_obj,indent=2)+'\n',encoding='utf-8')
print('Private stage/runtime visual evidence frozen')
