"""Loopback-only viewer of private survey data. No Unreal asset or layout writes."""
import argparse
import io
import json
import sqlite3
import threading
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs,urlsplit

from PIL import Image

from grid_core import PROFILE,cell_xy
from planning_data import PlanningData,REASONS


def run(entry,port):
    data=PlanningData(entry)
    manifest=json.loads((entry/'artifact_v3/manifest.json').read_text(encoding='utf-8'))
    lock=threading.Lock()
    page=(Path(__file__).parent/'viewer.html').read_bytes()

    def params(q):
        mode=q.get('mode',['walk'])[0]
        if mode not in ('walk','spawn','task','encounter'):raise ValueError('Invalid purpose')
        current=q.get('current',['1'])[0]=='1';group=int(q.get('group',['-1'])[0]);layer=int(q.get('layer',['0'])[0])
        minimum=int(q.get('minimum',['3'])[0]);radius=int(q.get('radius',['2'])[0])
        if minimum not in (3,5,6) or radius not in (2,3) or not 0<=layer<manifest['layers']:raise ValueError('Invalid filter')
        return mode,current,group,layer,minimum,radius

    class Handler(BaseHTTPRequestHandler):
        def send(self,body,mime='application/json; charset=utf-8'):
            self.send_response(200);self.send_header('Content-Type',mime)
            self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(body)))
            self.end_headers();self.wfile.write(body)

        def send_json(self,value):self.send(json.dumps(value,ensure_ascii=False,separators=(',',':')).encode('utf-8'))

        def do_GET(self):
            try:
                url=urlsplit(self.path);q=parse_qs(url.query)
                if url.path=='/':self.send(page,'text/html; charset=utf-8');return
                if url.path=='/api/config':
                    self.send_json({'spec':data.spec,'layers':manifest['layers'],'profile':PROFILE,
                                    'current_groups':data.groups(True),'survey_groups':data.groups(False),
                                    'identity':entry.name,'final_layout_selected':False});return
                if url.path in ('/api/mask','/map.png'):
                    options=params(q)
                    with lock:bitmap,meta,_=data.mask(*options)
                    if url.path=='/api/mask':self.send_json(meta)
                    else:
                        b=io.BytesIO();Image.fromarray(bitmap).convert('1').save(b,format='PNG');self.send(b.getvalue(),'image/png')
                    return
                if url.path=='/api/point':
                    col=int(q['c'][0]);row=int(q['r'][0]);xy=cell_xy(data.spec,col,row)
                    mode,current,group,layer,minimum,radius=params(q)
                    db=sqlite3.connect('file:'+str(entry/('saved_links' if current else 'links')/'cells.sqlite').replace('\\','/')+'?mode=ro',uri=True)
                    raw=[]
                    for z,reason,city,line in db.execute('SELECT z,reason,city,raw FROM surfaces WHERE c=? AND r=? ORDER BY z',(col,row)):
                        r=json.loads(line)
                        raw.append({'nav_cm':r['nav_cm'],'feet_cm':r['feet_cm'],'reason':reason,
                                    'reason_text':REASONS.get(reason,reason),'component':r['component'],'mesh':r['mesh'],
                                    'floor_walkable':r['floor_walkable'],'blockers':r['blockers'],
                                    'city_support':bool(city),'sample_id':r['id'],'polygon':r['p']})
                    db.close()
                    normalized=[]
                    with lock:
                        for n in data.by_cell.get((col,row),[]):
                            if n['scope']!=('current' if current else 'survey'):continue
                            eligible=data.eligible(n,mode,current,group,minimum,radius)
                            same_group=n['saved_group' if current else 'group']
                            explanation=[]
                            if n['quarantined']:explanation.append(REASONS['runtime_return_standing_capsule_overlap'])
                            if current and not n['saved']:explanation.append('当前正式导航未覆盖此精确表面')
                            if not n['saved_road_connected' if current else 'road_connected']:explanation.append('未建立到道路的双向格间连接')
                            if group>=0 and same_group!=group:explanation.append('属于其他连通组')
                            if n['layer']!=layer:explanation.append('属于其他叠置表面视图')
                            if not eligible and not explanation:explanation.append('未满足当前用途的空间或视线条件')
                            normalized.append({**n,'eligible':eligible and n['layer']==layer,'filter_reasons':explanation,
                                               'source_sample_scope':'saved' if current else 'full',
                                               'assembly_sites':data.local_sites(n,current,radius) if data.base(n,current) else [],
                                               'sight_peers':sorted(data.sight[n['id']])})
                    self.send_json({'col':col,'row':row,'xy_cm':xy,'surfaces':raw,'city_nodes':normalized,
                                    'empty_reason':None if raw else REASONS['no_navigation_or_coarse_unmeasured'],
                                    'profile':PROFILE,'final_layout_selected':False});return
                if url.path=='/api/node':
                    k=int(q['id'][0]);self.send_json(data.nodes[k]);return
                if url.path=='/favicon.ico':self.send(b'','image/x-icon');return
                self.send_error(404)
            except (ValueError,KeyError,IndexError) as e:self.send_error(400,str(e))

        def log_message(self,format,*args):pass

    server=ThreadingHTTPServer(('127.0.0.1',port),Handler)
    print(json.dumps({'url':f'http://127.0.0.1:{port}/','entry':str(entry),'loopback_only':True}),flush=True)
    server.serve_forever()


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('entry',type=Path);p.add_argument('--port',type=int,default=8793)
    a=p.parse_args();run(a.entry,a.port)
