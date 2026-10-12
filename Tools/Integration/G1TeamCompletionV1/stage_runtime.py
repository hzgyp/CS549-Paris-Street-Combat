"""Stage independent Game/text; link only immutable cooked parent bytes."""
import argparse,json,shutil,os
from prepare import ROOT,OUT,SOURCE,sha,load
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--revision',required=True);a=ap.parse_args();assert a.revision in {'candidate_v1','candidate_v2','candidate_v3','candidate_v4','candidate_v5','candidate_v6','candidate_v7','candidate_v8','candidate_v9'}
    frozen=load(OUT/'freeze.json');build=load(OUT/a.revision/'build.json');assert build['exit_code']==0
    parent=ROOT/frozen['parent']['playable_directory'];target=ROOT/('tmp/Playtest-G1-Completion-'+a.revision+'-20261010');assert not target.exists()
    inner='Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe';assert sha(parent/inner)==frozen['p1_game_sha256'];target.mkdir()
    for p in parent.rglob('*'):
        if not p.is_file():continue
        rel=p.relative_to(parent);dst=target/rel;dst.parent.mkdir(parents=True,exist_ok=True)
        if rel.as_posix()==inner:continue
        if p.suffix.lower() in {'.cmd','.ps1','.md','.txt','.json','.ini','.log'}:shutil.copyfile(p,dst)
        else:os.link(p,dst)
    src=OUT/a.revision/'Project/Binaries/Win64/WW2FranceLiberation.exe';assert sha(src)==build['game_sha256'];shutil.copyfile(src,target/inner)
    p=target/'PLAY_G1_REVISION.cmd';s=p.read_text(encoding='utf-8-sig');assert s.count('G1TeamP1v920261010')==1
    user='G1Completion'+a.revision.replace('candidate_','')+'20261010';p.write_text(s.replace('G1TeamP1v920261010',user),encoding='utf-8')
    r=dict(status='staged_unverified',revision=a.revision,path=str(target),game_sha256=sha(target/inner),source_manifest_sha256=sha(SOURCE.parent/'SOURCE_MANIFEST.json'),user_directory=user)
    if (OUT/'RUNTIME.json').exists():shutil.copyfile(OUT/'RUNTIME.json',OUT/(a.revision+'_previous_runtime.json'))
    (OUT/'RUNTIME.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps(r))
if __name__=='__main__':main()
