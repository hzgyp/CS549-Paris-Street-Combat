"""One registered action, read-only native load and joint mesh/action export."""
import unreal,json,os,hashlib,traceback
from pathlib import Path
job=json.loads(Path(os.environ['AW_ANIMATION_REQUEST']).read_text(encoding='utf8'));out=Path(job['output']);report={'status':'running','errors':[],'packages_saved':False}
try:
 for f in job['inputs']:
  assert hashlib.sha256(Path(f['file']).read_bytes()).hexdigest()==f['sha256'],'SOURCE_CHANGED'
 anim=unreal.load_asset(job['clip_path']);assert isinstance(anim,unreal.AnimSequence),'SOURCE_NOT_ANIMATION'
 skeleton=anim.get_editor_property('skeleton');assert skeleton and anim.get_play_length()>0,'SOURCE_SKELETON_OR_DURATION_MISSING'
 chosen=None
 for path in job['meshes']:
  mesh=unreal.load_asset(path)
  if mesh and mesh.get_editor_property('skeleton')==skeleton:chosen=mesh;break
 assert chosen,'NO_COMPATIBLE_PACKAGE_MESH'
 anim.set_preview_skeletal_mesh(chosen)
 options=unreal.FbxExportOption()
 for k,v in {'ascii':False,'level_of_detail':False,'collision':False,'export_morph_targets':True,'export_preview_mesh':True,'bake_material_inputs':unreal.FbxMaterialBakeMode.DISABLED}.items():options.set_editor_property(k,v)
 file=out/'source-action.fbx';task=unreal.AssetExportTask();task.object=anim;task.filename=str(file);task.automated=True;task.prompt=False;task.replace_identical=False;task.options=options
 assert unreal.Exporter.run_asset_export_task(task) and file.is_file() and file.stat().st_size>10000,'EXPORT_FAILED'
 for f in job['inputs']:assert hashlib.sha256(Path(f['file']).read_bytes()).hexdigest()==f['sha256'],'SOURCE_CHANGED'
 report.update(status='exported',fbx_sha256=hashlib.sha256(file.read_bytes()).hexdigest(),mesh=chosen.get_path_name(),animation=anim.get_path_name(),skeleton=skeleton.get_path_name(),native_duration=anim.get_play_length(),engine=unreal.SystemLibrary.get_engine_version())
except Exception as exc:report.update(status='failed',code=str(exc) if isinstance(exc,AssertionError) else 'SOURCE_LOAD_FAILED',errors=[traceback.format_exc()])
(out/'native-result.json').write_text(json.dumps(report,indent=2))
