"""Private self-contained map viewer: no listener, service or external resource."""
import argparse
import base64
import gzip
import json
from collections import defaultdict
from pathlib import Path

from grid_core import PROFILE,digest
from planning_data import PlanningData,REASONS


def build(entry):
    data=PlanningData(entry)
    pool=[];index={}
    def intern(text):
        if text not in index:index[text]=len(pool);pool.append(text)
        return index[text]
    nodes=[]
    for n in data.nodes:
        current=n['scope']=='current'
        nodes.append([n['id'],n['c'],n['r'],n['layer'],int(current),n['nav_cm'][2],n['feet_cm'][2],
                      n['saved_group'] if current else n['group'],n['group'] if current else -1,
                      intern(n['component']),intern(n['mesh']),[intern(p) for p in n['polys']],n['sample_ids'],
                      len(data.local_sites(n,current,2)) if data.base(n,current) else 0,
                      len(data.local_sites(n,current,3)) if data.base(n,current) else 0,
                      int(data.eligible(n,'task',current)),int(data.eligible(n,'encounter',current)),
                      int(data.base(n,current)),int(n['quarantined'])])
    raw=[];cols=data.spec['columns'];height=data.spec['rows']
    for scope,name in ((1,'saved'),(0,'full')):
        with (entry/name/'samples.jsonl').open(encoding='utf-8') as f:
            for line in f:
                r=json.loads(line)
                mesh=r['mesh'];component=r['component']
                city=mesh.startswith('/Game/WW2City/') and '/Proxy/' not in mesh and '/LV_Proxy.' not in component and 'Landscape' not in r['actor_class']
                reason=r['reason'] if not r['admitted'] else 'city_geometry_clear' if city else 'non_city_or_unclassified_support'
                key=(scope*height+r['r'])*cols+r['c']
                raw.append([key,r['nav_cm'][2],r['feet_cm'][2],intern(reason),intern(component),intern(mesh),
                            [intern(b) for b in r['blockers']],r['id'],intern(r['p']),int(r['floor_walkable']),int(city)])
    raw.sort(key=lambda r:r[0])
    config={'spec':data.spec,'layers':max(n['layer'] for n in data.nodes)+1,'profile':PROFILE,
            'current_groups':data.groups(True),'survey_groups':data.groups(False),'identity':entry.name,
            'final_layout_selected':False,'offline':True,'runtime_summary':json.loads((entry/'runtime_admission.json').read_text())['summary'],
            'runtime_admission_sha256':digest(entry/'runtime_admission.json')}
    payload={'config':config,'pool':pool,'nodes':nodes,'raw':raw,'reasons':REASONS}
    encoded=base64.b64encode(gzip.compress(json.dumps(payload,separators=(',',':'),ensure_ascii=False).encode('utf-8'),compresslevel=6)).decode('ascii')
    template=(Path(__file__).parent/'viewer.html').read_text(encoding='utf-8')
    adapter=(Path(__file__).parent/'offline_api.js').read_text(encoding='utf-8')
    insert='<script type="application/octet-stream" id="offlineDataset">'+encoded+'</script>\n<script>'+adapter+'</script>\n<script>'
    assert template.count('<script>')==1
    template=template.replace('<script>',insert)
    old="async function getJSON(url){const r=await fetch(url);if(!r.ok)throw Error('数据读取失败 '+r.status);return r.json()}"
    assert template.count(old)==1
    template=template.replace(old,"async function getJSON(url){await offlineReady;return offlineJSON(url)}")
    assert template.count("im.src='/map.png?'+p")==1
    template=template.replace("im.src='/map.png?'+p","im.src=offlineMaskURL(p)")
    target=entry/'artifact_v3/PARIS_GRID_TOOL_20261007.html'
    assert not target.exists();target.write_text(template,encoding='utf-8')
    receipt={'file':str(target),'bytes':target.stat().st_size,'sha256':digest(target),'normalized_nodes':len(nodes),
             'raw_surface_records':len(raw),'offline_no_external_requests':True,'source_entry':entry.name,
             'source_hashes':{name:digest(Path(__file__).parent/name) for name in ('viewer.html','offline_api.js','build_offline.py')}}
    (entry/'artifact_v3/offline_tool_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('entry',type=Path);build(p.parse_args().entry)
