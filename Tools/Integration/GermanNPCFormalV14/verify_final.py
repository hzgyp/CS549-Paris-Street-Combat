"""Read-only selected-epoch validation; private final QA receipt, no native entry."""
import ast
import subprocess
from common import *

epoch=read(BASE/'selected_v1/result.json')
assert epoch['status']=='formal_german_v11_with_rifle_and_private_sftp_verified'
assert epoch['file_count']==678 and len(epoch['files'])==678
assert all(exact(f) for f in epoch['files']), 'Current guard mismatch: do not roll back'
pre=read(BASE/'preflight/result.json')
assert exact(pre['descriptor']) and all(exact(f) for f in pre['baseline_files'])
assert sha(CONFIG)==pre['config_sha256']
scripts=list(Path(__file__).parent.glob('*.py'))
for p in scripts:
    ast.parse(p.read_text(encoding='utf-8-sig'),filename=str(p))
ps_paths=[str(p) for p in Path(__file__).parent.glob('*.ps1')]
ps_paths.append(str(ROOT/'Tools/Integration/run_paris_native_preview.ps1'))
commands=[]
for name in ps_paths:
    literal=name.replace("'","''")
    commands.append("$taskTokens=$null;$taskErrors=$null;[void][System.Management.Automation.Language.Parser]::ParseFile('"+literal+"',[ref]$taskTokens,[ref]$taskErrors);if($taskErrors.Count){throw ($taskErrors|Out-String)}")
commands.append("if(Get-Process UnrealEditor*,blender* -ErrorAction SilentlyContinue){throw 'Native slot remains occupied'}")
subprocess.run(['powershell.exe','-NoProfile','-Command',';'.join(commands)],check=True,capture_output=True,text=True)
log=ROOT/'tmp/german-npc-formal-v14/ordinary_game_v2.log'
assert read(Path(str(log)+'.exit.json'))['exit_code']==0
text=log.read_text(encoding='utf-8-sig',errors='replace')
assert text.count('PARIS_GERMAN_GRIP_READY')==3 and text.count('PARIS_ALLIED_GRIP_READY')==2
assert 'Paris approved first-person native binding ready; original gameplay retained' in text
assert 'PARIS_GERMAN_GRIP_FAILURE' not in text and 'PARIS_ALLIED_GRIP_FAILURE' not in text
receipt={'status':'current_678_rows_source_descriptor_config_parse_and_game_ready_verified',
    'exact_guard_rows':678,'python_ast_files':len(scripts),'powershell_parse_files':len(ps_paths),
    'engines_running':False,'native_slot':'A RELEASED',
    'qa_marker_correction':'First read-only QA asserted nonexistent PARIS_GRIP_V18_READY; corrected to the actual unchanged FP log message, no native rerun or asset change',
    'git_commit_push':'not requested/not performed','whole_mvp':'not established'}
write(BASE/'final_qa_v1/result.json',receipt)
print(json.dumps(receipt))
