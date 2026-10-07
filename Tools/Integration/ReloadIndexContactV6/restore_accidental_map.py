"""User-confirmed accidental save: backup/restore formal map only via selected SFTP bytes."""
import argparse,hashlib,importlib.util,json,os,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
OUT=STORE/'Evidence/ReloadIndexContactV6/map_recovery_v1'
assert not OUT.exists(),'Preserve occupied recovery'
spec=importlib.util.spec_from_file_location('restore',ROOT/'Tools/Integration/restore_native_playtest.py')
restore=importlib.util.module_from_spec(spec);spec.loader.exec_module(restore)
restore.idle();restore.STAGE=OUT
selected,rows=restore.entries()
path='Unreal/ParisStreetCombat/Content/ParisCombat/Maps/LV_ParisStreetCombat_V1.umap'
entry=next(r for r in rows if r['path']==path)
assert entry['sha256']=='2791b4a7f76b4b3d07f42286b6ad0156c3a185c2e3e795fa2446aaac0ad68519'
target=ROOT/path
assert restore.sha(target)=='de39b998d97cc992454db9dbd91b9f3b96bf304e2164a17375a170c9817a305a'
OUT.mkdir(parents=True);(OUT/'source.py').write_bytes(Path(__file__).read_bytes())
player=STORE/'Content/ParisCombat/Blueprints/PlayerActionsV1/BP_PCParisPlayerActionsV6.uasset'
assert restore.sha(player)=='572a0d9929ad65aa6fec0b206960524979314e1591eeaec27af2e75e8f22fbe8'
shutil.copy2(player,OUT/'AccidentalPlayerV6.uasset');assert restore.sha(OUT/'AccidentalPlayerV6.uasset')==restore.sha(player)
profile=Path(os.environ['USERPROFILE'])
args=argparse.Namespace(host='127.0.0.1',port=22222,user='cs549sftp',identity=str(profile/'.ssh/cs549_sftp_ed25519'),known_hosts=str(profile/'.ssh/known_hosts_cs549'),backup_conflicts=True)
restore.download(args,selected,[entry]);restore.apply(args,selected,[entry]);assert restore.same(target,entry)
current=json.loads((STORE/'Evidence/ReloadIndexContactV6/preflight_v1/result.json').read_text())['files']
changed=[]
for r in current:
    p=ROOT/r['path'];h=restore.sha(p)
    if h!=r['sha256']:
        assert r['path'].endswith('/Maps/LV_ParisStreetCombat_V1.umap') and h==entry['sha256']
        changed.append(r['path']);r.update(sha256=h,size_bytes=p.stat().st_size)
assert len(changed)==2
result={'scope':__doc__,'status':'formal_map_byte_exact_restored_accidental_version_backed_up',
 'files':current,'restored_alias_paths':changed,'player_v6_preserved_unselected':True,
 'remaining_old_guard_difference':'V6 accidental saved rate; original formal map does not use it',
 'sftp_verified_source':entry,'catalog_modified':False,'formal_trial_selection':False}
(OUT/'result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('files','sftp_verified_source')}))
