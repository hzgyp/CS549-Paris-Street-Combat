"""Publish only the bounded release changes through an isolated worktree."""
from release import *
import ast
TREE=OUT/'git-publication'
BRANCH='codex/tutorial-v1-20261017'
def git(*args,cwd=ROOT):return subprocess.check_output(['git','-C',str(cwd),*args],stderr=subprocess.STDOUT)
def prepare():
 assert read(OUT/'ADOPTION.json')['status']=='formal_tutorial_v1_selected'
 assert not git('diff','--cached','--name-only').strip(),'Preserve existing index'
 parent=git('rev-parse','origin/main').decode().strip()
 if TREE.exists():
  assert not (OUT/'GIT_STAGED.json').exists(),'Preserve an already staged release'
  assert git('rev-parse','HEAD',cwd=TREE).decode().strip()==parent
  assert git('branch','--show-current',cwd=TREE).decode().strip()==BRANCH
  assert not git('diff','--cached','--name-only',cwd=TREE).strip()
 else:git('worktree','add','-b',BRANCH,str(TREE),'origin/main')
 paths=[]
 def copy(rel):
  p=ROOT/rel;q=TREE/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);paths.append(rel)
 prefix=SOURCE.relative_to(ROOT).as_posix()
 for r in read(SOURCE/'SOURCE_MANIFEST.json')['files']:
  if r['path']!=CURVE:copy(prefix+'/Project/'+r['path'])
 exact=[prefix+'/SOURCE_MANIFEST.json','Assets/Sync/CATALOG.json','Assets/Sync/TUTORIAL_SOURCE_CONTRACT_20261017.json','Docs/Development/CURRENT_DEVELOPMENT_BASELINE.json','Docs/Development/CURRENT_DEVELOPMENT_BASELINE.md','Docs/Development/CURRENT_DEVELOPMENT_BASELINE_ZH.md','Docs/Development/CURRENT_TUTORIAL_RELEASE.json','Docs/Development/CURRENT_TUTORIAL_SOURCE_PENDING.json','Docs/Development/CURRENT_MEDICAL_GUIDANCE_MUSIC_PLAYTEST_REVIEW.json','Docs/Development/MissionLoopV1/TUTORIAL_V1_RELEASE_IMPLEMENTATION_20261017.md','Docs/Development/MissionLoopV1/TUTORIAL_V1_RELEASE_RESULT_20261017.md','Docs/Development/MissionLoopV1/TUTORIAL_V1_RELEASE_RESULT_20261017_ZH.md','Docs/Development/MissionLoopV1/MEDICAL_GUIDANCE_MUSIC_PLAYTEST_IMPLEMENTATION_20261017.md','Docs/Development/MissionLoopV1/MEDICAL_GUIDANCE_MUSIC_PLAYTEST_RESULT_20261017.md','Docs/Development/MissionLoopV1/MEDICAL_GUIDANCE_MUSIC_PLAYTEST_RESULT_20261017_ZH.md','PLAY_CURRENT_G1.cmd','HANDOFF_CURRENT.md']
 exact += [x['path'] for x in read(ROOT/'Assets/Sync/CATALOG.json')['active_manifests']]
 exact += [x.relative_to(ROOT).as_posix() for x in files(PROOF)]
 exact += [x.relative_to(ROOT).as_posix() for x in files(Path(__file__).parent) if x.suffix in {'.py','.ps1'}]
 for rel in sorted(set(exact)):copy(rel)
 # Publish this lane's handoff without sweeping other chats' uncommitted routing.
 check=subprocess.run(['git','-C',str(ROOT),'show',parent+':HANDOFF_CURRENT.md'],capture_output=True)
 previous_handoff=check.stdout.decode('utf-8-sig') if check.returncode==0 else ''
 (TREE/'HANDOFF_CURRENT.md').write_text('# Current formal tutorial1.0\n\n17 October2026. CURRENT_DEVELOPMENT_BASELINE.json and CURRENT_TUTORIAL_RELEASE.json select the unchanged human-reviewed source145/Game3bb90f64. PLAY_CURRENT_G1.cmd routes the formal tutorial. Read Docs/Development/MissionLoopV1/TUTORIAL_V1_RELEASE_RESULT_20261017.md and Assets/Sync/TUTORIAL_SOURCE_CONTRACT_20261017.json. Previous formal86 remains preserved. Continue from CURRENT_TUTORIAL_SOURCE_PENDING.json; reconcile action/gameplay edits and build only on explicit human request. This supersedes only older formal/current-tutorial routing below. Other lane records are preserved as inherited, not newly accepted. Development Git/SFTP only; coursework delivery remains human-only.\n\n'+previous_handoff,'utf-8')
 # The local platform has separate unfinished changes. Change only the existing
 # public formal selector's title; do not sweep the local registry/gameplay tree.
 regpath='Assets/Registry/registry.json';reg=read(TREE/regpath)
 next(x for x in reg['selectors'] if x['id']=='formal')['title']='教学阶段正式版1.0'
 write(TREE/regpath,reg);paths.append(regpath)
 attr='\n# Byte-exact tutorial1.0 source and verification metadata.\nUnreal/Variants/G1MedicalGuidanceMusic20261017/** -text whitespace=cr-at-eol,-blank-at-eof\nAssets/Sync/TUTORIAL_SOURCE_CONTRACT_20261017.json -text\nDocs/Development/TutorialReleaseV1/** -text\nDocs/Development/CURRENT_TUTORIAL_RELEASE.json -text\nDocs/Development/CURRENT_TUTORIAL_SOURCE_PENDING.json -text\nDocs/Development/CURRENT_MEDICAL_GUIDANCE_MUSIC_PLAYTEST_REVIEW.json -text\n'
 ignore='\n# Generated formal tutorial packages and licensed animation samples stay outside Git.\n/Releases/\n/Unreal/Variants/G1MedicalGuidanceMusic20261017/Project/'+CURVE+'\n'
 for rel,note in [('.gitattributes',attr),('.gitignore',ignore)]:
  for base in [ROOT,TREE]:
   p=base/rel;s=p.read_text('utf-8-sig')
   if note.splitlines()[1] not in s:p.write_text(s+note,'utf-8')
  paths.append(rel)
 note='<!-- tutorial-v1-development-release-20261017 -->\nCurrent formal tutorial1.0: [release guide](Docs/Development/MissionLoopV1/TUTORIAL_V1_RELEASE_RESULT_20261017.md), [selector](Docs/Development/CURRENT_TUTORIAL_RELEASE.json). Source145/Game3bb90f64; human-accepted medical guidance/music. This source clone requires private external resources; no coursework delivery.\n\n'
 for base in [ROOT,TREE]:
  p=base/'README.md';s=p.read_text('utf-8-sig')
  if 'tutorial-v1-development-release-20261017' not in s:p.write_text(note+s,'utf-8')
 paths.append('README.md')
 policy='<!-- tutorial-v1-routing-20261017 -->\nThe human has adopted tutorial1.0: CURRENT_DEVELOPMENT_BASELINE.json and CURRENT_TUTORIAL_RELEASE.json select145-source/Game3bb90f64. PLAY_CURRENT_G1.cmd now selects that formal tutorial. Previous formal86 remains preserved. This supersedes only older current-baseline routing. Use the latest combined pending source, reconcile action/gameplay chats and build only on explicit human request. All coursework delivery remains human-only.\n\n'
 for base in [ROOT,TREE]:
  p=base/'AGENTS.md';s=p.read_text('utf-8-sig')
  if base==TREE and len((policy+s).encode('utf-8'))>=16*1024:
   prior=git('show',parent+':AGENTS.md');archive='Docs/Development/InstructionHistory/AGENTS_PUBLIC_PRE_TUTORIAL_V1_20261017.txt'
   for destination in [ROOT,TREE]:
    a=destination/archive;a.parent.mkdir(parents=True,exist_ok=True)
    if a.exists():assert a.read_bytes()==prior
    else:a.write_bytes(prior)
   paths.append(archive)
   s=('# Paris Street Combat — bounded public entry\n\nRead HANDOFF_CURRENT.md, then the selector/result for the requested lane. The previous public AGENTS is preserved byte-for-byte at `'+archive+'`, SHA256 `'+hashlib.sha256(prior).hexdigest()+'`. Its clauses keep their existing authority except the exact later routing above. Read only relevant historical paragraphs; this reorganization grants no cleanup, publication, adoption or restart authority.\n\n'
      'All coursework uploads/submissions/attachments/pre-staging are human-only, every course and platform. Broad finish/publish/Git requests do not revoke that prohibition. Explicit development-only collaboration is separate; never modify existing teacher/course artifacts through it.\n\n'
      'Preserve actual human saves/settings, immutable source/native/vendor originals, failure/raw evidence, old releases and unrelated unfinished edits. Build/playtest only on explicit human request. Continue from CURRENT_TUTORIAL_SOURCE_PENDING.json, reconcile both action/gameplay change lists and use one writer per shared byte set. A source clone requires private Catalog resources; licensed native curves stay outside Git. Never enter a cached Editor without a matching build and dependency audit. No force-push, broad cleanup or takeover of another engine/session.\n\n'
      'Plan a work package before editing; read relevant failures and retain evidence/rollback. Matching compile/static/skeleton checks do not establish runtime/render/human acceptance. Keep this entry under16KiB and use small previews instead of full image batches. Current tutorial1.0 adoption does not accept unfinished NPC algorithms/map survey, all-map/stress/Editor/PIE or second-machine work.\n')
  if 'tutorial-v1-routing-20261017' not in s:p.write_text(policy+s,'utf-8')
  assert p.stat().st_size<16*1024,'Keep bounded AGENTS entry under16KiB'
 paths.append('AGENTS.md')
 archive='Docs/Development/InstructionHistory/AGENTS_PUBLIC_PRE_TUTORIAL_V1_20261017.txt'
 if (TREE/archive).exists():
  assert (TREE/archive).read_bytes()==git('show',parent+':AGENTS.md')
  paths.append(archive)
 # Preserve the archived original and pinned CRLF metadata; the accepted probe
 # contains one existing space-only line whose bytes must stay frozen.
 exact_attributes='\n# Preserve frozen tutorial metadata and archived public instructions.\nAssets/Sync/TUTORIAL_SOURCE_CONTRACT_20261017.json -text whitespace=cr-at-eol\nDocs/Development/TutorialReleaseV1/** -text whitespace=cr-at-eol\nDocs/Development/CURRENT_TUTORIAL_RELEASE.json -text whitespace=cr-at-eol\nDocs/Development/CURRENT_TUTORIAL_SOURCE_PENDING.json -text whitespace=cr-at-eol\nDocs/Development/CURRENT_MEDICAL_GUIDANCE_MUSIC_PLAYTEST_REVIEW.json -text whitespace=cr-at-eol\nDocs/Development/InstructionHistory/AGENTS_PUBLIC_PRE_TUTORIAL_V1_20261017.txt -text whitespace=cr-at-eol,-blank-at-eof\nUnreal/Variants/G1MedicalGuidanceMusic20261017/Project/Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/ParisProneTransitionProbe.inl whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol\n'
 for base in [ROOT,TREE]:
  p=base/'.gitattributes';s=p.read_text('utf-8-sig')
  if 'Preserve frozen tutorial metadata and archived public instructions.' not in s:p.write_text(s+exact_attributes,'utf-8')
 p=TREE/'HANDOFF_CURRENT.md';p.write_text(p.read_text('utf-8').rstrip()+'\n','utf-8')
 source_contract=read(ROOT/'Assets/Sync/TUTORIAL_SOURCE_CONTRACT_20261017.json')
 guide=TREE/prefix/'RESTORE.md';guide.write_text('Tutorial1.0 has145 byte-pinned source files;144 are public here. Restore the licensed ParisProneNativeCurves.inl from the private runtime manifest or Matching-Source-145.zip before compiling. Use Assets/Sync/TUTORIAL_SOURCE_CONTRACT_20261017.json for exact hashes and restore_path mappings. Restore Catalog-selected city/native dependencies, overlay the tutorial-native manifest, and copy Audio/Equipment/UI from the extracted private release to the new source project. Never use old Editor binaries; build a matching UE5.8.2 Editor and validate dependencies before entry. The packaged Game is independently ready to run; second-machine source restoration/play remains pending.\n','utf-8');paths.append(prefix+'/RESTORE.md');shutil.copyfile(guide,SOURCE/'RESTORE.md')
 # Selected source/metadata only: no personal saves, images, raw licensed data,
 # binaries, historical coursework files, credentials or unrelated platform edits.
 forbidden={'.sav','.uasset','.umap','.wav','.zip','.png','.jpg','.ttf','.exe','.dll','.pdb','.pdf','.docx','.mp4','.fbx','.blend'}
 secret=read(ROOT/'Assets/LocalWorking/AssetWorkbench/runtime/session.json')['token'].encode()
 for rel in set(paths):
  p=TREE/rel;raw=p.read_bytes();assert p.suffix.lower() not in forbidden and len(raw)<25*1024*1024
  private_header=b'-----BEGIN '+b'OPENSSH PRIVATE KEY-----'
  assert secret not in raw and private_header not in raw
  if p.suffix=='.py':ast.parse(raw.decode('utf-8-sig'))
  if p.suffix=='.json':json.loads(raw.decode('utf-8-sig'))
 assert not (TREE/prefix/'Project'/CURVE).exists()
 selected_paths=sorted(set(paths))
 for i in range(0,len(selected_paths),40):git('add','--',*selected_paths[i:i+40],cwd=TREE)
 staged=git('diff','--cached','--name-only','-z',cwd=TREE).decode().split('\0');staged=sorted(x for x in staged if x)
 assert all(p in set(paths) for p in staged)
 for r in read(SOURCE/'SOURCE_MANIFEST.json')['files']:
  if r['path']==CURVE:continue
  raw=git('show',':'+prefix+'/Project/'+r['path'],cwd=TREE);assert len(raw)==r['size_bytes'] and hashlib.sha256(raw).hexdigest()==r['sha256'],r['path']
 assert git('show',':'+archive,cwd=TREE)==git('show',parent+':AGENTS.md')
 proof=dict(status='pass_bounded_staged_release_no_credentials_or_asset_bytes',worktree=str(TREE),branch=BRANCH,parent=parent,files=staged,public_source_files=144,private_source_files=[CURVE],root_worktree_head_unchanged=git('rev-parse','HEAD').decode().strip(),root_index_untouched=not git('diff','--cached','--name-only').strip())
 write(OUT/'GIT_STAGED.json',proof);print(dict(status=proof['status'],staged=len(staged),public_source_files=144),flush=True)
def push():
 p=read(OUT/'GIT_STAGED.json');assert p['status'].startswith('pass_')
 diff=subprocess.run(['git','-C',str(TREE),'diff','--cached','--check'],text=True,capture_output=True);(OUT/'git-diff-check-final.log').write_text(diff.stdout+diff.stderr,'utf-8');assert diff.returncode==0,'Read the bounded diff-check log before publishing'
 check=subprocess.run([sys.executable,str(TREE/'Tools/check_asset_storage.py'),'--staged'],cwd=TREE,text=True,capture_output=True);(OUT/'git-storage-staged.log').write_text(check.stdout+check.stderr,'utf-8');assert check.returncode==0,'Read private staged storage-check log'
 # No force push or history rewrite. The remote must still match the frozen parent.
 remote=git('ls-remote','origin','refs/heads/main',cwd=TREE).decode().split()[0];assert remote==p['parent'],'Preserve intervening remote work'
 git('commit','-m','Release tutorial 1.0 with accepted medical guidance and contextual music',cwd=TREE)
 commit=git('rev-parse','HEAD',cwd=TREE).decode().strip()
 check=subprocess.run([sys.executable,str(TREE/'Tools/check_asset_storage.py'),'--git','--publish-ref',commit],cwd=TREE,text=True,capture_output=True);(OUT/'git-storage-ancestry.log').write_text(check.stdout+check.stderr,'utf-8');assert check.returncode==0,'Read private ancestry storage-check log'
 output=git('push','origin','HEAD:main',cwd=TREE);(OUT/'git-push.log').write_bytes(output)
 remote=git('ls-remote','origin','refs/heads/main',cwd=TREE).decode().split()[0];assert remote==commit
 write(OUT/'GIT_PUBLICATION.json',dict(status='fast_forward_push_and_remote_head_verified',commit=commit,remote_head=remote,branch='main',working_branch=BRANCH,worktree=str(TREE),root_head_unchanged=True,root_index_untouched=not git('diff','--cached','--name-only').strip(),public_source_files=144,private_source_files=1,coursework_delivery=False))
 print(dict(status='git_main_published_and_verified',commit=commit),flush=True)
if __name__=='__main__':globals()[sys.argv[1]]()
