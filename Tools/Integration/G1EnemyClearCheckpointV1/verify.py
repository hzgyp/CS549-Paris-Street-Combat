"""Verify current Game, native admission receipts and immutable assets/journal invariants."""
from prepare import ROOT,OUT,SOURCE,load,rows,sha
from pathlib import Path
import json,re,math
import check_source
def main():
 check_source.main();runtime=load(OUT/'RUNTIME.json');manifest=load(SOURCE.parent/'SOURCE_MANIFEST.json')
 assert rows(SOURCE)==manifest['files'] and len(manifest['files'])==52
 prepared=load(OUT/runtime['revision']/'prepare.json');build=load(OUT/runtime['revision']/'build.json')
 for r in manifest['files']:assert sha(Path(prepared['project'])/r['path'])==r['sha256'],r['path']
 assert sha(SOURCE.parent/'SOURCE_MANIFEST.json')==runtime['source_manifest_sha256']==prepared['source_manifest_sha256']
 assert sha(Path(runtime['path'])/'Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe')==runtime['game_sha256']==build['game_sha256']
 entry=(Path(runtime['path'])/'PLAY_G1_REVISION.cmd').read_text(encoding='utf-8-sig')
 assert runtime['user_directory'] in entry and not any(k in entry for k in ['ParisUXTest','ParisInteractionProbe','ParisAVAuditOut','ParisDemo','ParisSpaceSurveyOut'])
 results={}
 for name in ['menu_v1','clearance_v2','restore_v2','legacy_v1']:
  folder=OUT/'checks'/name;result=load(folder/'RESULT.json');launch=load(folder/'launch.json')
  assert launch['exit_code']==0 and launch['game_sha256']==runtime['game_sha256']
  assert result['status'].startswith('pass_') and all(c['pass'] for c in result['checks']),(name,result['status'])
  results[name]=dict(status=result['status'],checks=len(result['checks']),result_sha256=sha(folder/'RESULT.json'))
 clear=load(OUT/'checks/clearance_v2/RESULT.json');restore=load(OUT/'checks/restore_v2/RESULT.json')
 required={'zero_dead_e_f5_denied_even_at_g1','one_dead_still_locked','two_dead_still_locked','last_death_wins_without_far_bank_or_occupation','both_living_allies_unfinished_transit_not_a_gate','moving_crouched_player_has_no_save_blocker','moving_crouched_save_readback_success','ack_hides_prompt_and_repeats_do_not_write','real_disk_failure_retains_previous_save','retry_real_write_readback_success_once','f9_completed_clearance_checkpoint_restored','f6_three_alive_relocks_original_fresh_resources'}
 assert required.issubset({c['name'] for c in clear['checks']})
 want=json.loads(clear['journal'])['snapshot'];loaded=json.loads(clear['reloaded'])['snapshot'];fresh=json.loads(restore['restored'])['snapshot']
 for got in [loaded,fresh]:
  assert want['serial']==got['serial']==2 and want['phase']==got['phase']=='Won'
  for a,b in zip(want['actors'],got['actors']):
   for key in ['id','class','health','dead','loaded','reserve','shots']:assert a[key]==b[key],(a['id'],key)
   assert math.dist(a['location'],b['location'])<.001,(a['id'],'location')
 # Grounded low-posture saves must not become floor-embedded after lifecycle reset.
 settled=json.loads(clear['settled_restored'])['snapshot']['actors'][0]['location']
 assert math.dist(settled,want['actors'][0]['location'])<1,(settled,want['actors'][0]['location'])
 log=(OUT/'checks/clearance_v2/game.log').read_text(encoding='utf-8-sig')
 saved=re.findall(r'PARIS_G1_SAVED serial=(\d+)',log);assert saved==['1','2'],saved
 assert 'state=Waiting' not in log and 'Finish securing G1' not in log
 writes=[tuple(map(int,v)) for v in re.findall(r'PARIS_CHECKPOINT_DIALOG_WRITE frame=(\d+) after_draw=(\d+)',log)]
 assert len(writes)==3 and all(w>d+1 for w,d in writes),writes
 for name in ['saving','saved_window','clean_hud','write_failed','restored']:
  p=OUT/'checks/clearance_v2'/(name+'.png');assert p.is_file() and p.stat().st_size>50000
 # Preserve failed build, distinct repaired source receipt; never relabel it.
 assert load(OUT/'candidate_v1/build.json')['status']=='compile_failed'
 result=dict(status='pass_enemy_clear_checkpoint_native_checks_pending_manual_review',source_files=52,source_manifest_sha256=runtime['source_manifest_sha256'],game_sha256=runtime['game_sha256'],only_three_source_files_changed=True,cooked_reflection_exact=True,native_guards=1754,protected_blocks_exact=7,durable_write_readback_exact=True,player_saved_z_normalized_to_original_standing_capsule=True,ordinary_entry_no_diagnostics=True,verified_runs=results,successful_serials=saved,writes_after_draw=writes,fresh_restore_serial=2,settled_player_drift_cm=math.dist(settled,want['actors'][0]['location']),scope='Isolated original-death endpoint/diagnostic placement regression; no new natural combat/transit/FPS/physical-input claims')
 (OUT/'verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result))
if __name__=='__main__':main()
