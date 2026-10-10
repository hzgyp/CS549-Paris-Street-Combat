"""Read actual OBS capture and align native events; no gameplay or UI control."""
import argparse, datetime as dt, hashlib, json, re, subprocess
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[3]/'tmp/g1-voice-audition-20261009/runtime'))
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'tmp/g1-demo-draft04-20261010'
FF=Path(r'C:/Users/hzgyp/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe')
def run(args):
    return subprocess.run([str(FF),'-hide_banner','-nostdin']+args,capture_output=True,check=True)
def main():
    p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--video',type=Path,required=True)
    a=p.parse_args();case=OUT/a.case;dest=case/'av_audit';dest.mkdir()
    obs_path=max((Path.home()/'AppData/Roaming/obs-studio/logs').glob('*.txt'),key=lambda p:p.stat().st_mtime)
    obs=obs_path.read_text('utf-8-sig');(dest/'obs.log').write_text(obs,'utf-8')
    line=next(x for x in obs.splitlines() if 'Writing file' in x and a.video.name in x)
    date=a.video.name[:10]
    anchor=dt.datetime.strptime(date+' '+line[:12],'%Y-%m-%d %H:%M:%S.%f').replace(tzinfo=dt.timezone(dt.timedelta(hours=-4)))
    events={}
    for line in (case/'game.log').read_text('utf-8-sig').splitlines():
        m=re.match(r'\[(\d{4}\.\d{2}\.\d{2}-\d{2}\.\d{2}\.\d{2}:\d{3})\].*PARIS_DEMO_INPUT (.+)',line)
        if m:
            wall=dt.datetime.strptime(m[1],'%Y.%m.%d-%H.%M.%S:%f').replace(tzinfo=dt.timezone.utc)
            events.setdefault(m[2],(wall-anchor).total_seconds())
    decoded=run(['-v','error','-xerror','-i',str(a.video),'-map','0:v:0','-map','0:a:0','-f','null','-'])
    (dest/'decode.log').write_bytes(decoded.stderr)
    pcm=run(['-v','error','-i',str(a.video),'-map','0:a:0','-af','aresample=async=1:first_pts=0','-ac','2','-ar','48000','-f','f32le','-']).stdout
    x=np.frombuffer(pcm,'<f4').reshape(-1,2);stats={};frames={}
    for event,t in events.items():
        if event.startswith('step_') or event.startswith('actual_player_damage_'):
            end=min(t+1.5,len(x)/48000);chunk=x[round(t*48000):round(end*48000)].astype(np.float64)
            if len(chunk):stats[event]=dict(peak=float(np.max(np.abs(chunk))),rms=float(np.sqrt(np.mean(chunk**2))))
            at=max(0,t+.5);target=dest/(event+'.jpg')
            run(['-v','error','-ss',str(at),'-i',str(a.video),'-frames:v','1','-q:v','2','-update','1',str(target)])
            frames[event]=dict(seconds=at,path=str(target.resolve()))
    result=dict(status='numeric_decode_and_audio_review_visual_pending',video=str(a.video.resolve()),sha256=hashlib.sha256(a.video.read_bytes()).hexdigest(),anchor=anchor.isoformat(),duration_audio=len(x)/48000,events=events,game_audio_stats=stats,frames=frames,audio_peak=float(np.max(np.abs(x))),audio_rms=float(np.sqrt(np.mean(x.astype(np.float64)**2))))
    (dest/'audit.json').write_text(json.dumps(result,indent=2)+'\n','utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ['frames']},indent=2),flush=True)
if __name__=='__main__':main()
