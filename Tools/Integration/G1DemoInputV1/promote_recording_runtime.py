"""Retain old bytes, map a built helper to the isolated stable execution path."""
import argparse,hashlib,json,shutil,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];WORK=ROOT/'tmp/g1-demo-draft03-20261009'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--previous',default='recording_v4');p.add_argument('--revision',default='recording_v5');args=p.parse_args()
    for value in [args.previous,args.revision]:assert value.startswith('recording_v') and value[11:].isdigit()
    probe=subprocess.run(['powershell','-NoProfile','-Command','@(Get-Process UnrealEditor*,WW2FranceLiberation*,UnrealBuildTool,AutomationTool -ErrorAction SilentlyContinue).Count'],capture_output=True,text=True,check=True)
    assert probe.stdout.strip()=='0','Preserve active engine/build'
    inner=Path('Archive/Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe')
    old=WORK/'recording_v4'/inner;new=WORK/args.revision/inner
    a=json.loads((WORK/args.previous/'build.json').read_text('utf-8-sig'));b=json.loads((WORK/args.revision/'build.json').read_text('utf-8-sig'))
    assert a['exit_code']==b['exit_code']==0 and b['status']=='built_runtime_unverified'
    assert sha(old)==a['game_sha256'] and sha(new)==b['game_sha256']
    saved=WORK/args.previous/('retained_Game_'+a['game_sha256'][:4]+'.exe');assert not saved.exists();shutil.copyfile(old,saved);assert sha(saved)==a['game_sha256']
    shutil.copyfile(new,old);assert sha(old)==b['game_sha256']
    receipt_path=WORK/('runtime_remap_'+args.revision.removeprefix('recording_')+'.json');assert not receipt_path.exists()
    receipt=dict(status='isolated_recording_runtime_previous_bytes_retained',runtime=str(old),current_source_revision=args.revision,current_sha256=sha(old),historical_revision=args.previous,historical_sha256=a['game_sha256'],historical_retained_path=str(saved),scope='No normal playable or asset/network setting changed. Historical path hashes do not identify current bytes; the previous byte identity is retained separately.')
    receipt_path.write_text(json.dumps(receipt,indent=2),'utf-8');print(json.dumps(receipt,indent=2),flush=True)
if __name__=='__main__':main()
