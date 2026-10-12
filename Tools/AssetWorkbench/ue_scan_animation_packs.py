"""Enumerate native AnimSequence records without loading or saving packages."""
import unreal,json
from pathlib import Path
batch=Path(unreal.Paths.project_dir()).resolve().parent
registry=unreal.AssetRegistryHelpers.get_asset_registry()
registry.scan_paths_synchronous(['/Game'],True)
records=registry.get_assets_by_path('/Game',recursive=True)
rows=[]
for job in json.loads((batch/'jobs.json').read_text()):
 allowed=set(job['paths']);own=[a for a in records if str(a.package_name) in allowed]
 rows.append({'id':job['id'],'project':str(batch/'Project/AssetCoverLab.uproject'),'clips':[{'path':str(a.package_name)+'.'+str(a.asset_name),'name':str(a.asset_name)} for a in own if str(a.asset_class_path.asset_name)=='AnimSequence'],'meshes':[str(a.package_name)+'.'+str(a.asset_name) for a in own if str(a.asset_class_path.asset_name)=='SkeletalMesh']})
(batch/'animation-directory-v1.json').write_text(json.dumps(rows,indent=2))
