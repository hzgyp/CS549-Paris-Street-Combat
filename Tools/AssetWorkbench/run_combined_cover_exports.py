import json,subprocess,time,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'Assets/LocalWorking/AssetWorkbench/native-covers-v1'
UE='C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe'
for dest in sorted(OUT.glob('batch-*')):
 if len(sys.argv)>1:
  if sys.argv[1]=='--remaining' and dest.name=='batch-00':continue
  if sys.argv[1]!='--remaining' and dest.name!=sys.argv[1]:continue
 receipt=dest/'export-v4c-process.json'
 if receipt.exists():continue
 args=[UE,str(dest/'Project/AssetCoverLab.uproject'),'-run=pythonscript','-script='+str(ROOT/'Tools/AssetWorkbench/ue_export_combined_cover.py'),'-AllowCommandletRendering','-d3d12','-unattended','-NoP4','-NoSplash','-nosound','-NoSteam','-DDC=InstalledNoZenLocalFallback','-UDPMESSAGING_TRANSPORT_ENABLE=false','-abslog='+str(dest/'export-v4c-engine.log')]
 started=time.time()
 with (dest/'export-v4c-process.log').open('w') as log:
  proc=subprocess.Popen(args,stdout=log,stderr=log,creationflags=subprocess.CREATE_NO_WINDOW)
  (dest/'export-running.json').write_text(json.dumps({'pid':proc.pid,'started':started,'project':args[1]}))
  try:code=proc.wait(timeout=1200)
  except subprocess.TimeoutExpired:proc.kill();code=proc.wait();raise
 receipt.write_text(json.dumps({'exit_code':code,'seconds':time.time()-started}))
 print('EXPORT_BATCH_DONE',dest.name,code,round(time.time()-started,1),flush=True)
