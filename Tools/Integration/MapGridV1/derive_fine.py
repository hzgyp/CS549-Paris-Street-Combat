"""Rebuild independent fine components and meter-based purpose masks, excluding old failures."""
import argparse,json,gc
from array import array
from collections import Counter
from pathlib import Path
import numpy as np
from PIL import Image
from grid_core import digest
from fine_filters import filters

def derive(entry):
    out=entry/'derived';out.mkdir();spec=json.loads((entry/'grid_spec.json').read_text())
    summary={'cell_cm':25,'scopes':{},'failed_coarse_world_footprint_cm':[14700,-13700,14800,-13600],
             'encounter_fine_endpoint_visibility_measured':False,'final_layout_selected':False}
    for name,folder in (('saved','saved_links'),('full','links')):
        print('Loading '+name,flush=True)
        nodes=json.loads((entry/folder/'nodes.json').read_text());n=len(nodes)
        c=np.array([x['c'] for x in nodes],dtype=np.int32);r=np.array([x['r'] for x in nodes],dtype=np.int32)
        z=np.array([x['feet_cm'][2] for x in nodes]);road=np.array([x['road'] for x in nodes],dtype=bool)
        x=spec['xmin_cm']+(c+.5)*25;y=spec['ymax_cm']-(r+.5)*25
        quarantine=(x>=14700)&(x<14800)&(y>-13700)&(y<=-13600)
        aa=array('I');bb=array('I');total=admitted=0
        for line in (entry/folder/'samples.jsonl').open(encoding='utf-8'):
            row=json.loads(line);total+=1
            if row['admitted']:
                admitted+=1;a=row['from'];b=row['to']
                if not quarantine[a] and not quarantine[b]:aa.append(a);bb.append(b)
        a=np.frombuffer(aa,dtype=np.uint32).copy();b=np.frombuffer(bb,dtype=np.uint32).copy();del aa,bb
        keys=(a.astype(np.uint64)<<32)|b.astype(np.uint64);ordered=np.sort(keys)
        reverse=(b.astype(np.uint64)<<32)|a.astype(np.uint64)
        idx=np.searchsorted(ordered,reverse);valid=idx<len(ordered)
        valid&=ordered[np.minimum(idx,len(ordered)-1)]==reverse
        a,b=a[valid],b[valid];del keys,ordered,reverse,idx,valid
        parent=np.arange(n,dtype=np.int32)
        def find(k):
            while parent[k]!=k:parent[k]=parent[parent[k]];k=parent[k]
            return k
        for u,v in zip(a.tolist(),b.tolist()):
            if u>=v:continue
            uu,vv=find(u),find(v)
            if uu!=vv:parent[max(uu,vv)]=min(uu,vv)
        roots=np.array([find(i) for i in range(n)],dtype=np.int32);roots[quarantine]=-1
        sizes=Counter(roots[~quarantine].tolist());rank={root:k for k,(root,_) in enumerate(sorted(sizes.items(),key=lambda p:(-p[1],p[0])))}
        group=np.array([rank.get(root,-1) for root in roots],dtype=np.int32)
        has_road=np.zeros(len(rank),dtype=bool);has_road[group[road&~quarantine]]=True
        base=(group>=0)&has_road[np.maximum(group,0)]&~quarantine
        del parent,roots
        count2,count3,task=filters(c,r,z,group,base,a,b)
        layer=np.array([x['layer'] for x in nodes],dtype=np.int16)
        np.savez_compressed(out/(name+'_filters.npz'),c=c,r=r,group=group,base=base,quarantine=quarantine,count2=count2,count3=count3,task=task,layer=layer)
        counts={};groups=[]
        for gid,size in Counter(group[base].tolist()).most_common():groups.append({'id':int(gid),'cells':int(size)})
        for l in range(int(layer.max())+1):
            active=base&(layer==l)
            group_img=np.zeros((spec['rows'],spec['columns'],3),dtype=np.uint8)
            val=group[active]+1;cc=c[active];rr=r[active]
            group_img[rr,cc,0]=val&255;group_img[rr,cc,1]=(val>>8)&255;group_img[rr,cc,2]=(val>>16)&255
            Image.fromarray(group_img).save(out/f'{name}_groups_L{l}.png')
            for mode,flag in [('walk',base),('task',task),('encounter',np.zeros(n,dtype=bool))]+[(f'spawn_{radius}_{minimum}',base&(sites>=minimum)) for radius,sites in ((2,count2),(3,count3)) for minimum in (3,5,6)]:
                use=flag&(layer==l);bitmap=np.zeros((spec['rows'],spec['columns']),dtype=np.uint8);bitmap[r[use],c[use]]=255
                Image.fromarray(bitmap).convert('1').save(out/f'{name}_{mode}_L{l}.png');counts[f'{mode}_L{l}']=int(np.count_nonzero(bitmap))
        bridge_counts=[]
        from prepare_fine_candidates import BRIDGES
        for bx,by in BRIDGES:
            near=(np.abs(x-bx)<1000)&(np.abs(y-by)<1000)
            exact=np.array(['SM_Bridge_01a' in node['mesh'] for node in nodes])&near
            bridge_counts.append({'bridge':chr(65+len(bridge_counts)),'clear_bridge_mesh_nodes':int(exact.sum()),'road_connected_bridge_mesh_nodes':int((exact&base).sum()),'area_road_groups':sorted(set(group[near&base].tolist()))})
        endpoints=[]
        for px,py,pz in ((1950,-20650,114.26299010216593),(5850,-20250,110.14999471592469)):
            near=(np.hypot(x-px,y-py)<=35)&(np.abs(z-pz)<=35)&base
            ids=np.flatnonzero(near);selected=int(ids[np.argmin(np.hypot(x[ids]-px,y[ids]-py))]) if len(ids) else None
            endpoints.append({'test_xy_cm':[px,py],'near_fine_nodes':len(ids),'selected_id':selected,'group':int(group[selected]) if selected is not None else None})
        summary['scopes'][name]={'native_city_nodes':n,'components':len(rank),'road_groups':groups,'purpose_counts':counts,'layers':int(layer.max())+1,
                                 'link_rows':total,'admitted_directed_links':admitted,'reciprocal_after_quarantine':len(a),'quarantined_node_ids':np.flatnonzero(quarantine).tolist(),
                                 'bridges':bridge_counts,'C_test_endpoint_projection':endpoints,'C_fine_graph_same_group':all(e['group'] is not None for e in endpoints) and endpoints[0]['group']==endpoints[1]['group'],
                                 'station_pitch_cm':100,'station_radius_m':[2,3],'station_maximum_stencil':[13,29],
                                 'source_nodes_sha256':digest(entry/folder/'nodes.json'),'source_links_sha256':digest(entry/folder/'samples.jsonl')}
        print(json.dumps({k:v for k,v in summary['scopes'][name].items() if k not in ('road_groups','quarantined_node_ids')}),flush=True)
        del nodes,a,b,c,r,z,road,quarantine,group,base,count2,count3,task,layer;gc.collect()
    (out/'manifest.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('entry',type=Path);derive(p.parse_args().entry)
