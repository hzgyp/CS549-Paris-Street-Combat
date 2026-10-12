"""Freeze a bounded cache-only retirement; never traverse Content junctions."""
import hashlib, json, os, shutil, subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'tmp/storage-cleanup-20261011'
KEEP = {'candidate_death_v6', 'candidate_full_v8', 'candidate_full_v16'}
META = {'.json','.xml','.ini','.txt','.log','.rsp','.response','.manifest','.cpp','.h','.cs','.ubt','.uhtmanifest'}
CACHE_SUFFIXES = META | {'.sarif','.obj','.old','.bin','.pch','.res','.deps','.uhtpath','.uhtsettings','.uhttimestamps','.dll','.pdb','.rc2','.exp','.lib'}
HASHES = {}
def read(p): return json.loads(p.read_text('utf-8-sig'))
def sha(p):
    s=p.stat();key=(str(p),s.st_size,s.st_mtime_ns)
    if key not in HASHES:
        with p.open('rb') as f: HASHES[key]=hashlib.file_digest(f,'sha256').hexdigest()
    return HASHES[key]
def write(p,o): p.write_text(json.dumps(o,indent=2,ensure_ascii=False)+'\n','utf-8')
def safe(p):
    p=Path(os.path.abspath(p)); assert p.is_relative_to(ROOT) and p!=ROOT
    q=p
    while q!=ROOT:
        assert not (q.lstat().st_file_attributes & 0x400),str(q)
        q=q.parent
    return p
def files(p, external=False):
    if not p.exists(): return []
    result=[]; stack=[p if external else safe(p)]
    while stack:
        with os.scandir(stack.pop()) as es:
            for e in es:
                q=Path(e.path);s=q.lstat()
                assert not (s.st_file_attributes & 0x400),str(q)
                if e.is_dir(follow_symlinks=False):stack.append(q)
                else: result.append(q)
    return sorted(result)
def processes():
    command="Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'Unreal|WW2France|ShaderCompile|dotnet' } | Select-Object ProcessId,Name,CommandLine | ConvertTo-Json -Compress"
    r=subprocess.run(['powershell','-NoProfile','-Command',command],capture_output=True,text=True,check=True)
    result=json.loads(r.stdout) if r.stdout.strip() else []
    return result if isinstance(result,list) else [result]
def row(p):
    s=p.stat();return dict(path=str(p),size_bytes=s.st_size,mtime_ns=s.st_mtime_ns,sha256=sha(p))
def main():
    assert not (OUT/'PLAN.json').exists(),'Keep occupied audit'
    proc=processes(); projects=[]
    lane=ROOT/'tmp/g1-tactical-equipment-20261010'
    for p in sorted(lane.glob('candidate_*/Project')):
        if p.parent.name not in KEEP:projects.append(p)
    for n in [1,2]:projects.append(ROOT/f'tmp/g1-demo-draft03-20261009/recording_v{n}/Project')
    targets=[]; inventory=[]; metadata=[]
    for project in projects:
        assert project.exists()
        assert not any(str(project).lower() in (r.get('CommandLine') or '').lower().replace('/','\\') for r in proc),str(project)
        options=[project/'Intermediate/Build']+[p/'Intermediate/Build' for p in (project/'Plugins').iterdir() if p.is_dir()]
        for target in options:
            if not target.exists():continue
            safe(target);total=0;count=0
            for p in files(target):
                s=p.stat();rel=p.relative_to(ROOT).as_posix()
                assert p.suffix.lower() in CACHE_SUFFIXES, 'Unknown build file category: '+rel
                inventory.append(dict(path=rel,size_bytes=s.st_size,mtime_ns=s.st_mtime_ns))
                total+=s.st_size;count+=1
                if p.suffix.lower() in META:
                    assert s.st_size<=8*1024*1024,rel
                    dst=OUT/'BuildMetadata'/rel;dst.parent.mkdir(parents=True,exist_ok=True)
                    shutil.copyfile(p,dst);assert sha(p)==sha(dst)
                    metadata.append(dict(source=rel,backup=dst.relative_to(ROOT).as_posix(),size_bytes=s.st_size,sha256=sha(dst)))
            targets.append(dict(path=target.relative_to(ROOT).as_posix(),project=project.relative_to(ROOT).as_posix(),files=count,bytes=total))
    protected={}
    print('Cache inventory and diagnostic backups ready; freezing protected bytes',flush=True)
    def add(p):
        assert p.is_file(),str(p)
        protected[str(p)]=row(p)
    # Entire latest trial, immutable source and authoring source only (no junction).
    current=read(ROOT/'Docs/Development/CURRENT_PLAYER_DEATH_REVIEW.json')
    delivery=read(ROOT/'tmp/g1-player-death-20261011/DELIVERY_20261011.json')
    assert current['game_sha256']=='290b51b5648c73261e119edbef8d0f7fbb2e9088de4126262afc8cb92988ea21'
    assert sha(ROOT/current['source_manifest'])==current['source_manifest_sha256']
    manifest=read(ROOT/current['source_manifest'])
    assert len(manifest['files'])==73
    for r in manifest['files']:
        for base in [current['source_snapshot'],current['active_authoring_project']]:
            p=ROOT/base/r['path'];assert sha(p)==r['sha256'];add(p)
    trial=files(ROOT/current['playable_directory']);assert len(trial)==92
    expected={r['path']:r for r in delivery['normal_files']}
    assert len(expected)==92
    for p in trial:
        rel=p.relative_to(ROOT/current['playable_directory']).as_posix()
        assert sha(p)==expected[rel]['sha256'],rel
        add(p)
    print('Latest 73-source / 92-playable files exact',flush=True)
    add(ROOT/current['source_manifest'])
    formal=read(ROOT/'Docs/Development/CURRENT_DEVELOPMENT_BASELINE.json')
    for p in files(ROOT/formal['source_snapshot']):add(p)
    add(ROOT/formal['source_manifest'])
    inner='Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe'
    for c in [current,formal]:
        p=ROOT/c['playable_directory']/inner;assert sha(p)==c['game_sha256'];add(p)
    # Original and current user data, native assets, compact failures and receipts.
    for p in files(Path(os.environ['LOCALAPPDATA'])/'ParisStreetCombat', external=True):add(p)
    print('Formal baseline and all local user saves frozen',flush=True)
    original=read(lane/'freeze.json')
    for r in original['protected_native']:
        p=ROOT/r['path'];assert sha(p)==r['sha256'];add(p)
    for root in [ROOT/'Failures',ROOT/'Docs/Images/MissionLoopV1']:
        for p in files(root):add(p)
    for c in delivery['checks']:
        p=ROOT/c['result'];assert sha(p)==c['result_sha256'];add(p)
    for base in [ROOT/'tmp/g1-player-death-20261011',ROOT/'tmp/g1-field-manual-ui-20261011',ROOT/'tmp/g1-combat-ui-20261011']:
        for p in files(base):add(p)
    # Keep compiled source and all original build/run receipts at every retired project.
    for project in projects:
        for p in files(project.parent/'compiled-source-game'):add(p)
        for p in project.parent.iterdir():
            if p.is_file():add(p)
    for p in [ROOT/'AGENTS.md',ROOT/'HANDOFF.md',ROOT/'Assets/Sync/CATALOG.json',ROOT/'PLAY_CURRENT_G1.cmd']:
        add(p)
    write(OUT/'INVENTORY.json',inventory);write(OUT/'PROTECTED.json',list(protected.values()));write(OUT/'METADATA.json',metadata)
    plan=dict(status='prepared',prepared_at=datetime.now().astimezone().isoformat(),targets=targets,initial_processes=proc,retained_candidates=sorted(KEEP),disk_free_before=shutil.disk_usage(ROOT).free,logical_bytes=sum(r['bytes'] for r in targets),files=len(inventory),metadata_files=len(metadata),protected_files=len(protected),receipts={n:sha(OUT/n) for n in ['INVENTORY.json','PROTECTED.json','METADATA.json']})
    write(OUT/'PLAN.json',plan)
    print(json.dumps({k:plan[k] for k in ['status','logical_bytes','files','metadata_files','protected_files','disk_free_before']},indent=2));print('targets',len(targets))
if __name__=='__main__':main()
