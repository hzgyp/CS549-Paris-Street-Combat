"""Audit exact-point native interaction; crowd outcomes never update terrain masks."""
import argparse,json,math,sys
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Integration/NPCInteractionV1'))
from common import STORE,digest,guard_rows,guards_match
from audit import grounded

def audit(entry):
    parent=STORE/'Evidence/NativeConvergenceV1';bank_path=parent/'crowd_bank_v1_20261007/bank.json'
    bank=json.loads(bank_path.read_text());r=json.loads((entry/'result.json').read_text());ex=json.loads((entry/'exit.json').read_text(encoding='utf-8-sig'))
    assert ex['exit_code']==0 and ex['strict_log_errors']==0 and not r['errors'] and r['helpers_unchanged'] and r['protected_bytes_unchanged']
    assert guards_match(bank['protected_rows']) and guard_rows()==bank['protected_rows']
    assert digest(bank_path)==r['bank_sha256'] and r['stage']=='Crowd' and not r['terrain_phase_mutual_test_character_collision_ignored']
    assert not r['nav_rebuilt'] and not r['map_saved'] and r['source_white_scope']=='saved'
    assert all(x['before']==x['after'] for x in r['avoidance_group_isolation'])
    assert all(not x['remaining'] for x in r['crowd_move_ignore_before_travel']) and len(r['crowd_move_ignore_before_travel'])==6
    assert all(grounded(x) for x in r['hub_standing'].values())
    frozen={s['id']:s for s in bank['cases']};assert len(r['cases'])==len(frozen)==3 and {s['id'] for s in r['cases']}==set(frozen)
    counts={'passed':0,'negative':0};samples={};distance=[];hashes={}
    for s in r['cases']:
        f=frozen[s['id']]
        for k in ('role','source_cm','source_node_id','c','r','layer'):assert s[k]==f[k]
        assert grounded(s['source_standing']),'Crowd sources require independent standing admission'
        assert s['request']['started'] and s['request']['goal_cm']==bank['hub']['feet_cm']
        rows=[json.loads(line) for line in (entry/s['samples_file']).open()];assert len(rows)==s['sample_count'] and rows
        samples[s['id']]=rows;hashes[s['samples_file']]=digest(entry/s['samples_file']);counts[s['status']]+=1
        if s['status']=='passed':
            assert grounded(s['arrival_standing']) and s['completion']['result_code']==0
            assert s['completion']['request_id']==s['request']['request_id'] and s['completion']['controller']==s['request']['controller']
            assert s['ended_game_seconds']-s['arrival_first_game_seconds']>=.6-1e-8
        else:
            assert s['reason'] in ('native_path_following_failed','endpoint_standing_rejected','distance_scaled_travel_deadline')
            if s['reason']=='native_path_following_failed':assert s['completion']['result_code']!=0
            if s['reason']=='endpoint_standing_rejected':assert not grounded(s['arrival_standing'])
            if s['reason']=='distance_scaled_travel_deadline':assert s['ended_game_seconds']-s['moving_started_game_seconds']>s['deadline_seconds']
        end=rows[-1];others=end['other_bodies_cm'];minimum=min(math.dist(end['body_cm'][:2],p[:2]) for p in others.values())
        distance.append({'case':s['id'],'status':s['status'],'reason':s['reason'],'goal_xy_error_cm':math.dist(end['feet_cm'][:2],bank['hub']['feet_cm'][:2]),'nearest_other_body_xy_cm':minimum})
    result={'status':'pass_independent_crowd_observation_audit','counts':counts,'endpoints':distance,'terrain_cells_blackened':0,
            'original_rvo_and_mutual_collision_restored':True,'pawn_responses':r['crowd_move_ignore_before_travel'],
            'bank_sha256':digest(bank_path),'receipt_sha256':digest(entry/'result.json'),'observer_sha256':digest(entry/'ue_crowd.py'),
            'exit_sha256':digest(entry/'exit.json'),'samples_sha256':hashes,'formation_acceptance':False,'final_layout_selected':False}
    assert not (entry/'audit.json').exists();(entry/'audit.json').write_text(json.dumps(result,indent=2)+'\n')
    # Real XY trajectories at a common physical scale, not a staged illustration.
    im=Image.new('RGB',(1080,1190),'#f1f1f1');d=ImageDraw.Draw(im);ff=lambda n:ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',n)
    d.text((35,20),'三名正式角色同时走向同一坐标',font=ff(35),fill='black')
    d.text((35,74),f'原生A*、原碰撞和自动避让；到达 {counts["passed"]} / 3，负面 {counts["negative"]} / 3',font=ff(23),fill='black')
    points=[x['feet_cm'][:2] for rows in samples.values() for x in rows];h=bank['hub']['feet_cm'];points.append(h[:2])
    xs=[p[0] for p in points];ys=[p[1] for p in points];size=max(max(xs)-min(xs),max(ys)-min(ys))+300
    mx=(max(xs)+min(xs))/2;my=(max(ys)+min(ys))/2;scale=930/size
    xy=lambda p:(540+(p[0]-mx)*scale,610-(p[1]-my)*scale)
    bounds=(75,145,1005,1075);d.rectangle(bounds,fill='white',outline='#999999')
    for x in range(math.floor((mx-size/2)/100),math.ceil((mx+size/2)/100)+1):
        px=xy([x*100,my])[0]
        if 75<=px<=1005:d.line((px,145,px,1075),fill='#e3e3e3')
    for y in range(math.floor((my-size/2)/100),math.ceil((my+size/2)/100)+1):
        py=xy([mx,y*100])[1]
        if 145<=py<=1075:d.line((75,py,1005,py),fill='#e3e3e3')
    colors=['#007db0','#d48b00','#a74cb5']
    for color,s in zip(colors,r['cases']):
        rows=samples[s['id']];path=[xy(x['feet_cm']) for x in rows];d.line(path,fill=color,width=3)
        start=path[0];end=path[-1];radius=34*scale
        d.ellipse((end[0]-radius,end[1]-radius,end[0]+radius,end[1]+radius),fill=color,outline='black',width=2)
        d.text((start[0]+5,start[1]+5),s['id'].replace('crowd_',''),font=ff(18),fill=color)
    hx,hy=xy(h);rad=35*scale;d.ellipse((hx-rad,hy-rad,hx+rad,hy+rad),outline='#df392f',width=3)
    d.line((hx-10,hy,hx+10,hy),fill='#df392f',width=3);d.line((hx,hy-10,hx,hy+10),fill='#df392f',width=3)
    d.text((35,1094),'线：实际轨迹；实心圆：最终胶囊平面；红圈：35厘米终点范围；背景每格1米。',font=ff(21),fill='black')
    d.text((35,1130),'已到人物留在原地。其他人的失败保留为多人交互负面，不把其出发点涂黑。',font=ff(21),fill='black')
    target=entry/'PARIS_CROWD_POINT_20261007.png';im.save(target)
    print(json.dumps({k:v for k,v in result.items() if k not in ('samples_sha256','pawn_responses')}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('entry',type=Path);audit(p.parse_args().entry)
