"""Publish only the retirement and teammate handoff; preserve the main worktree."""
from manage import *
import ast
TREE=OUT/'git-publication'
BRANCH='codex/tutorial-sftp-retirement-20261017'
def git(*args,cwd=ROOT):return subprocess.check_output(['git','-C',str(cwd),*args],stderr=subprocess.STDOUT)

def prepare():
 assert read(OUT/'VERIFIED.json')['local_user_manifest_hashes_after_exact']
 assert not git('diff','--cached','--name-only').strip()
 git('fetch','origin','main');parent=git('rev-parse','origin/main').decode().strip()
 assert not TREE.exists();git('worktree','add','-b',BRANCH,str(TREE),'origin/main')
 assert read(TREE/'Assets/Sync/CATALOG.json')==read(OUT/'FREEZE.json')['catalog'],'Reconcile intervening or unrelated Catalog work'
 paths=['Assets/Sync/CATALOG.json','Assets/Sync/retired/PACKAGED_PLAYTEST_RETIREMENT_20261017.json',
  'Docs/Development/MissionLoopV1/TUTORIAL_SFTP_RETIREMENT_IMPLEMENTATION_20261017.md',
  'Docs/Development/MissionLoopV1/TUTORIAL_SFTP_RETIREMENT_RESULT_20261017.md',
  'Docs/Development/MissionLoopV1/TUTORIAL_SFTP_RETIREMENT_RESULT_20261017_ZH.md']
 paths += [p.relative_to(ROOT).as_posix() for p in PROOF.iterdir() if p.is_file()]
 paths += [p.relative_to(ROOT).as_posix() for p in Path(__file__).parent.iterdir() if p.suffix=='.py']
 for rel in paths:
  p=TREE/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/rel,p)
 guide='Docs/Development/TutorialSftpRetirementV1/DOWNLOAD_README_ZH.md'
 note='<!-- tutorial-current-teammate-package-20261017 -->\nCurrent teammate playtest: `/releases/paris-tutorial-20261017-v1/Paris-Tutorial-1.0-20261017.zip` (8,266,799,598 bytes). Extract all and run `PLAY_TUTORIAL.cmd`. [Bilingual download instructions]('+guide+'). Superseded11October development ZIP is retired; teacher AudioV2 and native/source resources remain preserved.\n\n'
 for rel in ['README.md','Assets/TEAM_SYNC_WORKFLOW.md']:
  for base in [ROOT,TREE]:
   p=base/rel;s=p.read_text('utf-8-sig');local_note=note.replace(']('+guide,']('+('../'+guide if rel.startswith('Assets/') else guide))
   if 'tutorial-current-teammate-package-20261017' not in s:p.write_text(local_note+s,'utf-8',newline='\n')
  paths.append(rel)
 attr='\n# Dated SFTP retirement evidence and teammate handoff keep exact bytes.\nDocs/Development/TutorialSftpRetirementV1/** -text whitespace=cr-at-eol\nDocs/Development/MissionLoopV1/TUTORIAL_SFTP_RETIREMENT_*.md -text whitespace=cr-at-eol\n'
 for base in [ROOT,TREE]:
  p=base/'.gitattributes';s=p.read_text('utf-8-sig')
  if 'Dated SFTP retirement evidence' not in s:p.write_text(s+attr,'utf-8',newline='\n')
 paths.append('.gitattributes')
 token=read(ROOT/'Assets/LocalWorking/AssetWorkbench/runtime/session.json')['token'].encode()
 header=b'-----BEGIN '+b'OPENSSH PRIVATE KEY-----'
 for rel in paths:
  raw=(TREE/rel).read_bytes();assert token not in raw and header not in raw and b'\0' not in raw
  assert (TREE/rel).suffix.lower() not in {'.zip','.sav','.uasset','.pdf','.png','.wav','.exe'}
  if rel.endswith('.json'):json.loads(raw.decode('utf-8-sig'))
  if rel.endswith('.py'):ast.parse(raw.decode('utf-8-sig'))
 git('add','--',*paths,cwd=TREE)
 staged=sorted(x for x in git('diff','--cached','--name-only','-z',cwd=TREE).decode().split('\0') if x)
 assert set(staged)<=set(paths)
 for rel in [r['path'] for r in read(ROOT/'Assets/Sync/CATALOG.json')['active_manifests']]:
  assert git('show',':'+rel,cwd=TREE)==(ROOT/rel).read_bytes()
 check=subprocess.run(['git','-C',str(TREE),'diff','--cached','--check'],capture_output=True);(OUT/'git-diff-check.log').write_bytes(check.stdout+check.stderr);assert check.returncode==0
 write(OUT/'GIT_STAGED.json',dict(status='bounded_retirement_handoff_staged',parent=parent,files=staged,root_head=git('rev-parse','HEAD').decode().strip(),root_index_untouched=True))
 print(dict(status='bounded_retirement_handoff_staged',files=len(staged)),flush=True)

def push():
 p=read(OUT/'GIT_STAGED.json')
 check=subprocess.run([sys.executable,str(TREE/'Tools/check_asset_storage.py'),'--staged'],cwd=TREE,capture_output=True);(OUT/'git-staged-storage.log').write_bytes(check.stdout+check.stderr);assert check.returncode==0
 assert git('ls-remote','origin','refs/heads/main',cwd=TREE).decode().split()[0]==p['parent']
 git('commit','-m','Retire superseded SFTP playtest and document tutorial 1.0 teammate download',cwd=TREE)
 commit=git('rev-parse','HEAD',cwd=TREE).decode().strip()
 check=subprocess.run([sys.executable,str(TREE/'Tools/check_asset_storage.py'),'--git','--publish-ref',commit],cwd=TREE,capture_output=True);(OUT/'git-ancestry-storage.log').write_bytes(check.stdout+check.stderr);assert check.returncode==0
 output=git('push','origin','HEAD:main',cwd=TREE);(OUT/'git-push.log').write_bytes(output)
 assert git('ls-remote','origin','refs/heads/main',cwd=TREE).decode().split()[0]==commit
 assert not git('diff','--cached','--name-only').strip()
 write(OUT/'GIT_PUBLICATION.json',dict(status='fast_forward_push_remote_head_verified',commit=commit,parent=p['parent'],files=len(p['files']),root_head_preserved=git('rev-parse','HEAD').decode().strip()==p['root_head'],root_index_untouched=True,coursework_delivery=False))
 print(dict(status='fast_forward_push_remote_head_verified',commit=commit),flush=True)

if __name__=='__main__':globals()[sys.argv[1]]()
