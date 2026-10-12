"""Run prepared, conflict-free native capture batches with durable progress."""
import json,subprocess,time,sys,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'Assets/LocalWorking/AssetWorkbench/native-covers-v1'
UE='C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe'
for dest in sorted(OUT.glob('batch-*')):
 if len(sys.argv)>1 and dest.name!=sys.argv[1]:continue
 receipt=dest/'process.json'
 if receipt.exists():continue
 args=[UE,str(dest/'Project/AssetCoverLab.uproject'),'-run=pythonscript','-script='+str(ROOT/'Tools/AssetWorkbench/ue_capture_cover_batch.py'),'-AllowCommandletRendering','-unattended','-NoP4','-NoSplash','-nosound','-d3d12','-NoSteam','-DDC=InstalledNoZenLocalFallback','-UDPMESSAGING_TRANSPORT_ENABLE=false','-abslog='+str(dest/'engine.log')]
 started=time.time()
 with (dest/'process.log').open('w') as log:
  proc=subprocess.Popen(args,stdout=log,stderr=log,creationflags=subprocess.CREATE_NO_WINDOW)
  (dest/'running.json').write_text(json.dumps({'pid':proc.pid,'started':started,'project':args[1]}))
  try:code=proc.wait(timeout=2400)
  except subprocess.TimeoutExpired:
   proc.kill();code=proc.wait();receipt.write_text(json.dumps({'exit_code':code,'status':'timeout','seconds':time.time()-started}));raise
 receipt.write_text(json.dumps({'exit_code':code,'seconds':time.time()-started}))
 print('BATCH_DONE',dest.name,code,round(time.time()-started,1),flush=True)
