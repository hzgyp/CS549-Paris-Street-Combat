"""Admit only visually reviewed actual takes with native gates, sound and live readings."""
import argparse,json,re,datetime as dt
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];WORK=ROOT/'tmp/g1-demo-draft04-20261010'
p=argparse.ArgumentParser();p.add_argument('--case',required=True);args=p.parse_args()
case=WORK/args.case;r=json.loads((case/'result.json').read_text());a=json.loads((case/'av_audit/audit.json').read_text())
mapping={'actions_panel_v1':('pass_actions_pending_media_review','admitted_actions_actual_av_frames_and_native_input'),'victory_panel_v1':('pass_victory_save_restore_pending_media_review','admitted_victory_save_restore_actual_av_frames_and_native_input'),'defeat_panel_v1':('pass_genuine_enemy_defeat_restart_pending_media_review','admitted_genuine_defeat_restart_actual_av_frames_and_native_input')}
assert r['status']==mapping[args.case][0]
events=a['events'];assert min(events.values())>=0 and max(events.values())<a['duration_audio']
rates=[]
for x,y in zip(r['samples'],r['samples'][1:]):
 delta=y['wall']-x['wall']
 if x['generation']==y['generation'] and 0<delta<.25:rates.append(abs((y['yaw']-x['yaw']+180)%360-180)/delta)
assert max(rates,default=0)<60,'Unexpected turn snap'
live=[]
anchor=dt.datetime.fromisoformat(a['anchor']).astimezone(dt.timezone.utc)
for line in (case/'game.log').read_text('utf-8-sig').splitlines():
 if 'PARIS_LIVE_STATS frame=' in line:
  time=dt.datetime.strptime(line[1:24],'%Y.%m.%d-%H.%M.%S:%f').replace(tzinfo=dt.timezone.utc)
  if not 0<=(time-anchor).total_seconds()<=a['duration_audio']:continue
  values=dict(re.findall(r'(\w+)=([\d.]+)',line.split('PARIS_LIVE_STATS ')[1]));live.append({k:float(v) for k,v in values.items()})
assert len(live)>20 and len({x['fps'] for x in live})>10
assert all(abs(x['fps']*x['frame_ms']-1000)<=.0005*(x['fps']+x['frame_ms'])+.01 for x in live if x['frame_ms']>0),'FPS/frame identity beyond3-decimal serialization precision'
assert all(x['ram_bytes']>0 and x['vram_bytes']>0 and x['vram_budget']>0 for x in live)
if args.case=='actions_panel_v1':
 for e in ['step_walk','step_run','step_slow','step_jump','step_reload','step_shot']:assert a['game_audio_stats'][e]['peak']>.001
else:assert a['audio_peak']>.001
if args.case=='defeat_panel_v1':
 assert events['actual_player_damage_100.0_to_65.0']<events['step_lost_hold']<events['step_restart_wait']<events['step_fresh_ready']
if args.case=='victory_panel_v1':
 assert events['step_saved']<events['step_changed_ammo']<events['step_load_wait']<events['step_corpse_observe']
a.update(status=mapping[args.case][1],maximum_sampled_yaw_rate=max(rates,default=0),visual_review='Actual full-frame event images inspected: native live panel readable, values change, minimap/HUD intact; required action/state frames inspected',live_scope='Current UE counters in raw capture, not past CSV or postproduction numeric overlay. 0.9/0.1 frame smoothing, displayed4Hz. Existing NPCs only; measurement/OBS/helper overhead included',live_samples=len(live))
(case/'av_audit/admission.json').write_text(json.dumps(a,indent=2)+'\n','utf-8')
print(json.dumps(dict(status=a['status'],max_yaw_rate=a['maximum_sampled_yaw_rate'],live_samples=len(live),audio_peak=a['audio_peak'])))
