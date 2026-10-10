"""Freeze prior recording source, then stage a documented helper-only revision."""
import argparse, hashlib, json, shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'tmp/g1-demo-draft03-20261009'
def main():
    p=argparse.ArgumentParser();p.add_argument('--previous',required=True);p.add_argument('--revision',required=True);p.add_argument('--reason',required=True);a=p.parse_args()
    for s in [a.previous,a.revision]:assert s.startswith('recording_v') and s[11:].isdigit()
    plan=json.loads((OUT/(a.previous+'_prepare.json')).read_text('utf-8-sig'));project=Path(plan['project'])
    new=OUT/a.revision;assert not new.exists();new.mkdir()
    snap=OUT/a.previous/'compiled_source_snapshot';assert not snap.exists()
    for r in plan['recording_source_files']:
        f=project/r['path'];assert hashlib.sha256(f.read_bytes()).hexdigest()==r['sha256'];to=snap/r['path'];to.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,to)
    private=project/'Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/ParisDemoInput.cpp'
    shutil.copyfile(Path(__file__).parent/'ParisDemoInput.cpp',private)
    changed=[]
    for r in plan['recording_source_files']:
        f=project/r['path'];sha=hashlib.sha256(f.read_bytes()).hexdigest()
        if sha!=r['sha256']:changed.append(r['path'])
        r['sha256']=sha;r['bytes']=f.stat().st_size
    assert changed==['Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/ParisDemoInput.cpp'],changed
    plan['preflight_corrections'].append(a.reason);plan['retained_previous_source']=str(snap);plan['changed_from_previous']=changed
    (OUT/(a.revision+'_prepare.json')).write_text(json.dumps(plan,indent=2)+'\n','utf-8')
    print(json.dumps(dict(status='prepared_helper_only',revision=a.revision,changes=changed)),flush=True)
if __name__=='__main__':main()
