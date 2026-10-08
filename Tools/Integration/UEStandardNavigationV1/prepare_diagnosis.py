"""Generate a query-only observer with unique receipt identities; never replay locomotion."""
import ast,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).parent
sys.path.insert(0,str(ROOT/'Tools/Integration/NPCInteractionV1'))
from common import STORE,digest

def main():
    p=STORE/'Evidence/UEStandardNavigationV1';bank=json.loads((p/'bank_v1_20261007/bank.json').read_text())
    path=p/'diagnostic_bank_v1_20261007.json';assert not path.exists()
    selected=[s['id'] for s in bank['cases'] if s['origin_index'] in (0,4,7,9,18,49)]
    frozen={'case_ids':selected,'budgets':[0,65536],'queries':48,'movement_submitted':False,
        'parent_bank_sha256':digest(p/'bank_v1_20261007/bank.json'),
        'plan_sha256':digest(ROOT/'Docs/Development/MissionLoopV1/UE_STANDARD_NAV_QUERY_DIAGNOSIS_20261007.md')}
    path.write_text(json.dumps(frozen,indent=2)+'\n',encoding='utf-8',newline='\n')
    text=(HERE/'ue_standard.py').read_text()
    tree=ast.parse(text);fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='standard_request')
    lines=text.splitlines(keepends=True);del lines[fn.lineno-1:fn.end_lineno];text=''.join(lines)
    assert 'move_to_location' not in text and 'begin_formal_move' not in text
    text=text.replace("early=set(bank['early_ids']);queue=[c for c in bank['cases'] if STAGE=='SavedProbe' or (c['id'] in early)==(STAGE=='Early')]", "query_bank=json.loads((STORE/'Evidence/UEStandardNavigationV1/diagnostic_bank_v1_20261007.json').read_text());assert query_bank['parent_bank_sha256']==digest(BANK)\n            queue=[c for c in bank['cases'] if c['id'] in query_bank['case_ids']]\n            report['query_diagnosis_plan_sha256']=query_bank['plan_sha256'];report['queries_only']=True")
    begin=text.index("                req=standard_request(controllers[i],h['feet_cm'])")
    end=text.index("            phase='moving';last_sample=t;write();return",begin)
    text=text[:begin]+"""                s['diagnostic_queries']=[]
                for budget in (0,65536):
                    answer=json.loads(unreal.ParisNavDiagnosticsLibrary.inspect_standard_query(controllers[i],unreal.Vector(*bank['hub']['feet_cm']),budget))
                    assert not answer.get('error'),answer
                    assert answer['movement_submitted'] is False
                    s['diagnostic_queries'].append(answer)
                    if s['origin_index']==0:assert answer['path_valid'] and not answer['partial'],'Positive native query control failed'
                record(i,'query_observed','no_movement_submitted')
"""+text[end:]
    # Remove the now-unreachable movement observer branch, retaining the common fixture/end handling.
    begin=text.index("        if phase=='moving':");end=text.index("    except Exception:",begin)
    text=text[:begin]+"        if phase=='moving':phase='next';write();return\n"+text[end:]
    ast.parse(text);(HERE/'ue_diagnosis.py').write_text(text,encoding='utf-8',newline='\n')
    runner=(HERE/'run_standard.ps1').read_text().replace('ue_standard.py','ue_diagnosis.py')
    runner=runner.replace('-EnablePlugins=ParisFormalSurveyV1,ParisMapSurveyV1','-EnablePlugins=ParisFormalSurveyV1,ParisMapSurveyV1,ParisNavDiagnosticsV1')
    (HERE/'run_diagnosis.ps1').write_text(runner,encoding='utf-8',newline='\n')
    build=(ROOT/'Tools/Integration/MapGridV1/build_helper.ps1').read_text().replace('ParisGridSurveyV1','ParisNavDiagnosticsV1').replace('map-grid-v1','ue-standard-navigation-v1').replace('Evidence/MapGridV1','Evidence/UEStandardNavigationV1')
    (HERE/'build_diagnostic.ps1').write_text(build,encoding='utf-8',newline='\n')
    print(json.dumps({'frozen_queries':48,'physical_movements':0,'case_ids':selected}))

if __name__=='__main__':main()
