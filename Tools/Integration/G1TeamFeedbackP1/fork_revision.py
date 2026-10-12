"""Preserve previous attempt and fork updated source/build caches into a new identity."""
import argparse,json,shutil,subprocess
from prepare import ROOT,OUT,SOURCE,rows,sha

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--from-revision',required=True);ap.add_argument('--revision',required=True);ap.add_argument('--reason',required=True);args=ap.parse_args()
    assert args.revision in {'candidate_v2','candidate_v3','candidate_v4','candidate_v5','candidate_v6','candidate_v7','candidate_v8','candidate_v9'}
    old=OUT/args.from_revision;new=OUT/args.revision;assert not new.exists()
    previous=json.loads((old/'build.json').read_text('utf-8-sig'));assert previous['status']!='building'
    files=rows(SOURCE);assert len(files)==48
    old_manifest=SOURCE.parent/'SOURCE_MANIFEST.json';shutil.copyfile(old_manifest,old/'source_manifest_before_revision.json')
    old_manifest.write_text(json.dumps(dict(format='paris-source-snapshot-v1',scope='Unselected P1 review candidate',files=files),indent=2)+'\n','utf-8')
    project=new/'Project';shutil.copytree(SOURCE,project)
    for name in ['Binaries','Intermediate']:shutil.copytree(old/'Project'/name,project/name)
    command="New-Item -ItemType Junction -Path '"+str(project/'Content').replace("'","''")+"' -Value '"+str(ROOT/'Unreal/ParisStreetCombat/Content').replace("'","''")+"' | Out-Null"
    subprocess.run(['powershell','-NoProfile','-Command',command],check=True)
    (new/'prepare.json').write_text(json.dumps(dict(status='prepared_not_built',project=str(project),source_files=files,source_manifest_sha256=sha(old_manifest),previous_identity=args.from_revision,reason=args.reason),indent=2)+'\n','utf-8')
    print(json.dumps(dict(status='prepared_new_identity',revision=args.revision,reason=args.reason)))

if __name__=='__main__':main()
