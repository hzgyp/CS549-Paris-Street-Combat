"""Conservative planning filters built only from measured native cells and links."""
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np


class PlanningData:
    def __init__(self,entry):
        self.entry=Path(entry)
        self.spec=json.loads((self.entry/'grid_spec.json').read_text(encoding='utf-8'))
        self.nodes=json.loads((self.entry/'derived_v3/nodes.json').read_text(encoding='utf-8'))
        derived=json.loads((self.entry/'derived_v3/manifest.json').read_text(encoding='utf-8'))
        self.current_offset=derived['current_source_native_offset']
        self.by_cell=defaultdict(list)
        for n in self.nodes:self.by_cell[(n['c'],n['r'])].append(n)
        self.links=set();self.outgoing=defaultdict(set)
        with (self.entry/'links/samples.jsonl').open(encoding='utf-8') as f:
            for line in f:
                r=json.loads(line)
                if r['admitted']:self.links.add((r['from'],r['to']))
        for a,b in self.links:
            if (b,a) in self.links:self.outgoing[a].add(b)
        matched_current=defaultdict(list)
        for n in self.nodes:
            if n['scope']=='current':
                for k in n['survey_node_ids']:matched_current[k].append(n['id'])
        self.sight=defaultdict(set)
        with (self.entry/'sight/samples.jsonl').open(encoding='utf-8') as f:
            for line in f:
                r=json.loads(line)
                if r['admitted']:
                    self.sight[r['from']].add(r['to']);self.sight[r['to']].add(r['from'])
                    for a in matched_current[r['from']]:
                        for b in matched_current[r['to']]:
                            self.sight[a].add(b);self.sight[b].add(a)
        self.saved_pairs=set();self.current_links=set()
        with (self.entry/'saved_links/samples.jsonl').open(encoding='utf-8') as f:
            for line in f:
                r=json.loads(line)
                if r['admitted']:
                    self.saved_pairs.add((r['from'],r['to']))
                    self.current_links.add((r['from']+self.current_offset,r['to']+self.current_offset))
        for a,b in self.current_links:
            if (b,a) in self.current_links:self.outgoing[a].add(b)
        self.space_cache={};self.mask_cache={}

    def groups(self,current):
        sizes=Counter(n['saved_group' if current else 'group'] for n in self.nodes
                      if n['scope']==('current' if current else 'survey') and n['saved_road_connected' if current else 'road_connected'])
        return [{'id':i,'cells':size} for i,size in sizes.most_common()]

    def base(self,n,current,group=-1):
        if n.get('quarantined',False) or n['scope']!=('current' if current else 'survey'):return False
        if current:
            return n['saved'] and n['saved_road_connected'] and (group<0 or n['saved_group']==group)
        return n['road_connected'] and (group<0 or n['group']==group)

    def reciprocal(self,a,b,current):
        pairs=self.current_links if current else self.links
        return (a['id'],b['id']) in pairs and (b['id'],a['id']) in pairs

    def local_sites(self,n,current,radius=2):
        key=(n['id'],current,radius)
        if key in self.space_cache:return self.space_cache[key]
        group=n['saved_group' if current else 'group'];sites=[];seen={n['id']};queue=[n['id']]
        while queue:
            k=queue.pop();other=self.nodes[k];sites.append(k)
            for target in self.outgoing[k]:
                if target in seen:continue
                candidate=self.nodes[target]
                dc=candidate['c']-n['c'];dr=candidate['r']-n['r']
                if dc*dc+dr*dr>radius*radius:continue
                if not self.base(candidate,current,group) or abs(candidate['feet_cm'][2]-n['feet_cm'][2])>20:continue
                if not self.reciprocal(other,candidate,current):continue
                seen.add(target);queue.append(target)
        # One site per XY; each has an independently clear 68cm-diameter capsule.
        chosen=[];occupied=set()
        for site in sorted(sites,key=lambda k:(abs(self.nodes[k]['feet_cm'][2]-n['feet_cm'][2]),k)):
            other=self.nodes[site];xy=(other['c'],other['r'])
            if xy not in occupied:chosen.append(site);occupied.add(xy)
        self.space_cache[key]=chosen
        return chosen

    def operating_space(self,n,current):
        group=n['saved_group' if current else 'group']
        center=n['feet_cm'][2]
        stencil=[]
        for dc,dr in ((0,0),(1,0),(-1,0),(0,1),(0,-1)):
            options=[o for o in self.by_cell.get((n['c']+dc,n['r']+dr),[])
                     if self.base(o,current,group) and abs(o['feet_cm'][2]-center)<=20]
            if not options:return False
            other=min(options,key=lambda o:abs(o['feet_cm'][2]-center))
            if dc or dr:
                if not self.reciprocal(n,other,current):return False
            stencil.append(other)
        return True

    def eligible(self,n,mode,current,group=-1,min_sites=3,radius=2):
        if not self.base(n,current,group):return False
        if mode=='walk':return True
        if mode=='spawn':return len(self.local_sites(n,current,radius))>=min_sites
        if mode=='task':return self.operating_space(n,current)
        if mode=='encounter':
            if len(self.local_sites(n,current,2))<3:return False
            if sum(self.reciprocal(n,self.nodes[k],current) for k in self.outgoing[n['id']])<2:return False
            for target in self.sight[n['id']]:
                other=self.nodes[target]
                if self.base(other,current,n['saved_group' if current else 'group']) and len(self.local_sites(other,current,2))>=3:
                    return True
            return False
        raise ValueError('Unknown purpose')

    def mask(self,mode='walk',current=True,group=-1,layer=0,min_sites=3,radius=2):
        key=(mode,current,group,layer,min_sites,radius)
        if key in self.mask_cache:return self.mask_cache[key]
        bitmap=np.zeros((self.spec['rows'],self.spec['columns']),dtype=np.uint8)
        ids=[]
        for n in self.nodes:
            if n['layer']!=layer:continue
            if self.eligible(n,mode,current,group,min_sites,radius):
                bitmap[n['r'],n['c']]=255;ids.append(n['id'])
        if ids:
            ns=[self.nodes[k] for k in ids]
            bbox=[min(n['c'] for n in ns),min(n['r'] for n in ns),max(n['c'] for n in ns)+1,max(n['r'] for n in ns)+1]
        else:bbox=[0,0,self.spec['columns'],self.spec['rows']]
        meta={'white_cells':len(ids),'black_cells':bitmap.size-int(np.count_nonzero(bitmap)),
              'bbox_cells':bbox,'mode':mode,'current_saved_navigation':current,'group':group,
              'layer':layer,'minimum_assembly_sites':min_sites,'assembly_radius_m':radius,
              'all_white_centers_mutually_connected':group>=0}
        self.mask_cache[key]=(bitmap,meta,ids)
        return bitmap,meta,ids


REASONS={
    'runtime_return_standing_capsule_overlap':'正式玩家到达后返回前站立重叠；本格隔离，未准入',
    'outside_navigation':'无指定导航表面',
    'unsupported_or_nonwalkable_floor':'无可步行支撑或地面查询穿入碰撞',
    'surface_floor_height_mismatch':'导航高度与实际站立高度不一致',
    'capsule_blocked':'正式尺寸胶囊被阻挡',
    'non_city_or_unclassified_support':'非城市支撑或代理支撑尚未准入',
    'city_geometry_clear':'城市支撑与胶囊净空通过',
    'no_navigation_or_coarse_unmeasured':'无导航覆盖，或一米格心未覆盖窄小表面；不能断言物理不可走',
}
