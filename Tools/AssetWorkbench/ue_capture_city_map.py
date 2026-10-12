"""Read the original city in an engine-only preview project; never save packages."""
import unreal,json,traceback,hashlib,math,os
from pathlib import Path

OUT=Path(os.environ['CITY_CAPTURE_OUT']) if os.environ.get('CITY_CAPTURE_OUT') else Path(unreal.Paths.project_dir()).resolve().parent/'capture-v1'
OUT.mkdir(exist_ok=True)
report={'status':'running','map':'/Game/WW2City/Maps/LV_Paris_WW2','engine':unreal.SystemLibrary.get_engine_version(),'packages_saved':False,'captures':[]}
def save():(OUT/'result.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
save()
try:
    world=unreal.EditorLoadingAndSavingUtils.load_map(report['map'])
    assert world,'City world not loaded'
    unreal.AutomationLibrary.finish_loading_before_screenshot()
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    all_actors=actors.get_all_level_actors()
    bounds=[]
    for a in all_actors:
        meshes=a.get_components_by_class(unreal.StaticMeshComponent)
        if not meshes or any(s in a.get_actor_label().lower() for s in ('sky','cloud','fog')):continue
        center,extent=a.get_actor_bounds(False)
        if max(extent.x,extent.y)>200000 or max(extent.x,extent.y)<1:continue
        bounds.append(([center.x,center.y,center.z],[extent.x,extent.y,extent.z]))
    assert len(bounds)>300,('Incomplete city geometry',len(bounds))
    low=[min(c[i]-e[i] for c,e in bounds) for i in range(3)]
    high=[max(c[i]+e[i] for c,e in bounds) for i in range(3)]
    center=[(low[i]+high[i])/2 for i in range(3)]
    span=max(high[0]-low[0],high[1]-low[1])
    report.update(actor_count=len(all_actors),mesh_actor_count=len(bounds),bounds_cm={'min':low,'max':high},loaded_levels=[x.get_path_name() for x in unreal.EditorLevelUtils.get_levels(world)])
    save()
    camera=actors.spawn_actor_from_class(unreal.SceneCapture2D,unreal.Vector(0,0,10000))
    camera.set_actor_label('AssetWorkbenchReadonlyCityCapture')
    cap=camera.get_component_by_class(unreal.SceneCaptureComponent2D)
    cap.set_editor_property('capture_source',unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
    cap.set_editor_property('capture_every_frame',False);cap.set_editor_property('capture_on_movement',False)
    cap.set_editor_property('fov_angle',65)
    target=unreal.RenderingLibrary.create_render_target2d(world,1600,1000,unreal.TextureRenderTargetFormat.RTF_RGBA8,unreal.LinearColor(.05,.05,.05,1),False)
    cap.set_editor_property('texture_target',target)
    x,y,z=center
    poses=[('city-overview',(x+span*.62,y-span*.68,high[2]+span*.7),(x,y,z)),
           ('city-overhead',(x,y,high[2]+span*.95),(x,y,low[2])),
           ('city-bridge',(-4500,-16000,9000),(-4000,1000,300)),
           ('city-streets',(-12000,11000,4200),(-3000,6500,300))]
    for name,pos,aim in poses:
        camera.set_actor_location(unreal.Vector(*pos),False,False)
        camera.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(unreal.Vector(*pos),unreal.Vector(*aim)),False)
        unreal.AutomationLibrary.finish_loading_before_screenshot()
        for _ in range(5):cap.capture_scene()
        file=OUT/(name+'.png')
        unreal.RenderingLibrary.export_render_target(world,target,str(OUT),file.name)
        assert file.is_file() and file.stat().st_size>1000
        report['captures'].append({'file':file.name,'camera_cm':pos,'aim_cm':aim,'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'size_bytes':file.stat().st_size})
        save()
    actors.destroy_actor(camera)
    report['status']='captured_pending_visual_review'
except Exception:
    report['status']='failed';report['error']=traceback.format_exc()
save()
