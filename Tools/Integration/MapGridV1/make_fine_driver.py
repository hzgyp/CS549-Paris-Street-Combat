"""Build a distinct static-only driver from the admitted isolation implementation."""
from pathlib import Path

HERE=Path(__file__).parent
def build():
    source=(HERE/'ue_grid_sample.py').read_text(encoding='utf-8')
    def replace(old,new):
        nonlocal source
        assert source.count(old)==1,old[:100]
        source=source.replace(old,new)
    replace("STAGE=os.environ['CS549_GRID_STAGE'];assert STAGE in ('Early','Full')", "STAGE=os.environ['CS549_GRID_STAGE'];assert STAGE in ('Early','Full','Expanded')\nCOARSE=STORE_PLACEHOLDER")
    source=source.replace('COARSE=STORE_PLACEHOLDER','COARSE=ROOT/\'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/MapGridV1/full_v1_20261007\'')
    replace("MAP_GRID_IMPLEMENTATION_20261007.md", "FINE_GRID_IMPLEMENTATION_20261007.md")
    replace("grid=grid_spec(base_nav);", "grid=grid_spec(base_nav);grid.update(cell_cm=25.0,columns=4032,rows=4032);")
    replace("3500,'Finite grid deadline'", "3300,'Finite fine-grid deadline'")
    replace("'complete_finite_native_grid_geometry'", "'complete_finite_native_fine_grid_geometry'")
    replace("'pass_early_grid_admission'", "'pass_early_fine_grid_admission'")
    replace("'failed_grid_global_admission'", "'failed_fine_grid_global_admission'")
    replace("str(OUT/'prepare_candidates.py')", "str(OUT/'prepare_fine_candidates.py')")
    replace("str(OUT/name/'navmesh.json'),str(OUT/name),'--spec',str(OUT/'grid_spec.json')]", "str(OUT/name/'navmesh.json'),str(OUT/name),'--spec',str(OUT/'grid_spec.json'),'--coarse',str(COARSE)]")
    replace("str(OUT/('prepare_'+('links' if name=='saved_links' else name)+'.py'))", "str(OUT/'prepare_fine_links.py')")
    replace("if current_name=='links':prepare_post('sight');phase='preparing';write();return", "if current_name=='links':environment_check();finish();return")
    replace("export_nav('saved');prepare('saved');phase='preparing';write();return", "if STAGE=='Expanded':expand();phase='expanded_ready';write();return\n            export_nav('saved');prepare('saved');phase='preparing';write();return")
    replace("if STAGE=='Early':early();environment_check();finish();return", "if STAGE=='Early':early();environment_check();finish();return\n            if STAGE=='Expanded' and current_name=='full':early();environment_check();write()")
    replace("editor=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)", "if STAGE=='Expanded':\n    prior=json.loads((OUT/'saved_source_receipt.json').read_text())\n    assert prior['status']=='pass_saved_scope_native_audit'\n    report['reused_saved_source']=prior\n    parent=json.loads(Path(prior['source_entry']).joinpath('result.json').read_text())\n    report['passes']={k:parent['passes'][k] for k in ('saved','saved_links')}\neditor=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)")
    start=source.index('def early():');end=source.index('\ndef expand():',start)
    source=source[:start]+'''def early():
    from grid_core import polygon_cells,cell_xy,world_cell
    from prepare_fine_candidates import BRIDGES
    known=json.loads((COARSE.parent/'early_v3_20261007/result.json').read_text())
    road=known['early_controls'][0]['request']['xyz']
    stack_xy=known['early_controls'][1]['requests'][0]['xyz'][:2]
    near=[];stacks={};bridges=[[] for _ in BRIDGES]
    for p in native_export['polygons']:
        xs=[v[0] for v in p['vertices_cm']];ys=[v[1] for v in p['vertices_cm']]
        targets=[road[:2],stack_xy]+[list(b) for b in BRIDGES]
        if not any(min(xs)<=x+200 and max(xs)>=x-200 and min(ys)<=y+200 and max(ys)>=y-200 for x,y in targets):continue
        for c,r in polygon_cells(p,grid):
            x,y=cell_xy(grid,c,r)
            req={'id':len(near)+sum(map(len,bridges)),'p':p['id'],'c':c,'r':r,'xyz':[x,y,p['surface_cm'][2]]}
            if math.dist([x,y],road[:2])<=200:near.append(req)
            if math.dist([x,y],stack_xy)<=150:stacks.setdefault((c,r),[]).append(req)
            for k,b in enumerate(BRIDGES):
                if math.dist([x,y],b)<=200:bridges[k].append(req)
    chosen=min(near,key=lambda r:math.dist(r['xyz'][:2],road[:2])+abs(r['xyz'][2]-road[2]))
    result=sample([chosen])[0]
    report['early_controls'].append({'kind':'known_city_road','request':chosen,'result':result})
    assert result['admitted'] and 'Road' in result['mesh']
    options=[rs for rs in stacks.values() if max(r['xyz'][2] for r in rs)-min(r['xyz'][2] for r in rs)>200]
    assert options,'25 cm stacked-surface control absent'
    pair=sorted(min(options,key=lambda rs:math.dist(rs[0]['xyz'][:2],stack_xy)),key=lambda r:r['xyz'][2])
    pair=[pair[0],pair[-1]];result=sample(pair)
    assert result[0]['nav_cm'][:2]==result[1]['nav_cm'][:2] and abs(result[0]['nav_cm'][2]-result[1]['nav_cm'][2])>200
    report['early_controls'].append({'kind':'same_xy_different_surface','requests':pair,'results':result})
    blocking=next(b for b in inventory['blockers'] if b['class']=='/Script/Engine.BlockingVolume');p=blocking['origin_cm']
    req={'id':-1,'p':'0','xyz':[p[0],p[1],p[2]-PROFILE['half_height_cm']-PROFILE['floor_gap_cm']]}
    result=sample([req])[0];assert result['requested_blockers'] and not result['admitted']
    report['early_controls'].append({'kind':'known_blocking_volume','request':req,'result':result})
    for k,rows in enumerate(bridges):
        chosen=sorted(rows,key=lambda r:math.dist(r['xyz'][:2],BRIDGES[k]))[:64]
        assert chosen,'25 cm bridge control absent'
        results=sample(chosen);city_clear=sum(r['admitted'] and r['mesh'].startswith('/Game/WW2City/') for r in results)
        assert city_clear>0,'No city support at bridge control'
        report['early_controls'].append({'kind':'bridge_'+chr(65+k),'requests':chosen,'results':results,'city_clear':city_clear})
    report['early_coordinate_checks']=len(near)+sum(map(len,bridges))
    for req in near:
        assert world_cell(grid,*req['xyz'][:2])==(req['c'],req['r'])
''' +source[end:]
    start=source.index('def early():');end=source.index('\ndef expand():',start)
    source=source[:start]+'''def early():
    from grid_core import world_cell
    controls=json.loads((OUT/current_name/'early_controls.json').read_text())
    chosen=controls['road'];result=sample([chosen])[0]
    assert result['admitted'] and ('Road' in result['mesh'] or 'Road' in result['component'])
    report['early_controls'].append({'kind':'known_city_road','request':chosen,'result':result})
    pair=controls['stack'];result=sample(pair)
    assert result[0]['nav_cm'][:2]==result[1]['nav_cm'][:2] and abs(result[0]['nav_cm'][2]-result[1]['nav_cm'][2])>200
    report['early_controls'].append({'kind':'same_xy_different_surface','requests':pair,'results':result})
    blocking=next(b for b in inventory['blockers'] if b['class']=='/Script/Engine.BlockingVolume');p=blocking['origin_cm']
    req={'id':-1,'p':'0','xyz':[p[0],p[1],p[2]-PROFILE['half_height_cm']-PROFILE['floor_gap_cm']]}
    result=sample([req])[0];assert result['requested_blockers'] and not result['admitted']
    report['early_controls'].append({'kind':'known_blocking_volume','request':req,'result':result})
    for k,requests in enumerate(controls['bridges']):
        results=sample(requests);city_clear=sum(r['admitted'] and r['mesh'].startswith('/Game/WW2City/') for r in results)
        assert city_clear>0,'No city support at bridge control'
        report['early_controls'].append({'kind':'bridge_'+chr(65+k),'requests':requests,'results':results,'city_clear':city_clear})
    for req in [chosen]+pair+[r for rows in controls['bridges'] for r in rows]:
        assert world_cell(grid,*req['xyz'][:2])==(req['c'],req['r'])
    report['early_coordinate_checks']=controls['coordinate_checks']
''' +source[end:]
    target=HERE/'ue_fine_grid.py';target.write_text(source,encoding='utf-8')
    print(target)

if __name__=='__main__':build()
