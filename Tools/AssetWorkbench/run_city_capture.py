"""Own the isolated commandlet and authenticate map inputs before/after capture."""
import hashlib,json,subprocess,time,argparse,os
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
parser=argparse.ArgumentParser();parser.add_argument('--attempt',default='v1',choices=['v1','v2']);parser.add_argument('--timeout',type=int,default=600);args_cli=parser.parse_args()
BASE=ROOT/'Assets/LocalWorking/AssetWorkbench/runs/city-map-capture-v1'
OUT=ROOT/f'Assets/LocalWorking/AssetWorkbench/runs/city-map-capture-{args_cli.attempt}'
OUT.mkdir(parents=True,exist_ok=True)
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
assert not (OUT/'process.json').exists(),'Preserve the previous run'
manifest=ROOT/'Assets/Sync/manifests/france-liberation-content.json'
m=json.loads(manifest.read_text(encoding='utf-8-sig'))
maps=[ROOT/x['path'] for x in m['files'] if x['path'].endswith('.umap')]
maps+=list((ROOT/'Unreal/ParisStreetCombat/Content/ParisCombat/Maps').glob('*.umap'))
protected={rel(p):sha(p) for p in [manifest,ROOT/'Assets/Sync/CATALOG.json',*maps]}
(OUT/'protected-before.json').write_text(json.dumps(protected,indent=2),encoding='utf-8')
script=ROOT/'Tools/AssetWorkbench/ue_capture_city_map.py'
(OUT/'ue_capture_city_map.py').write_bytes(script.read_bytes())
args=['C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe',str(BASE/'Project/CityPreview.uproject'),
      '-run=pythonscript','-script='+str(OUT/'ue_capture_city_map.py'),'-AllowCommandletRendering','-unattended','-NoP4','-NoSplash','-nosound','-d3d12',
      '-NoSteam','-DDC=InstalledNoZenLocalFallback','-UDPMESSAGING_TRANSPORT_ENABLE=false','-abslog='+str(OUT/'engine.log')]
started=time.time()
env={**os.environ,'CITY_CAPTURE_OUT':str(OUT/'capture-v1')}
exit_code=None;failure=None
with (OUT/'process.log').open('w') as log:
    try:
        proc=subprocess.run(args,stdout=log,stderr=log,timeout=args_cli.timeout,creationflags=subprocess.CREATE_NO_WINDOW,env=env)
        exit_code=proc.returncode
    except subprocess.TimeoutExpired:
        failure='timeout_before_complete_capture'
unchanged=all(sha(ROOT/p)==h for p,h in protected.items())
result=OUT/'capture-v1/result.json'
status=failure or (json.loads(result.read_text())['status'] if result.is_file() else 'no_result')
record={'status':status,'exit_code':exit_code,'seconds':time.time()-started,'protected_map_files':len(maps),'protected_inputs_unchanged':unchanged}
(OUT/'process.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps(record),flush=True)
assert unchanged,'Protected map input changed'
assert exit_code==0 and status=='captured_pending_visual_review','Read actual capture result/log'
