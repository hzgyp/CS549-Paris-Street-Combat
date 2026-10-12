"""Stage new Game and ordinary entry; only hardlink immutable cooked bytes."""
import argparse,shutil,os,json
from prepare import ROOT,OUT,SOURCE,load,sha
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--revision',default='candidate_v1');a=ap.parse_args()
 f=load(OUT/'freeze.json');build=load(OUT/a.revision/'build.json');assert build['exit_code']==0
 parent=ROOT/f['parent']['playable_directory'];target=ROOT/('tmp/Playtest-G1-EnemyClear-'+a.revision+'-20261010');assert not target.exists()
 inner='Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe';assert sha(parent/inner)==f['parent_game_sha256'];target.mkdir()
 for p in parent.rglob('*'):
  if not p.is_file():continue
  rel=p.relative_to(parent)
  if rel.as_posix()==inner or p.name in {'PLAY_CHECKPOINT_REVIEW.cmd','README_CHECKPOINT_QUICK_REVIEW.md'}:continue
  dst=target/rel;dst.parent.mkdir(parents=True,exist_ok=True)
  if p.suffix.lower() in {'.cmd','.ps1','.md','.txt','.json','.ini','.log'}:shutil.copyfile(p,dst)
  else:os.link(p,dst)
 src=OUT/a.revision/'Project/Binaries/Win64/WW2FranceLiberation.exe';assert sha(src)==build['game_sha256'];shutil.copyfile(src,target/inner)
 p=target/'PLAY_G1_REVISION.cmd';text=p.read_text(encoding='utf-8-sig');old='G1Checkpointv320261010';assert text.count(old)==1
 user='G1EnemyClear'+a.revision.replace('candidate_','')+'20261010';p.write_text(text.replace(old,user),encoding='utf-8')
 assert not any(k in text for k in ['ParisInteractionProbe','ParisUXTest','ParisAVAuditOut','ParisDemo'])
 for name in ['INTERACTION_REVIEW.md','README_CHECKPOINT_REVIEW.md','README_P1.md','README_TEAM_FEEDBACK.md']:
  note=target/name
  if note.exists():note.write_text('Latest checkpoint rule: eliminate all registered G1 enemies, then enter the gold circle and press E.\nFar-bank marker, squad arrival, posture and movement are no longer save gates.\nSee README_CHECKPOINT_RULE.md for the latest rule; the inherited notes below describe earlier revisions.\n\n'+note.read_text(encoding='utf-8-sig'),encoding='utf-8')
 r=dict(status='staged_unverified',revision=a.revision,path=str(target),game_sha256=sha(target/inner),source_manifest_sha256=sha(SOURCE.parent/'SOURCE_MANIFEST.json'),user_directory=user)
 if (OUT/'RUNTIME.json').exists():shutil.copyfile(OUT/'RUNTIME.json',OUT/(a.revision+'_previous_runtime.json'))
 (OUT/'RUNTIME.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps(r))
if __name__=='__main__':main()
