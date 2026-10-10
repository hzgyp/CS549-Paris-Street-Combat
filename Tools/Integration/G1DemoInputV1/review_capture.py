"""Inspect completed OBS media and native read-only evidence; never drives UI."""
import argparse,datetime as dt,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'tmp/g1-demo-draft03-20261009'
FF=Path(r'C:/Users/hzgyp/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe')
def run(a):return subprocess.run([str(FF),'-hide_banner','-nostdin']+a,capture_output=True,text=True,encoding='utf-8',errors='replace')
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--video',required=True,type=Path);args=p.parse_args()
 case=OUT/args.case;r=json.loads((case/'result.json').read_text('utf-8-sig'))
 review=case/'media_review';assert not review.exists();review.mkdir()
 metadata=run(['-i',str(args.video),'-f','null','-']);(review/'full_decode.log').write_text(metadata.stderr,'utf-8');assert metadata.returncode==0
 samples=r['samples'];rates=[]
 for a,b in zip(samples,samples[1:]):
  t=b['wall']-a['wall']
  if a['generation']==b['generation'] and 0<t<.25:
   d=(b['yaw']-a['yaw']+180)%360-180;rates.append(abs(d)/t)
 rate=max(rates,default=0)
 native=[dict(event=e['event'],wall_seconds=e['wall_seconds']) for e in r['events']]
 event_times={}
 for line in (case/'game.log').read_text('utf-8-sig').splitlines():
  m=re.match(r'\[(\d{4}\.\d{2}\.\d{2}-\d{2}\.\d{2}\.\d{2}:\d{3})\].*PARIS_DEMO_INPUT (.+)',line)
  if m:event_times.setdefault(m[2],dt.datetime.strptime(m[1],'%Y.%m.%d-%H.%M.%S:%f').replace(tzinfo=dt.timezone.utc).isoformat())
 result=dict(status='technical_review_visual_audio_event_admission_pending',native_status=r['status'],maximum_sampled_yaw_rate=rate,full_decode_exit=metadata.returncode,video=str(args.video.resolve()),events=native,event_times_utc=event_times)
 (review/'review.json').write_text(json.dumps(result,indent=2)+'\n','utf-8')
 print(json.dumps(result,indent=2),flush=True)
if __name__=='__main__':main()
