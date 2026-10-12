"""Final identity/protected-bytes/native-dialog evidence verification."""
from pathlib import Path
import json,re,math
from prepare import ROOT,OUT,SOURCE,rows,sha,load
import check_source
def main():
 check_source.main()
 f=load(OUT/'freeze.json');completion=f['prior_freeze'];p0=completion['prior_freeze'];selected=p0['selected_parent_freeze']
 for epoch in [completion,p0,selected]:assert rows(ROOT/epoch['parent']['source_snapshot'])==epoch['parent_files']
 for r in selected['protected_native']:assert sha(ROOT/r['path'])==r['sha256'],r['path']
 assert sha(ROOT/'Assets/Sync/CATALOG.json')==selected['catalog_sha256']
 for epoch,k,u,uf in [(completion,'p1','p1_user_root','p1_user_files'),(p0,'p0','p0_user_root','p0_user_files')]:
  assert sha(Path(epoch[k+'_game']))==epoch[k+'_game_sha256'];assert rows(Path(epoch[u]))==epoch[uf]
 assert sha(Path(selected['normal_game']))==selected['normal_game_sha256']
 assert rows(Path(selected['user_root']))==selected['user_files']
 runtime=load(OUT/'RUNTIME.json');manifest=load(SOURCE.parent/'SOURCE_MANIFEST.json');assert rows(SOURCE)==manifest['files'] and len(manifest['files'])==52
 prepared=load(OUT/runtime['revision']/'prepare.json');build=load(OUT/runtime['revision']/'build.json')
 for r in manifest['files']:assert sha(Path(prepared['project'])/r['path'])==r['sha256'],r['path']
 assert sha(SOURCE.parent/'SOURCE_MANIFEST.json')==runtime['source_manifest_sha256']==prepared['source_manifest_sha256']
 assert sha(Path(runtime['path'])/'Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe')==runtime['game_sha256']==build['game_sha256']
 launcher=(Path(runtime['path'])/'PLAY_G1_REVISION.cmd').read_text(encoding='utf-8-sig')
 assert runtime['user_directory'] in launcher and not any(x in launcher for x in ['ParisUXTest','ParisInteractionProbe','ParisAVAuditOut','ParisDemo','ParisSpaceSurveyOut'])
 results={}
 for identity in ['menu_v2','checkpoint_v2','restore_v2']:
  folder=OUT/'checks'/identity;r=load(folder/'RESULT.json');receipt=load(folder/'launch.json')
  assert receipt['exit_code']==0 and receipt['game_sha256']==runtime['game_sha256']
  assert r['status'].startswith('pass_') and all(c['pass'] for c in r['checks']),(identity,r['status'])
  results[identity]=dict(status=r['status'],checks=len(r['checks']),result_sha256=sha(folder/'RESULT.json'))
 cp=load(OUT/'checks/checkpoint_v2/RESULT.json');rs=load(OUT/'checks/restore_v2/RESULT.json')
 required={'moving_e_queues_visible_wait_without_write','pending_e_no_duplicate_request','escape_cancels_pending_no_write','unsafe_timeout_not_success','write_failure_window_retains_serial','mouse_retry_only_queues','readback_success_window_prompt_hidden','mouse_ok_closes_dialog_and_prompt','same_visit_e_f5_do_not_reopen_or_resave','new_visit_explicit_save_once','new_save_reloads','restart_menu_original_resources'}
 required.add('leaving_cancels_pending_no_write')
 assert required.issubset({c['name'] for c in cp['checks']})
 want=json.loads(cp['journal'])['snapshot'];got=json.loads(rs['restored'])['snapshot'];assert want['serial']==got['serial']==3
 for a,b in zip(want['actors'],got['actors']):
  for k in ['id','class','health','dead','loaded','reserve','shots']:assert a[k]==b[k],(a['id'],k)
  assert math.dist(a['location'],b['location'])<.001
 log=(OUT/'checks/checkpoint_v2/game.log').read_text(encoding='utf-8-sig')
 writes=[tuple(map(int,m)) for m in re.findall(r'PARIS_CHECKPOINT_DIALOG_WRITE frame=(\d+) after_draw=(\d+)',log)]
 assert len(writes)==3 and all(w>d+1 for w,d in writes),writes
 saved=re.findall(r'PARIS_G1_SAVED serial=(\d+)',log);assert saved==['2','3'],saved
 for name in ['waiting','crouched_wait','timed_out','saving','write_failed','saved_window','saved_clean_hud']:
  p=OUT/'checks/checkpoint_v2'/(name+'.png');assert p.is_file() and p.stat().st_size>50000,name
 failed_restore=load(OUT/'checks/restore_v1/launch.json');assert failed_restore['exit_code']==3 and not (OUT/'checks/restore_v1/RESULT.json').exists()
 result=dict(status='pass_checkpoint_dialog_native_checks_pending_manual_review',source_files=52,native_guards=1754,game_sha256=runtime['game_sha256'],source_manifest_sha256=runtime['source_manifest_sha256'],parents_models_original_transactions_saves_exact=True,cooked_reflection_exact=True,protected_blocks_exact=7,ordinary_entry_no_diagnostics=True,verified_runs=results,writes_after_draw= writes,successful_serials=saved,fresh_restore_serial=3,pre_ready_gpu_startup_failure_retained='restore_v1 exit3, DXGI_ERROR_DEVICE_HUNG; root cause unresolved; one distinct unchanged-settings recovery entry does not prove stability')
 (OUT/'verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result))
if __name__=='__main__':main()
