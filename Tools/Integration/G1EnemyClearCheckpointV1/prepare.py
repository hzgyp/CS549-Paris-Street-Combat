"""Freeze current reviewed source/user epoch; author an independent clear-only child."""
from pathlib import Path
import hashlib,json,shutil,subprocess
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'tmp/g1-enemy-clear-checkpoint-20261010'
SOURCE=ROOT/'Unreal/Variants/G1EnemyClearCheckpoint20261010/Project'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def rows(base):
 return [dict(path=p.relative_to(base).as_posix(),size_bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(base.rglob('*')) if p.is_file()]
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def main():
 assert not OUT.exists() and not SOURCE.exists(),'Preserve occupied identities'
 p=load(ROOT/'Docs/Development/CURRENT_CHECKPOINT_REVIEW.json')
 assert p['review_id']=='g1-checkpoint-dialog-candidate_v3-20261010'
 manifest=ROOT/p['source_manifest'];assert sha(manifest)==p['source_manifest_sha256']
 files=load(manifest)['files'];assert rows(ROOT/p['source_snapshot'])==files and len(files)==52
 game=ROOT/p['playable_directory']/'Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe';assert sha(game)==p['game_sha256']
 prior=load(ROOT/'tmp/g1-checkpoint-dialog-20261010/freeze.json')
 selected=prior['prior_freeze']['prior_freeze']['selected_parent_freeze']
 for r in selected['protected_native']:assert sha(ROOT/r['path'])==r['sha256'],r['path']
 assert sha(ROOT/'Assets/Sync/CATALOG.json')==selected['catalog_sha256']
 users=[Path.home()/'AppData/Local/ParisStreetCombat/G1Checkpointv320261010',ROOT/'tmp/g1-checkpoint-dialog-20261010/manual-checkpoint/User']
 OUT.mkdir(parents=True);shutil.copytree(ROOT/p['source_snapshot'],SOURCE)
 freeze=dict(parent=p,parent_files=files,parent_game=str(game),parent_game_sha256=sha(game),users=[dict(root=str(u),files=rows(u)) for u in users],protected_native=selected['protected_native'],catalog_sha256=selected['catalog_sha256'],prior_freeze=prior)
 (OUT/'freeze.json').write_text(json.dumps(freeze,indent=2)+'\n',encoding='utf-8')
 # Retain the actual manual failure log independently of later user launches.
 logs=OUT/'manual_failure';logs.mkdir()
 for log in users[0].glob('Saved/Logs/*.log'):shutil.copyfile(log,logs/log.name)
 print(json.dumps(dict(status='parent_frozen',files=len(files),native=len(selected['protected_native']),user_files=sum(len(u['files']) for u in freeze['users']))))
def author(revision='candidate_v1',previous=None,reason='Enemy-clear-only checkpoint admission'):
 target=OUT/revision;assert not target.exists()
 m=SOURCE.parent/'SOURCE_MANIFEST.json'
 if m.exists():shutil.copyfile(m,OUT/(revision+'_previous_manifest.json'))
 files=rows(SOURCE);m.write_text(json.dumps(dict(format='paris-source-snapshot-v1',scope=reason,files=files),indent=2)+'\n',encoding='utf-8')
 project=target/'Project';shutil.copytree(SOURCE,project)
 old=OUT/previous/'Project' if previous else ROOT/load(OUT/'freeze.json')['parent']['active_authoring_project']
 if not previous:old=old.parent
 for name in ['Binaries','Intermediate']:shutil.copytree(old/name,project/name)
 command="New-Item -ItemType Junction -Path '"+str(project/'Content').replace("'","''")+"' -Value '"+str(ROOT/'Unreal/ParisStreetCombat/Content').replace("'","''")+"' | Out-Null"
 subprocess.run(['powershell','-NoProfile','-Command',command],check=True,capture_output=True)
 (target/'prepare.json').write_text(json.dumps(dict(status='prepared_not_built',project=str(project),source_files=files,source_manifest_sha256=sha(m),reason=reason),indent=2)+'\n',encoding='utf-8')
 print(json.dumps(dict(status='prepared',revision=revision,files=len(files))))
if __name__=='__main__':main()
