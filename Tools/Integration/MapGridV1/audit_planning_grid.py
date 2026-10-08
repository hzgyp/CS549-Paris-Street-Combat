"""Check provenance, native graph admission, coordinate mapping and binary masks."""
import argparse,json,math
from collections import defaultdict,deque
from pathlib import Path
import numpy as np
from PIL import Image
from grid_core import cell_xy,world_cell,digest
from planning_data import PlanningData

def audit(entry):
    data=PlanningData(entry);dest=entry/'artifact_v3';manifest=json.loads((dest/'manifest.json').read_text())
    for rel,value in manifest['sources'].items():assert digest(entry/rel)==value
    original_full=json.loads((entry/'sight/nodes.json').read_text());original_saved=json.loads((entry/'saved_links/nodes.json').read_text())
    same_fields=['c','r','layer','nav_cm','feet_cm','component','mesh','polys','sample_ids','road']
    for n in data.nodes:
        source=original_saved[n['native_node_id']] if n['scope']=='current' else original_full[n['id']]
        for key in same_fields:assert n[key]==source[key],(n['id'],key)
        xy=cell_xy(data.spec,n['c'],n['r']);assert xy==n['nav_cm'][:2]==n['feet_cm'][:2]
        assert world_cell(data.spec,*xy)==(n['c'],n['r'])
    associations=json.loads((entry/'derived_v3/associations.json').read_text())
    for a in associations:
        c=data.nodes[a['current_id']];s=data.nodes[a['survey_id']]
        assert c['scope']=='current' and s['scope']=='survey' and c['component']==s['component']
        assert c['feet_cm'][:2]==s['feet_cm'][:2] and math.dist(c['feet_cm'],s['feet_cm'])<=.01
        assert a['current_nav_cm']==c['nav_cm'] and a['survey_nav_cm']==s['nav_cm']
    # Independently traverse native reciprocal edges after exclusion, checking that
    # reported groups contain exactly the remaining graph components.
    components={};largest={}
    for current in [True,False]:
        scope='current' if current else 'survey';pairs=data.current_links if current else data.links
        active={n['id'] for n in data.nodes if n['scope']==scope and not n['quarantined']}
        adj=defaultdict(set)
        for a,b in pairs:
            if a in active and b in active and (b,a) in pairs:adj[a].add(b)
        unseen=set(active);groups={};component_count=0
        while unseen:
            start=min(unseen);pending=[start];seen={start};unseen.remove(start)
            while pending:
                a=pending.pop()
                for b in adj[a]:
                    if b not in seen:seen.add(b);unseen.remove(b);pending.append(b)
            key='saved_group' if current else 'group';roadkey='saved_road_connected' if current else 'road_connected'
            ids={data.nodes[k][key] for k in seen};assert len(ids)==1
            group=next(iter(ids));assert group not in groups;groups[group]=seen
            road=any(data.nodes[k]['road'] for k in seen);assert all(data.nodes[k][roadkey]==road for k in seen)
            component_count+=1
        components[scope]=component_count;largest[scope]=len(max(groups.values(),key=len))
    runtime=json.loads((entry/'runtime_admission.json').read_text())
    quarantine={(x['c'],x['r']) for x in runtime['quarantined_cells']}
    assert { (n['c'],n['r']) for n in data.nodes if n['quarantined']}==quarantine
    checked=0;expect=[];sources={}
    for current in [True,False]:
        scope='current' if current else 'survey'
        for layer in range(manifest['layers']):
            for mode in ['walk','spawn','task','encounter']:
                bitmap,meta,ids=data.mask(mode,current,layer=layer)
                path=dest/f'{scope}_{mode}_surface_{layer}.png';image=np.array(Image.open(path).convert('L'))
                assert image.shape==(1008,1008) and set(np.unique(image))<={0,255} and np.array_equal(bitmap,image)
                assert len(ids)==np.count_nonzero(image)==meta['white_cells']
                for c,r in quarantine:assert image[r,c]==0
                for k in ids:
                    n=data.nodes[k];assert not n['quarantined'] and n['scope']==scope
                    if mode=='spawn' or mode=='encounter':
                        sites=data.local_sites(n,current,2);assert len(sites)>=3
                        for j in sites:
                            s=data.nodes[j];assert not s['quarantined'] and s['scope']==scope
                            assert (s['c']-n['c'])**2+(s['r']-n['r'])**2<=4 and abs(s['feet_cm'][2]-n['feet_cm'][2])<=20
                    if mode=='task':assert data.operating_space(n,current)
                    if mode=='encounter':
                        assert sum(data.reciprocal(n,data.nodes[j],current) for j in data.outgoing[k])>=2
                        assert any(data.base(data.nodes[j],current,n['saved_group' if current else 'group']) and len(data.local_sites(data.nodes[j],current,2))>=3 for j in data.sight[k])
                    checked+=1
                sources[path.name]=digest(path)
                expect.append({'query':f'mode={mode}&current={int(current)}&group=-1&layer={layer}&minimum=3&radius=2','white_cells':meta['white_cells']})
        # Other assembly options and default selected connected group.
        group=data.groups(current)[0]['id']
        for mode in ['walk','spawn','task','encounter']:
            _,meta,_=data.mask(mode,current,group=group);expect.append({'query':f'mode={mode}&current={int(current)}&group={group}&layer=0&minimum=3&radius=2','white_cells':meta['white_cells']})
        for radius in [2,3]:
            for minimum in [5,6]:
                _,meta,_=data.mask('spawn',current,min_sites=minimum,radius=radius)
                expect.append({'query':f'mode=spawn&current={int(current)}&group=-1&layer=0&minimum={minimum}&radius={radius}','white_cells':meta['white_cells']})
    result={'status':'pass_planning_provenance_coordinate_binary_and_negative_audit','normalized_nodes':len(data.nodes),'point_roundtrip_error_cm':0,
            'checked_white_admissions_across_filters':checked,'scope_graph_components':components,'largest_scope_components':largest,
            'quarantined_xy':sorted(quarantine),'quarantined_nodes':sum(n['quarantined'] for n in data.nodes),'physical_associations':len(associations),
            'pixel_binary_masks':40,'runtime_summary':runtime['summary'],'sources':sources,'final_layout_selected':False,'browser_ui_verified':False}
    (dest/'offline_expected.json').write_text(json.dumps({'checks':expect,'quarantined_xy':sorted(quarantine),'scope_default_groups':{str(int(c)):data.groups(c)[0]['id'] for c in [True,False]}},indent=2)+'\n')
    target=dest/'audit_planning_v1.json';assert not target.exists();target.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='sources'}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('entry',type=Path);audit(p.parse_args().entry)
