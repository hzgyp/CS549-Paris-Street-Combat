# Added to the observer before callback registration, not a separately executed UE script.
def navigation_objects(w):
    ns=[n for n in unreal.ObjectIterator(unreal.NavigationSystemV1) if 'Default__' not in n.get_path_name() and n.get_outer()==w]
    aa=list(unreal.GameplayStatics.get_all_actors_of_class(w,unreal.Actor))
    ms=[a for a in aa if isinstance(a,unreal.RecastNavMesh)]
    vs=[a for a in aa if isinstance(a,unreal.NavMeshBoundsVolume)]
    assert len(ns)==len(ms)==len(vs)==1,(len(ns),len(ms),len(vs))
    return ns[0],ms[0],vs[0]

def navigation_info(w,scope):
    n,m,v=navigation_objects(w);o,e=v.get_actor_bounds(False)
    props={k:prop(m,k) for k in ('agent_radius','agent_height','agent_max_slope','tile_size_uu')}
    assert props=={'agent_radius':34.0,'agent_height':193.0,'agent_max_slope':45.0,'tile_size_uu':1000.0},props
    mesh=json.loads(unreal.ParisMapSurveyLibrary.export_navmesh(m));assert not mesh.get('error'),mesh
    name=scope+('_pie' if w==editor.get_game_world() else '_editor')+'_navmesh.json'
    (OUT/name).write_text(json.dumps(mesh)+'\n')
    return {'scope':scope,'instance':n.get_path_name(),'nav_data':m.get_path_name(),'properties':props,
        'bounds_center_cm':xyz(o),'bounds_extent_cm':xyz(e),
        'export_file':name,'export_sha256':digest(OUT/name),'polygon_count':len(mesh['polygons']),
        'active_tiles':mesh['active_tiles'],'exported_tiles':mesh['exported_tiles'],
        'build_state':json.loads(unreal.ParisMapSurveyLibrary.navigation_build_state(n))}

def expand_navigation():
    global nav,nav_data,expansion_started
    w=editor.get_editor_world();nav,nav_data,vol=navigation_objects(w)
    report['before_expansion_navigation']=navigation_info(w,'saved')
    # Disable only formal disposable bodies before generation, without touching source packages.
    lookup={a.get_actor_label():a for a in actors.get_all_level_actors()}
    report['editor_collision_restore']=[]
    for name in ('PC_City_Player',*LABELS):
        a=lookup[name];original=bool(a.get_actor_enable_collision())
        report['editor_collision_restore'].append({'label':name,'original':original})
        a.set_actor_enable_collision(False);assert not a.get_actor_enable_collision()
    inv=json.loads(inventory_path.read_text())['collision_bounds_cm']
    lo=[inv['min'][i]-(100 if i<2 else 193) for i in range(3)]
    hi=[inv['max'][i]+(100 if i<2 else 193) for i in range(3)]
    center=[(a+b)/2 for a,b in zip(lo,hi)];extent=[(b-a)/2 for a,b in zip(lo,hi)]
    vol.set_actor_location(unreal.Vector(*center),False,False)
    vol.set_actor_scale3d(unreal.Vector(*(v/100 for v in extent)))
    nav.on_navigation_bounds_updated(vol)
    o,e=vol.get_actor_bounds(False)
    assert max(abs(a-b) for a,b in zip(xyz(o),center))<.1 and max(abs(a-b) for a,b in zip(xyz(e),extent))<.1
    report['temporary_bounds_cm']={'min':lo,'max':hi}
    expansion_started=time.monotonic()

def restore_editor_collision():
    lookup={a.get_actor_label():a for a in actors.get_all_level_actors()}
    for row in report['editor_collision_restore']:
        a=lookup[row['label']];a.set_actor_enable_collision(row['original'])
        row['restored']=bool(a.get_actor_enable_collision());assert row['restored']==row['original']
    report['fixture_addendum_sha256']=digest(ROOT/'Docs/Development/MissionLoopV1/UE_STANDARD_NAV_FIXTURE_ADDENDUM_20261007.md')

def projection(point):
    # Live receiver avoids the known Python class/CDO world-context ensure.
    answer=nav.call_method('K2_ProjectPointToNavigation',args=(world,unreal.Vector(*point),nav_data,None,unreal.Vector(0,0,0)))
    if isinstance(answer,tuple):
        if any(isinstance(v,bool) and not v for v in answer):return None
        answer=next((v for v in answer if isinstance(v,unreal.Vector)),None)
    assert answer is None or isinstance(answer,unreal.Vector),repr(answer)
    return xyz(answer) if answer is not None else None

def standard_request(c,actual_feet):
    before=control(c);assert before['status_code']==0,'Do not replace a live request'
    source_project=projection(actual_feet);goal_project=projection(bank['hub']['feet_cm'])
    code=c.move_to_location(unreal.Vector(*bank['hub']['feet_cm']),30.0,False,True,True,False,None,False)
    after=control(c)
    result={'api':'AAIController.MoveToLocation','return_code':str(code),'started':code==unreal.PathFollowingRequestResult.REQUEST_SUCCESSFUL,
        'controller':c.get_path_name(),'request_id':after['request_id'],'goal_cm':bank['hub']['feet_cm'],
        'actual_source_feet_cm':actual_feet,'source_projection_cm':source_project,'goal_projection_cm':goal_project,
        'use_pathfinding':True,'project_destination':True,'allow_partial_paths':False,'stop_on_overlap':False,
        'acceptance_cm':30,'before_controller':before,'after_controller':after,'path_cm':[],'path_length_cm':0}
    if result['started']:
        route=unreal.AIHelperLibrary.get_current_path(c);assert route and route.is_valid() and not route.is_partial(),'Standard request supplied no complete current path'
        points=[xyz(p) for p in prop(route,'path_points')]
        assert len(points)>=2 and after['request_id']>=0 and after['status_code']!=0
        result['path_cm']=points;result['path_length_cm']=sum(math.dist(a,b) for a,b in zip(points,points[1:]))
        result['partial']=bool(route.is_partial());result['native_path_end_cm']=points[-1]
    else:
        assert code==unreal.PathFollowingRequestResult.FAILED,('Unexpected already-at-goal',result)
        result['rejection']='standard_controller_failed_request'
    return result
