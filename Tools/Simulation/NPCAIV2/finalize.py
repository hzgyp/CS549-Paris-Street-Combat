"""Produce an exact local handoff; never merge/write selected game source."""
import argparse
import ast
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def cpp_body(path,signature):
    source=path.read_text(encoding='utf-8-sig')
    start=source.index(signature); brace=source.index('{',start);level=0
    for i in range(brace,len(source)):
        level+=int(source[i]=='{')-int(source[i]=='}')
        if level==0:
            return source[start:i+1]
    raise ValueError('Unclosed function '+signature)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--run',required=True);args=parser.parse_args();run=(ROOT/args.run).resolve();work=run.parent
    handoff=work/'SOURCE_HANDOFF.json';reconciliation=work/'BASE_RECONCILIATION.json';static=work/'STATIC_CHECKS.json'
    pointer=ROOT/'Docs/Development/CURRENT_NPC_AI_CANDIDATE.json'
    if any(p.exists() for p in (handoff,reconciliation,static,pointer)):
        raise SystemExit('Preserve existing identities; finalization outputs already exist')
    old=json.loads((work/'AUDIT_INITIAL.json').read_text(encoding='utf-8'));final=json.loads((work/'AUDIT_FINAL.json').read_text(encoding='utf-8'))
    selector_path=ROOT/'Docs/Development/CURRENT_TUTORIAL_SOURCE_PENDING.json';selector=json.loads(selector_path.read_text(encoding='utf-8-sig'))
    if selector['source_manifest_sha256']!=final['source_manifest_sha256']:
        raise SystemExit('Shared base advanced again; audit and reconcile before finalization')
    oldbase=ROOT/old['source_project'];newbase=ROOT/final['source_project']
    def relative_rows(a,base):return {str(Path(x['path']).relative_to(base)).replace('\\','/'):x for x in a['source']}
    aa,bb=relative_rows(old,oldbase),relative_rows(final,newbase)
    changed=[{'path':p,'old_sha256':aa.get(p,{}).get('sha256'),'new_sha256':bb[p]['sha256'],'kind':'changed' if p in aa else 'added'} for p in bb if aa.get(p,{}).get('sha256')!=bb[p]['sha256']]
    sourcecpp=Path('Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/ParisBridgeMission.cpp')
    signatures=['EBTNodeResult::Type UParisG1AgentPlan::ExecuteTask','bool AParisBridgeMission::UpdateBridgeSquad',
                'bool AParisBridgeMission::BuildBridgePath','bool AParisBridgeMission::InstallAgentFeetPlan']
    functions=[]
    for sig in signatures:
        a,b=cpp_body(oldbase/sourcecpp,sig),cpp_body(newbase/sourcecpp,sig)
        functions.append({'signature':sig,'unchanged':a==b,'sha256':hashlib.sha256(b.encode()).hexdigest()})
    retained=sum(Path(row['path']).is_file() and sha(Path(row['path']))==row['sha256'] for row in old['source'])
    receipt={'scope':'read_only_reconciliation_no_merge','original_revision':old['source_revision'],'current_revision':final['source_revision'],
             'original_manifest_sha256':old['source_manifest_sha256'],'current_manifest_sha256':final['source_manifest_sha256'],
             'original_source_files_still_exact':retained,'inherited_identical':len(aa)-sum(p in aa for p in [x['path'] for x in changed]),
             'current_source_files_match_manifest':final['source_matches'],'relative_changed_or_added':changed,
             'npc_native_all_92_unchanged':old['native']==final['native'],
             'AI_function_comparison':functions,'explanation':'Another lane advanced the shared pointer to an independent medical/music child; no AI game/native source write occurred.',
             'admission':'Use current live combined selector before integration, preserve all tutorial/action/audio/medical changes; no shared merge is performed.'}
    if not all(f['unchanged'] for f in functions) or retained!=len(old['source']) or old['native']!=final['native']:
        raise SystemExit('Reconciliation identity conflict; preserve evidence and stop shared integration')
    reconciliation.write_text(json.dumps(receipt,indent=2),encoding='utf-8')
    checks=[];functions=[]
    for file in HERE.glob('*.py'):
        tree=ast.parse(file.read_text(encoding='utf-8'))
        checks.append({'path':str(file),'python_ast_syntax':'pass'})
        def visit(node,prefix=''):
            for child in ast.iter_child_nodes(node):
                if isinstance(child,ast.ClassDef):visit(child,prefix+child.name+'.')
                elif isinstance(child,(ast.FunctionDef,ast.AsyncFunctionDef)):
                    functions.append({'path':str(file),'function':prefix+child.name,'line':child.lineno,'end_line':child.end_lineno})
        visit(tree)
    for file in HERE.glob('*.json'):
        json.loads(file.read_text(encoding='utf-8'));checks.append({'path':str(file),'json_parse':'pass'})
    template=(HERE/'replay.html').read_text(encoding='utf-8');script=template.split('<script>',1)[1].split('</script>',1)[0]
    (work/'replay_script_syntax.js').write_text(script,encoding='utf-8')
    static.write_text(json.dumps({'scope':'Python/JSON parse only, browser JS verified separately','checks':checks},indent=2),encoding='utf-8')
    files=[]
    for folder in (HERE,ROOT/'Docs/Development/NPCAIV2',run):
        for p in sorted(folder.rglob('*')):
            if p.is_file() and '__pycache__' not in p.parts:
                files.append({'path':str(p.relative_to(ROOT)).replace('\\','/'),'size_bytes':p.stat().st_size,'sha256':sha(p)})
    manifest={'scope':'independent_offline_candidate_not_shared_source_or_native_adoption','selected_run':str(run.relative_to(ROOT)).replace('\\','/'),
              'initial_game_audit_manifest_sha256':old['source_manifest_sha256'],'integration_entry_now':{
                  'selector':str(selector_path.relative_to(ROOT)).replace('\\','/'),'revision':selector['source_revision'],
                  'source_project':selector['source_project'],'manifest_sha256':selector['source_manifest_sha256'],'must_re_read_before_merge':True},
              'files':files,'functions':functions,'exact_inventory_bytes':sum(x['size_bytes'] for x in files),'exact_inventory_files':len(files),
              'selected_run_bytes':sum(x['size_bytes'] for x in files if x['path'].startswith(str(run.relative_to(ROOT)).replace('\\','/')+'/')),
              'algorithm_checks':79,'replay_checks':9,'merged_into_game':False,'new_build_authorized':False,
              'map_integration_passed':False,'publication_performed':False,'coursework_uploads_performed':False,
              'oracle':'sequential full scenario policy/scoring/move expectations; replay only renders logged output',
              'retained_unselected_runs':['run_v1','run_v2','run_v3','run_v4','run_v5'],
              'rollback':'Keep independent candidate unselected; no shared rollback/deletion required.'}
    handoff.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    pointer.write_text(json.dumps({'status':'finite_offline_candidate_verified_not_game_integrated','date':'2026-10-17',
       'implementation':'Docs/Development/NPCAIV2/IMPLEMENTATION_20261017.md','implementation_zh':'Docs/Development/NPCAIV2/IMPLEMENTATION_20261017_ZH.md',
       'result':'Docs/Development/NPCAIV2/RESULT_20261017.md','result_zh':'Docs/Development/NPCAIV2/RESULT_20261017_ZH.md',
       'source':'Tools/Simulation/NPCAIV2','selected_run':manifest['selected_run'],'replay':manifest['selected_run']+'/replay.html',
       'replay_size_bytes':(run/'replay.html').stat().st_size,'handoff':'tmp/npc-ai-v2-20261017/SOURCE_HANDOFF.json',
       'handoff_sha256':sha(handoff),'base_reconciliation':'tmp/npc-ai-v2-20261017/BASE_RECONCILIATION.json',
       'live_combined_selector':'Docs/Development/CURRENT_TUTORIAL_SOURCE_PENDING.json','integration_revision_at_handoff':selector['source_revision'],
       'integration_manifest_at_handoff':selector['source_manifest_sha256'],'re_read_before_integration':True,
       'algorithm_checks':79,'replay_checks':9,'geometry_scope':'hypothetical_2D_not_Paris_survey','UE_runtime_accepted':False,
       'shared_source_native_written':False,'new_build_authorized':False,'no_automatic_map_queue_or_publication':True},indent=2),encoding='utf-8')
    print(json.dumps({'status':'local_handoff_written','revision':selector['source_revision'],'source_functions_unchanged':len(receipt['AI_function_comparison']),
                      'files':len(files),'bytes':manifest['exact_inventory_bytes'],'run_bytes':manifest['selected_run_bytes'],'handoff_sha256':sha(handoff)}))


if __name__=='__main__':main()
