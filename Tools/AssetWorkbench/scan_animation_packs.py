import subprocess,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'Assets/LocalWorking/AssetWorkbench/native-covers-v1'
UE='C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe'
for batch in sorted(BASE.glob('batch-*'))+[BASE/'repair-movement']:
 if (batch/'animation-directory-v1.json').exists():continue
 with (batch/'animation-directory-v1.log').open('w') as log:
  r=subprocess.run([UE,str(batch/'Project/AssetCoverLab.uproject'),'-run=pythonscript','-script='+str(ROOT/'Tools/AssetWorkbench/ue_scan_animation_packs.py'),'-NullRHI','-unattended','-NoP4','-nosound','-DDC=InstalledNoZenLocalFallback','-UDPMESSAGING_TRANSPORT_ENABLE=false'],stdout=log,stderr=log,timeout=300,creationflags=subprocess.CREATE_NO_WINDOW)
 assert (batch/'animation-directory-v1.json').exists(),batch
 print('SCANNED',batch.name,r.returncode,flush=True)
