"""Run isolated UE read-only preview commandlets. Preserve all attempts and sessions."""
from prepare_native_covers import *
import time
UE='C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe'
SCRIPT=ROOT/'Tools/AssetWorkbench/ue_capture_asset_cover.py'
for row in facts['archives']:
 if len(sys.argv)>1 and sys.argv[1] not in row['title']:continue
 try:
  job=prepare(row);dest=OUT/job['id'];result=dest/'capture-v1/result.json'
  if result.exists():print('PRESERVED',job['id'],json.loads(result.read_text())['status'],flush=True);continue
  start=time.time()
  args=[UE,job['project'],'-run=pythonscript','-script='+str(SCRIPT),'-AllowCommandletRendering','-unattended','-NoP4','-NoSplash','-nosound','-d3d12','-NoSteam','-DDC=InstalledNoZenLocalFallback','-UDPMESSAGING_TRANSPORT_ENABLE=false','-abslog='+str(dest/'capture-v1-engine.log')]
  with (dest/'process.log').open('w') as log:
   proc=subprocess.run(args,stdout=log,stderr=log,timeout=600,creationflags=subprocess.CREATE_NO_WINDOW)
  status=json.loads(result.read_text())['status'] if result.exists() else 'no_result'
  (dest/'process.json').write_text(json.dumps({'exit_code':proc.returncode,'seconds':time.time()-start,'status':status}))
  print('CAPTURE',job['id'],status,round(time.time()-start,1),flush=True)
 except Exception as e:print('FAILED',row['title'],type(e).__name__,flush=True)
