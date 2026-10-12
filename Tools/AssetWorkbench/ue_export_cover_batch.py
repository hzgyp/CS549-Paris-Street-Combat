"""Read exact package meshes/clips and export private animated FBX for clean cover renders."""
import unreal,json,traceback,hashlib,gc,time
from pathlib import Path
batch=Path(unreal.Paths.project_dir()).resolve().parent
registry=unreal.AssetRegistryHelpers.get_asset_registry();registry.scan_paths_synchronous(['/Game'],True)
all_records=registry.get_assets_by_path('/Game',recursive=True)
for job in json.loads((batch/'jobs.json').read_text()):
 out=Path(job['directory'])/'export-v3';out.mkdir(exist_ok=True);receipt=out/'result.json'
 if receipt.exists():continue
 report={'id':job['id'],'engine':unreal.SystemLibrary.get_engine_version(),'status':'running','captures':[],'errors':[],'packages_saved':False,'source_sha256':job['source_sha256']}
 def save():receipt.write_text(json.dumps(report,indent=2))
 save()
 try:
  allowed=set(job['paths']);records=[a for a in all_records if str(a.package_name) in allowed]
  meshes=[a for a in records if str(a.asset_class_path.asset_name)=='SkeletalMesh'];clips=[a for a in records if str(a.asset_class_path.asset_name)=='AnimSequence']
  report['mesh_candidates']=[str(a.package_name) for a in meshes];report['clip_count']=len(clips);save()
  def rank(a):
   n=str(a.asset_name).lower();return (any(x in n for x in ('additive','aimoffset','tpose','reference','ref_pose')),0 if any(x in n for x in ('attack','walk','run','idle')) else 1,n)
  chosen=None
  for a in sorted(clips,key=rank)[:80]:
   anim=a.get_asset()
   if not anim or anim.get_play_length()<=0:continue
   skeleton=anim.get_editor_property('skeleton')
   if not skeleton:continue
   for m in sorted(meshes,key=lambda x:('mannequin' not in str(x.asset_name).lower(),str(x.asset_name))):
    mesh=m.get_asset()
    if mesh and mesh.get_editor_property('skeleton')==skeleton:chosen=(mesh,anim,skeleton);break
   if chosen:break
  assert chosen,'No own mesh and matching nonempty clip'
  mesh,anim,skeleton=chosen;anim.set_preview_skeletal_mesh(mesh)
  report.update(mesh=mesh.get_path_name(),animation=anim.get_path_name(),skeleton=skeleton.get_path_name(),duration=anim.get_play_length(),neutral_material=True)
  options=unreal.FbxExportOption();options.set_editor_property('ascii',False);options.set_editor_property('level_of_detail',False);options.set_editor_property('collision',False);options.set_editor_property('export_morph_targets',True);options.set_editor_property('export_preview_mesh',False);options.set_editor_property('bake_material_inputs',unreal.FbxMaterialBakeMode.DISABLED)
  file=out/'source-action.fbx';task=unreal.AssetExportTask();task.object=anim;task.filename=str(file);task.automated=True;task.prompt=False;task.replace_identical=False;task.options=options
  assert unreal.Exporter.run_asset_export_task(task) and file.is_file() and file.stat().st_size>10000,list(task.errors)
  model=out/'source-mesh.fbx';task.object=mesh;task.filename=str(model)
  assert unreal.Exporter.run_asset_export_task(task) and model.is_file() and model.stat().st_size>10000,list(task.errors)
  report.update(status='exported',fbx_sha256=hashlib.sha256(file.read_bytes()).hexdigest(),fbx_bytes=file.stat().st_size,mesh_fbx_sha256=hashlib.sha256(model.read_bytes()).hexdigest())
 except Exception:report['status']='failed';report['errors'].append(traceback.format_exc())
 save();unreal.log('COVER_EXPORT_PROGRESS '+job['id']+' '+report['status']);gc.collect()
