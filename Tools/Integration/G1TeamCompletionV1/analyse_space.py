"""Choose one bounded measured proposal; no game writes or coordinate retries."""
import json,re,math,collections
from prepare import ROOT,OUT,sha,load
def xyz(s):return [float(re.search(k+r'=([-\d.]+)',s)[1]) for k in ['X','Y','Z']]
def dist(a,b):return math.dist(a[:2],b[:2])
def main():
    p=OUT/'checks/survey_v1/result.json';r=load(p);launch=load(p.parent/'launch.json')
    assert r['status']=='pass_finite_read_only_space_survey' and launch['exit_code']==0
    assert len(r['npc_cells'])==2205 and len(r['prone_corridors'])==289
    original={x['id']:xyz(x['feet']) for x in r['original_actors']};centres={'Ally1':[1512.5,-21462.5],'Ally2':[1262.5,-20212.5],'German1':[6612.5,-20662.5],'German2':[7387.5,-19937.5],'German3':[7612.5,-21362.5]}
    counts={};choices={};blocked=collections.Counter()
    for cell in r['npc_cells']:
        for hit in cell.get('blocking',[]):blocked[hit['actor'].split('.')[-1]]+=1
    for name,centre in centres.items():
        cells=[x for x in r['npc_cells'] if x['id']==name];good=[x for x in cells if x.get('admitted_static')]
        counts[name]=dict(measured=len(cells),static_admitted=len(good),sight_to_farbank=sum(x.get('sight_to_farbank',False) for x in good))
        viable=[]
        for x in good:
            pos=xyz(x['feet'])
            if name.startswith('Ally') and dist(pos,original['Player'])<350:continue
            if any(dist(pos,xyz(y['feet']))<(500 if name=='Ally2' and key=='Ally1' else 350) for key,y in choices.items()):continue
            viable.append(x)
        assert viable,'No complete-space proposal for '+name
        # Prefer fixed region centres, with a sightline for the first guard.
        viable.sort(key=lambda x:((not x['sight_to_farbank']) if name=='German1' else False,dist(xyz(x['feet']),centre),-x['normal_z'],x['feet']))
        choices[name]=viable[0]
    corridors=[x for x in r['prone_corridors'] if x.get('admitted_static')];assert corridors,'No full prone corridor; stop without widening survey'
    corridors.sort(key=lambda x:(dist(xyz(x['feet']),original['Player']),x['feet']))
    proposal=dict(status='measured_proposal_not_runtime_adopted',survey_sha256=sha(p),survey_game_sha256=launch['game_sha256'],npc_counts=counts,blocking_actor_counts=blocked.most_common(8),original_feet=original,npc_feet={key:xyz(x['feet']) for key,x in choices.items()},npc_evidence=choices,prone_corridors_measured=289,prone_corridors_admitted=len(corridors),prone_feet=xyz(corridors[0]['feet']),prone_evidence=corridors[0],limitations='Single proposal based on full-space admission; no actual spawn/squad/engagement/crawl proof yet')
    out=OUT/'measured_proposal.json';assert not out.exists();out.write_text(json.dumps(proposal,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:proposal[k] for k in ['status','npc_counts','blocking_actor_counts','npc_feet','prone_corridors_admitted','prone_feet']},ensure_ascii=False))
if __name__=='__main__':main()
