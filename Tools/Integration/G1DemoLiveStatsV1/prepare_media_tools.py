"""Derive new recording04 editing tools while preserving every recording03 file."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).parent
old=ROOT/'Tools/Integration/G1DemoInputV1'
s=(old/'audit_media.py').read_text('utf-8')
s=s.replace("OUT=ROOT/'tmp/g1-demo-draft03-20261009'","OUT=ROOT/'tmp/g1-demo-draft04-20261010'")
s=s.replace("obs_path=Path(r'C:/Users/hzgyp/AppData/Roaming/obs-studio/logs/2026-10-09 18-45-30.txt')","obs_path=max((Path.home()/'AppData/Roaming/obs-studio/logs').glob('*.txt'),key=lambda p:p.stat().st_mtime)")
s=s.replace("import numpy as np","import sys\nsys.path.insert(0,str(Path(__file__).resolve().parents[3]/'tmp/g1-voice-audition-20261009/runtime'))\nimport numpy as np")
(HERE/'audit_media.py').write_text(s,'utf-8')
s=(old/'compose_full_review.py').read_text('utf-8')
s=s.replace('tmp/g1-demo-draft03-20261009','tmp/g1-demo-draft04-20261010').replace('DemoDraft03_20261009','DemoDraft04_20261010')
s=s.replace('actions_probe_v3','actions_panel_v1').replace('victory_v6','victory_panel_v1').replace('defeat_v5','defeat_panel_v1')
s=s.replace('Paris_G1_MVP_Draft_03.mp4','Paris_G1_MVP_Draft_04_Live_Performance.mp4')
s=s.replace('Current build stress test and teammate validation: PENDING','Live UE counters | Existing 1 player + 2 Allies + 3 guards')
s=s.replace("current_build_stress='Pending, no old measurements reused'","current_build_stress='Existing population gameplay, live on-screen UE timings/process RAM/VRAM-budget; not a capacity sweep or normal Game benchmark'")
s=s.replace("Style: Label,Segoe UI,23","Style: Label,Segoe UI,20")
s=s.replace('440,440,20,3,4,0,8,1','430,780,20,3,4,0,8,1').replace('440,440,57,3,4,0,8,1','430,780,57,3,4,0,8,1').replace('440,440,57,3,5,0,8,1','430,780,57,3,5,0,8,1')
# Keep caption/voice information accurate and disclose instrumentation.
s=s.replace('AUTOMATED UE INPUT  |  A / MICHAEL AI VOICE  |  1x','AUTO UE INPUT | A / MICHAEL AI VOICE | 1x')
assert 'PENDING' not in s and 'Paris_G1_MVP_Draft_03' not in s
(HERE/'compose_full_review.py').write_text(s,'utf-8')
print('New recording04 media tools created; recording03 unchanged.')
