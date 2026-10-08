"""Independent native exit/log/receipt/protection gate. Never rewrites raw receipts."""
import argparse,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Integration/NPCInteractionV1'))
from common import STORE,guard_rows,guards_match,digest
p=argparse.ArgumentParser();p.add_argument('--identity',required=True);p.add_argument('--mode',choices=('author','test','plain'),required=True)
p.add_argument('--revision',choices=('python_log_v2',))
a=p.parse_args();assert re.fullmatch('[A-Za-z0-9_]+',a.identity)
out=STORE/'Evidence/G1MissionV1'/a.identity;log=ROOT/'tmp/g1-mission-v1'/f'{a.identity}.log'
text=log.read_text(errors='replace');exit_file=Path(str(log)+'.exit.json');native_exit=json.loads(exit_file.read_text(encoding='utf-8-sig'))
bad=[x for x in text.splitlines() if re.search(r'Log\w+: Error:|Fatal error:|Ensure condition failed|Unhandled Exception',x)]
rows=guard_rows();checks={'normal_exit':native_exit['exit_code']==0,'strict_native_log':not bad,'protected703_exact':len(rows)==703 and guards_match(rows)}
manifest=out/'runtime_manifest.json'
if manifest.exists():
 runtime=json.loads(manifest.read_text(encoding='utf-8-sig'))
 checks['owned_runtime_inputs_exact']=all(digest(ROOT/f['path'])==f['sha256'] for f in runtime['files'])
if a.mode=='plain':
 checks.update({'native_mission_ready':'PARIS_G1_PHASE Ready' in text,'python_disabled':"Python disabled via command-line flag '-DisablePython'" in text,
  'no_python_usage':not re.search(r'Using Python|Python is enabled|LogPython:.*(?:Python enabled|Running start-up script)',text),
  'bridge_absent':'Mounting Project plugin ParisEditorBridge' not in text})
else:
 raw=json.loads((out/'result.json').read_text())
 checks.update({'raw_receipt_pass':raw['status'].startswith('pass_'),'raw_protection_exact':raw.get('protected_unchanged') is True,
  'raw_no_errors':not raw['errors']})
result={'identity':a.identity,'checks':checks,'status':'pass_native_entry_audit' if all(checks.values()) else 'failed_native_entry_audit',
 'errors':bad,'log_sha256':digest(log),'exit_sha256':digest(exit_file)}
target=out/'audit.json'
if a.revision:
 assert a.mode=='plain'
 previous=json.loads(target.read_text())
 assert previous['status']=='failed_native_entry_audit' and previous['checks']['python_disabled'] is False
 assert all(v for k,v in previous['checks'].items() if k!='python_disabled')
 assert previous['log_sha256']==digest(log) and previous['exit_sha256']==digest(exit_file)
 engine=Path('C:/Program Files/Epic Games/UE_5.8/Engine/Plugins/Experimental/PythonScriptPlugin/Source/PythonScriptPlugin/Private/PythonScriptPlugin.cpp')
 source=engine.read_text()
 assert 'TEXT("DisablePython")' in source and "Python disabled via command-line flag '-DisablePython'" in source
 result.update(revision=a.revision,previous_failed_audit_sha256=digest(target),engine_source=str(engine),engine_source_sha256=digest(engine),native_entry_not_rerun=True)
 target=out/('audit_'+a.revision+'.json')
 snapshot=out/('audit_'+a.revision+'_source.py');assert not snapshot.exists();snapshot.write_bytes(Path(__file__).read_bytes())
assert not target.exists();target.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2));sys.exit(0 if all(checks.values()) else 2)
