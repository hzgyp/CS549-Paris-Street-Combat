"""Fresh read of diagnostic-only blend, not an exported/runtime rig acceptance."""
import bpy,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
BASE=STORE/'Evidence/WeaponTriggerAlignmentV2/index_pose_v1';OUT=STORE/'Evidence/WeaponTriggerAlignmentV2/fresh_check_v1'
assert not OUT.exists();OUT.mkdir();(OUT/'source.py').write_bytes(Path(__file__).read_bytes())
file=BASE/'ExistingIndexPoseContact.blend';before=hashlib.sha256(file.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(file));objects=[o for o in bpy.data.objects if o.type=='MESH' and not o.hide_render]
assert len(objects)==3,[o.name for o in objects]
assert any('Right hand existing_index_pose_v3'==o.name for o in objects)
assert any('Left hand unchanged'==o.name for o in objects)
assert any('Frozen V2 M1'==o.name for o in objects)
armatures=[o for o in bpy.data.objects if o.type=='ARMATURE'];assert len(armatures)==1 and len(armatures[0].data.bones)==72
assert hashlib.sha256(file.read_bytes()).hexdigest()==before
source=json.loads((BASE/'result.json').read_text());assert source['inputs_unchanged'] and not source['errors'] and source['stock_guard_gate_passed']
r={'status':'fresh_diagnostic_blend_read_checked_not_runtime_rig_export','blend_unchanged':True,'blend_sha256':before,
 'visible_meshes':[{'name':o.name,'vertices':len(o.data.vertices),'triangles':len(o.data.polygons)} for o in objects],
 'source_armature_bones':72,'limits':'Visible meshes are offline skin evaluations, NOT an authored playable/native rig/animation.'}
(OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
