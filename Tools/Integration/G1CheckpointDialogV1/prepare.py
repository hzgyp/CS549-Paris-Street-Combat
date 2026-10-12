"""Freeze reviewed unified v9; build independent non-reflected checkpoint UI."""
from pathlib import Path
import hashlib,json,shutil,subprocess
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'tmp/g1-checkpoint-dialog-20261010'
SOURCE=ROOT/'Unreal/Variants/G1CheckpointDialog20261010/Project'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def rows(base):
    return [dict(path=p.relative_to(base).as_posix(),size_bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(base.rglob('*')) if p.is_file()]
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def main():
    assert not OUT.exists() and not SOURCE.exists(),'Preserve occupied attempt'
    p=load(ROOT/'Docs/Development/CURRENT_TEAM_FEEDBACK_REVIEW.json')
    assert p['review_id']=='g1-team-feedback-completion-v9-20261010'
    manifest=ROOT/p['source_manifest'];assert sha(manifest)==p['source_manifest_sha256']
    parent=ROOT/p['source_snapshot'];files=load(manifest)['files'];assert rows(parent)==files and len(files)==52
    game=ROOT/p['playable_directory']/'Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe';assert sha(game)==p['game_sha256']
    old=load(ROOT/'tmp/g1-team-completion-20261010/freeze.json')
    for r in old['prior_freeze']['selected_parent_freeze']['protected_native']:assert sha(ROOT/r['path'])==r['sha256'],r['path']
    OUT.mkdir(parents=True);shutil.copytree(parent,SOURCE)
    user=Path.home()/'AppData/Local/ParisStreetCombat/G1Completionv920261010'
    (OUT/'freeze.json').write_text(json.dumps(dict(parent=p,parent_files=files,parent_game=str(game),parent_game_sha256=sha(game),parent_user_root=str(user),parent_user_files=rows(user),prior_freeze=old),indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status='parent_frozen',files=52,native_guards=1754)))
def author(revision,previous=None,reason=''):
    target=OUT/revision;assert not target.exists();files=rows(SOURCE)
    m=SOURCE.parent/'SOURCE_MANIFEST.json'
    if m.exists():shutil.copyfile(m,OUT/(revision+'_previous_manifest.json'))
    m.write_text(json.dumps(dict(format='paris-source-snapshot-v1',scope='Checkpoint dialog child; original cooked schema/assets/transaction preserved',files=files),indent=2)+'\n',encoding='utf-8')
    project=target/'Project';shutil.copytree(SOURCE,project)
    old=OUT/previous/'Project' if previous else ROOT/'tmp/g1-team-completion-20261010/candidate_v9/Project'
    for name in ['Binaries','Intermediate']:shutil.copytree(old/name,project/name)
    command="New-Item -ItemType Junction -Path '"+str(project/'Content').replace("'","''")+"' -Value '"+str(ROOT/'Unreal/ParisStreetCombat/Content').replace("'","''")+"' | Out-Null"
    subprocess.run(['powershell','-NoProfile','-Command',command],check=True)
    (target/'prepare.json').write_text(json.dumps(dict(status='prepared_not_built',project=str(project),source_files=files,source_manifest_sha256=sha(m),reason=reason),indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status='prepared',revision=revision,source_files=len(files))))
if __name__=='__main__':main()
