"""Separate recording build; retain selected source, assets and normal playable."""
import argparse,hashlib,json,shutil,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'tmp/g1-demo-draft03-20261009'
SOURCE=ROOT/'Unreal/Variants/G1FootContactAudio20261009/Project'
PARENT=ROOT/'tmp/g1-foot-contact-audio-v2-20261009/candidate_v2/Project'
NORMAL=ROOT/'tmp/Playtest-G1-Foley-V2-20261009'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def rows(base):return [dict(path=p.relative_to(base).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(base.rglob('*')) if p.is_file()]
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n','utf-8')
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--revision',default='recording_v1');args=parser.parse_args()
 assert args.revision in ('recording_v1','recording_v2')
 PROJECT=OUT/args.revision/'Project'
 assert not PROJECT.exists(),'Preserve previous source/build identity'
 OUT.mkdir(exist_ok=True)
 manifest=json.loads((SOURCE.parent/'SOURCE_MANIFEST.json').read_text('utf-8-sig'))
 for r in manifest['files']:assert sha(SOURCE/r['path'])==r['sha256'],r['path']
 game=NORMAL/'Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe'
 assert sha(game)=='53ab36d9da1975a2f8e1109fcf6745cc40e96d371fc89fbfa009139b91950aec'
 saves=Path.home()/'AppData/Local/ParisStreetCombat/G1PlaytestFoleyV220261009'
 protected=rows(saves) if saves.exists() else []
 cooked=rows(NORMAL)
 shutil.copytree(SOURCE,PROJECT)
 ps=Path(r'C:/Users/hzgyp/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe')
 taskPSCommand="New-Item -ItemType Junction -Path '"+str(PROJECT/'Content').replace("'","''")+"' -Value '"+str(ROOT/'Unreal/ParisStreetCombat/Content').replace("'","''")+"' | Out-Null"
 subprocess.run([str(ps),'-NoProfile','-Command',taskPSCommand],check=True)
 for folder in ('Intermediate','Binaries'):
  if (PARENT/folder).exists():shutil.copytree(PARENT/folder,PROJECT/folder)
 private=PROJECT/'Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private'
 for name in ('ParisDemoInput.cpp','ParisDemoInput.h'):shutil.copyfile(Path(__file__).parent/name,private/name)
 module=private/'ParisBridgeMissionV1.cpp';s=module.read_text('utf-8-sig')
 assert s.count('#include "ParisGameplayAV.h"')==1
 s=s.replace('#include "ParisGameplayAV.h"','#include "ParisGameplayAV.h"\n#include "ParisDemoInput.h"')
 assert s.count('  ParisGameplayAV::Initialize();')==1
 s=s.replace('  ParisGameplayAV::Initialize();','  ParisGameplayAV::Initialize();\n  ParisDemoInput::Initialize();')
 assert s.count('void ShutdownModule()override{')==1
 s=s.replace('void ShutdownModule()override{','void ShutdownModule()override{ParisDemoInput::Shutdown();')
 module.write_text(s,'utf-8')
 changed=[r['path'] for r in manifest['files'] if sha(PROJECT/r['path'])!=r['sha256']]
 assert changed==['Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/ParisBridgeMissionV1.cpp']
 assert 'SetControlRotation' not in (private/'ParisDemoInput.cpp').read_text('utf-8')
 save(OUT/(args.revision+'_prepare.json'),dict(status='prepared_not_yet_built',project=str(PROJECT),parent_source=str(SOURCE),parent_manifest=manifest,parent_game_sha256=sha(game),changed=changed,normal_playable=str(NORMAL),normal_files=cooked,user_saves_root=str(saves),user_saves=protected,scope='Only separate opt-in normal input helper/module wiring; current normal gameplay untouched'))
 print(json.dumps(dict(source_rows=len(manifest['files']),normal_files=len(cooked),user_files=len(protected),project=str(PROJECT))),flush=True)
if __name__=='__main__':main()
