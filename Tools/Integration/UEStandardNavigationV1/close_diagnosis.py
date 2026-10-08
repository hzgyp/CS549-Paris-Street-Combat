"""Persist audited native query diagnosis and retain its exact source/receipts privately."""
import json,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'Tools/Integration/NPCInteractionV1'))
from common import STORE,digest,guard_rows,guards_match
P=STORE/'Evidence/UEStandardNavigationV1'

def main():
    names=('diagnostic_saved_v1_20261007','diagnostic_expanded_v1_20261007')
    data=[];hashes={};copies=[];out=P/'diagnosis_archive_v1_20261007';assert not out.exists();out.mkdir()
    for name in names:
        e=P/name;a=json.loads((e/'audit.json').read_text());assert a['status']=='pass_independent_query_diagnosis_audit';data+=a['observations'];hashes[name]=digest(e/'audit.json')
        for file in list(e.glob('*'))+[ROOT/f'tmp/ue-standard-navigation-v1/{name}.log']:
            if not file.is_file():continue
            target=out/name/file.name;target.parent.mkdir(exist_ok=True);shutil.copyfile(file,target);assert digest(file)==digest(target)
            copies.append({'source':str(file),'copy':str(target),'sha256':digest(file)})
    assert len(data)==24 and len(guard_rows())==703 and guards_match(guard_rows())
    result={'status':'complete_native_query_diagnosis','native_queries':48,'physical_movements':0,'audit_sha256':hashes,
        'observations':data,'search_budget_contribution_cases':[r for r in data if r['search_budget_contribution_observed']],
        '703_exact':True,'default_filter_mutated':False,'native_nav_saved':False,
        'diagnostic_helper_sha256':digest(ROOT/'Unreal/ParisStreetCombat/Plugins/ParisNavDiagnosticsV1/Binaries/Win64/UnrealEditor-ParisNavDiagnosticsV1.dll')}
    (P/'query_diagnosis_v1_20261007.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    (out/'manifest.json').write_text(json.dumps({'copies':copies,'originals_retained':True},indent=2)+'\n',encoding='utf-8',newline='\n')
    d=ROOT/'Docs/Development/MissionLoopV1';lines=['| Scope | Origin | Role | Original budget | Original complete | Search limit reached | Copied65536 complete |','|---|---:|---|---:|---|---|---|']
    for r in data:
        parts=r['id'].split('_');lines.append(f"| {r['scope']} | {int(parts[1])} | {parts[2]} | {r['original_budget']} | {r['original_complete']} | {r['original_search_reached_limit']} | {r['higher_budget_complete']} |")
    table='\n'.join(lines)
    count=len(result['search_budget_contribution_cases'])
    text=f'''# Native query diagnosis result

7 October2026. Read UE_STANDARD_NAV_QUERY_DIAGNOSIS and ML013/17/19/21.48 native read-only queries complete at six unchanged sites/two original roles/two navigation scopes/two query budgets. Zero movement requests, zero physical arrivals under the higher budget, no default filter/config/map mutation. Independent audits and normal exit0/strict log0 pass; current703, helpers, models/fingers/weapons/sources exact.

{table}

Observed search-budget contributions: {count} site/role/scope combinations. A contribution requires the ORIGINAL query to reach its node limit without a complete path, while one cloned-filter65536 query finds a complete path. This does not establish measured physical traversal, production budget choice/performance, bridge-specific support, all69 higher-budget cases or whole-map connectivity. Native adjacency alone remains weaker than these filtered query results. Preserve the complete default-budget physical bank and all earlier negatives; do not rerun a stopped movement or silently adopt a configuration. A future physical budget control needs a new bounded plan and identities.

Private query_diagnosis_v1_20261007.json and diagnosis_archive_v1_20261007 authenticate native responses, sources, exports and logs. The diagnostic plugin is separate/disabled/Editor-only and supplies no path or movement, leaving all old helpers unchanged. Source/helper build and receipt hashes are retained. No final sites, squad/floors/FPS/MVP/course acceptance, save, commit or publication.
'''
    zh=f'''# 原生查询诊断结果

2026年10月7日。已读原生查询诊断计划和ML013/017/019/021。六个原点、两原阵营、保存/临时完整导航、原预算/复制高预算，共48项UE只读查询完成。没有发移动请求，高预算实际到达0项；未改默认过滤器/配置/地图。独立审计、正常退出0/严格日志0通过；703项、辅助库、模型/手指/枪械/源数据保持。

{table}

观察到搜索预算影响的点/阵营/范围组合：{count}项。必须同时满足：原查询触顶而未获得完整路径，一份复制过滤器的65536查询获得完整路径。这不证明高预算实际走过、正式预算/性能选择、桥的实际支撑、69个点全量高预算查询或全图互达。原始邻接比经过过滤的UE查询证据弱。原默认预算真实移动银行和所有旧失败保留，不能重跑旧失败或暗中采用配置；后续高预算实体对照需要新的有界计划和身份。

私有query_diagnosis_v1_20261007.json及diagnosis_archive_v1_20261007认证原生返回、脚本、导出和日志。独立默认关闭Editor诊断插件不提交路径/移动，原三个辅助库保持；保存源/构建/回执哈希。未验最终点、小队/完整楼层/FPS/MVP/课程，未保存正式地图、提交发布。
'''
    (d/'UE_STANDARD_NAV_QUERY_RESULT_20261007.md').write_text(text,encoding='utf-8',newline='\n')
    (d/'UE_STANDARD_NAV_QUERY_RESULT_20261007_ZH.md').write_text(zh,encoding='utf-8',newline='\n')
    print(json.dumps({'queries':48,'physical_movements':0,'budget_contribution_combinations':count,'result_sha256':digest(P/'query_diagnosis_v1_20261007.json')}))

if __name__=='__main__':main()
