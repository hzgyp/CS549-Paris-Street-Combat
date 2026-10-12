"""Read existing equipment and export a private geometry/texture derivative only."""
import unreal,json,traceback,hashlib
from pathlib import Path
ROOT=Path(r'D:\0.Rutgers\CS549\Project-New')
OUT=ROOT/'tmp/g1-grenade-models-20261011/asset_lookup/equipment_v1'
OUT.mkdir(parents=True,exist_ok=False)
report={'status':'inspecting','native_packages_saved':False,'materials':[]}
try:
    path='/Game/USParatrooper/Meshes/SK_WWII_US_Paratrooper_equipment'
    mesh=unreal.load_asset(path);assert mesh
    report['mesh']=path
    report['materials']=[dict(index=i,slot=str(m.material_slot_name),material=m.material_interface.get_path_name() if m.material_interface else None) for i,m in enumerate(mesh.get_editor_property('materials'))]
    options=unreal.GLTFExportOptions()
    options.set_editor_property('bake_material_inputs',unreal.GLTFMaterialBakeMode.DISABLED)
    options.set_editor_property('texture_image_format',unreal.GLTFTextureImageFormat.NONE)
    options.set_editor_property('export_uniform_scale',.01)
    result=unreal.GLTFExporter.export_to_gltf(mesh,str(OUT/'Equipment.glb'),options,set())
    report['export_result']=str(result)
    assert (OUT/'Equipment.glb').is_file()
    report['textures']=[]
    for suffix in ['D','N','ORM']:
        asset='/Game/USParatrooper/Textures/FragGrenade/T_MKII_FRAG_'+suffix
        texture=unreal.load_asset(asset);assert texture
        task=unreal.AssetExportTask();task.object=texture;task.filename=str(OUT/('T_MKII_FRAG_'+suffix+'.tga'));task.automated=True;task.prompt=False;task.replace_identical=False;task.exporter=unreal.TextureExporterTGA()
        assert unreal.Exporter.run_asset_export_task(task),suffix
        report['textures'].append(dict(asset=asset,file=task.filename))
    report['status']='exported_pending_geometry_inspection'
except Exception:report['status']='failed';report['error']=traceback.format_exc()
report['files']=[dict(path=p.name,bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in OUT.iterdir() if p.is_file()]
(OUT/'REPORT.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('GRENADE_ASSET_READONLY_REPORT',json.dumps(report))
