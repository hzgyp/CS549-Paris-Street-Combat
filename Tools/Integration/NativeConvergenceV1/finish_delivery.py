"""Publish local documentation from completed measured receipts, never assets or Git."""
import json,shutil,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Integration/NPCInteractionV1'))
from common import STORE,digest,guard_rows,guards_match

def main():
    parent=STORE/'Evidence/NativeConvergenceV1';bank_path=parent/'bank_v1_20261007/bank.json';bank=json.loads(bank_path.read_text())
    early=parent/'early_v2_20261007';full=parent/'full_v1_20261007';crowd=parent/'crowd_v1_20261007';artifact=parent/'artifact_v1_20261007'
    entries=[early,full];reports=[json.loads((e/'result.json').read_text()) for e in entries]
    for e in entries:assert json.loads((e/'audit.json').read_text())['status']=='pass_independent_convergence_audit'
    cases=[c for r in reports for c in r['cases']];assert len(cases)==138 and len({c['id'] for c in cases})==138
    assert {c['id'] for c in cases}=={c['id'] for c in bank['cases']}
    ca=json.loads((crowd/'audit.json').read_text());assert ca['status']=='pass_independent_crowd_observation_audit'
    stats={role:dict(Counter(s['status'] for s in cases if s['role']==role)) for role in ('allied','german')}
    reasons=dict(Counter(s['reason'] for s in cases if s['status']=='negative'))
    negatives=[s for s in cases if s['status']=='negative'];rows=guard_rows();assert rows==bank['protected_rows'] and guards_match(rows)
    source=STORE/bank['source'];assert all(digest(source/n)==h for n,h in bank['source_sha256'].items())
    for n,h in bank['helpers'].items():assert digest(ROOT/f'Unreal/ParisStreetCombat/Plugins/{n}/Binaries/Win64/UnrealEditor-{n}.dll')==h
    # Exact private copies preserve both the complete receipt and individual negatives.
    archive=parent/'failed_runtime_v1_20261007';assert not archive.exists();archive.mkdir();copied=[]
    for e in (full,crowd):
        folder=archive/e.name;folder.mkdir()
        selected=['result.json','entry.json','exit.json','audit.json','guards_before.json','ue_crowd.py' if e==crowd else 'ue_convergence.py']
        selected += [s['samples_file'] for s in json.loads((e/'result.json').read_text())['cases'] if s['status']=='negative' and (e/s['samples_file']).exists()]
        for name in selected:
            p=e/name;q=folder/name;shutil.copy2(p,q);assert digest(p)==digest(q)
            copied.append({'source':str(p),'copy':str(q),'sha256':digest(q),'bytes':q.stat().st_size})
        p=ROOT/'tmp/native-convergence-v1'/f'{e.name}.log';q=folder/p.name;shutil.copy2(p,q);assert digest(p)==digest(q);copied.append({'source':str(p),'copy':str(q),'sha256':digest(q),'bytes':q.stat().st_size})
    for name,p in [('terrain_bank.json',bank_path),('crowd_bank.json',parent/'crowd_bank_v1_20261007/bank.json')]:
        q=archive/name;shutil.copy2(p,q);copied.append({'source':str(p),'copy':str(q),'sha256':digest(q),'bytes':q.stat().st_size})
    (archive/'negative_cells.json').write_text(json.dumps({'role_start_negatives':negatives,'crowd_negatives_never_blacken_terrain':ca},indent=2)+'\n')
    failure=ROOT/'Failures/ML019-20261007-convergence-runtime';assert not failure.exists();failure.mkdir()
    (failure/'manifest.json').write_text(json.dumps({'failure':'ML019','commercial_derived_bytes_private':True,'originals_preserved':True,'rows':copied},indent=2)+'\n')
    (failure/'ANALYSIS.md').write_text(f'''# Native convergence terrain and interaction negatives

7 October 2026. Read ML010/11/13/14/15/17/18 and the convergence implementation/addenda/crowd plan. All138 frozen terrain-role tests complete once: Allied {stats['allied'].get('passed',0)} passed/{stats['allied'].get('negative',0)} negative; German {stats['german'].get('passed',0)} passed/{stats['german'].get('negative',0)} negative. White grid centres are geometry candidates, not native navigation admission. Observed reasons: {json.dumps(reasons)}. Each original native query/event/floor/trajectory is retained; no failed move was retried.

Complete-path rejection is failure under current saved navigation toward this particular hub, not proof of permanent physical obstruction or a broken model. PathFollowing failure after a complete A* query is a runtime navigation/movement negative; its particular obstructing primitive/root cause is not isolated by the floor support alone. Do not infer a gun/finger defect, relax the35cm/overlap/deadline gates, move the source, or automatically rebuild/save NavMesh. Blacken only the exact rejected25cm start cell in its role/hub-relative derivative, retaining the immutable source white map and unmeasured neighbours.

The separate three-new-start crowd observation has {ca['counts']['passed']} endpoint passes/{ca['counts']['negative']} negatives with original RVO/mutual collision restored and arrived bodies retained. Keep its raw completion/endpoint and other-body separation data. It is an interaction/capacity observation, not terrain admission; zero crowd start cells are blackened. Future rally-area/assigned-slot design is different work and must preserve these negatives.

Private authenticated copies: Evidence/NativeConvergenceV1/failed_runtime_v1_20261007, plus original admitted early/full/crowd directories. Current703, all old helpers and selected fine sources remain exact; normal exits/log gates are recorded in the final result. No original model, rig, fingers, gun, action, AI asset, formal map, navigation or selected Catalog is repaired/saved/published. No final placement or whole-map/squad/MVP/course pass follows. A later diagnosis needs a new measured bounded plan, not retries or colouring whole tiles/components black.
''',encoding='utf-8')
    english=f'''# Native NPC convergence survey result

7 October 2026. **The retained25cm black/white map now has a completed first native convergence sample:69 uniformly covered50m tiles, each tested once with an accepted Allied and German NPC,138 role/start outcomes.** The original map remains unchanged. These are temporary tests, not final spawn/objective/encounter choices.

Read the implementation and dependency/avoidance/crowd addenda and ML010/11/13/14/15/17/18. New runtime negatives are archived in ML019. Browser/iPad interaction work is deferred by the user.

## Actual outcomes

| Original profile | Reached and stood safely | Negative | Unmeasured bank cases |
|---|---:|---:|---:|
| Allied | {stats['allied'].get('passed',0)} | {stats['allied'].get('negative',0)} | 0 |
| German | {stats['german'].get('passed',0)} | {stats['german'].get('negative',0)} | 0 |

Observed terrain-bank reasons: `{json.dumps(reasons)}`. Do not equate missing/partial saved paths with physically blocked terrain. Native following failures retain their original completion events and actual sampled positions/supports, without an invented obstacle diagnosis. Every negative25cm start centre is black in its role-specific, **current-saved-navigation/to-this-hub** derivative. Neighbours, whole50m tiles and other connected destinations are not rejected by that observation. Other white remains a geometry candidate; this finite sample does not certify all733900 white centres.

This bank verifies movement **toward** the hub only. It does not establish hub-to-origin return or mutual all-pairs reachability. A future reciprocal test must use a new bounded bank and preserve these original successes/negatives, especially ML014's arrival-offset lesson.

The central real floor is [187.5,-337.5,107.87759089519764]cm, about3.86m from the geometric map centre, with25 measured3m-stencil stations. Both original NPC profiles stand safely there. Origins are selected from retained expanded-survey white; actual locomotion uses unchanged saved production Recast/Detour A* and original PathFollowing/CharacterMovement. Installed engine source confirms the A* call chain. Partial paths are rejected. Original maximum speed300cm/s, acceleration/capsules/terrain/time rate and native animation/equipment remain unchanged. Native actual route length determines the unchanged distance-scaled deadline. A near35m straight-distance origin required154.574m native travel and passed in52.509game seconds; a short universal timeout would misclassify it.

Four early_v2 positives are reused once, with their original RVO configuration. The134 fresh Full cases explicitly isolate capsule test-agent collisions and RVO group steering in the disposable world; original RVO enable flags and movement profiles remain exact. Inactive movement ticks are suspended to prevent falling. Each arrival requires matching SUCCESS, idle path following, actual XY/feet-Z<=35cm, grounded walking, no terrain overlap and0.6s safe standing. Python schedules only initial placements and observes; no moving-frame pose/position driver.

## Separate simultaneous crowd observation

Three newly frozen starts use original RVO groups and mutual capsule collision, the same exact hub/gates and retained arrived bodies: **{ca['counts']['passed']} endpoint passes, {ca['counts']['negative']} negatives**. Native final position/separation/event records and the near-hub trajectory plot are preserved. This is a measured interaction observation, not a production squad-follow pass. Crowd outcomes blacken zero terrain cells. A future rally region or assigned destinations must be designed separately rather than changing these failed gates.

## Layer status

The existing saved3/full5 local surface stacks and exact feetZ are retained. The new atlas shows full-survey geometric clearance nodes by local order:1242419,81265,13170,1740,76; admitted road white:733900,0,0,0,0. These are local XY-height stacks, not five globally consistent floors. **Semantic floor partitioning and real stair/ramp/bridge-above-below connections remain unverified.** No higher-layer origin is silently admitted or flattened into another floor. Native A* itself preserves real polygon heights/connectivity.

## Evidence and preservation

Private Evidence/NativeConvergenceV1 contains frozen bank, failed_dependency_v1, early_v2, full_v1, crowd_bank_v1, crowd_v1, layer_atlas_v1, artifact_v1 and the exact failed_runtime archive. Independent audits validate all138 finite bank outcomes and the separate3 crowd outcomes. Source mask differences are independently checked to be exactly the observed per-role negative starts; all ten derivative layer PNGs are4032² pure1bit. ML018's first setup failure had zero movement attempts, remains negative and blackens no cells. Its required snapshot-container contract was corrected in distinct early_v2; old functions/bank/thresholds remain exact.

Early native photographs were actually inspected and are dark/occluded, sometimes identical for overlapping isolated agents; they do not approve visual model presentation or full motion. The delivered map/layer/crowd figures are measured plots, not fabricated in-engine photographs. Selected original25cm source files, all703 frozen current guards and three historical survey helpers remain exact. No map/navigation/config/asset save, model/finger/grip/weapon/AI edit, Catalog adoption, release, Git commit or push. No whole-map, formation, performance, playable-build, teammate, MVP or course acceptance. All owned native exits and log gates are in closure; no user preview was terminated.
'''
    chinese=f'''# 正式NPC中央汇聚测绘结果

2026年10月7日，与英文同步。**原25厘米黑白地图保留；首轮真实UE汇聚抽样完成：69个50米均匀分区，每点各测一次正式盟军、德军，共138项。** 所有点仍是临时测试，不选最终出生、任务或遭遇位置。

已读实施方案、依赖／避让／人群补充和ML010／11／13／14／15／17／18，实际负面归档ML019。浏览器／iPad交互按用户要求暂缓。

## 实际结果

| 正式角色 | 实走到达并站稳 | 负面 | 库内未测 |
|---|---:|---:|---:|
| 盟军 | {stats['allied'].get('passed',0)} | {stats['allied'].get('negative',0)} | 0 |
| 德军 | {stats['german'].get('passed',0)} | {stats['german'].get('negative',0)} | 0 |

原始负面原因统计：`{json.dumps(reasons)}`。无完整保存导航路线不能直接解释为永久物理障碍；有路线但原生移动失败，保留真实完成事件、位置和支撑，不凭地面支撑名称虚构卡住的物体。派生图按角色将这些起点的**准确25厘米格心**标黑，含义限定为“当前保存导航下到不了本中央点”；不涂黑未测邻格、整个50米区域，或否定它到其他局部目标的能力。其他白格仍是几何候选，不能说733900个白格均已正式角色实走。

本库只验证**走向**汇聚点，尚不证明从中心返回、或任意点互相可达。往返验证须另立有界固定库，保留本次成功／负面，尤其继续遵守ML014的到达偏移教训。

汇聚点实际脚底为[187.5，−337.5，107.87759089519764]厘米，距地图几何中心约3.86米，3米站位模板有25个已测独立点。两种正式角色先站稳准入。初始点取自保留的扩展白图，实走采用**现有保存导航**和UE Recast／Detour原生A*、PathFollowing／CharacterMovement；已核查本机源码调用链，部分路径拒绝。原最大速度300厘米／秒、加速、胶囊、地形、时间倍率、动画和装备不变。按实际路线长度设置原距离超时：一处直线约35米，真实A*路线154.574米，用52.509游戏秒通过，不能统一短超时误判。

early_v2四个实际通过仅复用一次，保留其原RVO配置；Full其余134项首次实测，在临时世界隔离人物胶囊互堵及RVO组转向，原RVO开启标志和运动参数不变。非活动角色暂关移动tick防下落。到达须对应原生SUCCESS、寻路Idle、XY／脚底误差≤35厘米、有效步行地面、无地形重叠，并继续安全站稳0.6秒。Python仅调度初始放置和观察，不逐帧移位或驱动姿态。

## 同点多人观察

另用3个新固定起点，恢复原RVO组和人物碰撞，使用同一准确终点／原条件，已到人物留在原地：**{ca['counts']['passed']}项到达，{ca['counts']['negative']}项负面**。真实轨迹、最终距离和事件保留。本项属于人群交互观察，不是正式小队跟随验收；其结果涂黑地形格数为0。以后集合区／分配站位另行设计，不能重试或放宽本次失败条件。

## 分层是否完成

已有保存范围3个／扩展5个局部叠置表面及真实Z，本次补出分层总览。扩展几何净空节点按序为1242419、81265、13170、1740、76；道路准入白格为733900、0、0、0、0。它们不是5个统一建筑楼层。**完整楼层划分和楼梯／坡道／桥上桥下的真实层间通行仍未验证。** 不把高层自动涂白或压到另一层；本次原生A*自身保留真实高度及连接。

## 证据、失败和保护

私有Evidence/NativeConvergenceV1保留固定库、failed_dependency_v1、early_v2、full_v1、crowd_bank_v1、crowd_v1、layer_atlas_v1、artifact_v1和精确failed_runtime归档。独立审计核查138项库和3项人群结果；10张4032²纯1位角色／分层派生PNG，与源图的差异仅是实际负面起点。ML018首次初始化失败没有移动请求，仍是失败、不涂黑；不同early_v2补齐容器依赖，原认证函数、固定库、条件未改。

早期原生照片已实际查看，较暗／遮挡，隔离重叠人物有相同照片，不能据此验收模型视觉或完整动作。交付的地图、分层、人群图均是实测绘图，不冒充引擎照片。原25厘米选用来源、703项当前保护及3个旧辅助二进制精确不变。没有保存地图／导航／配置／资产，没有改模型、手指、握枪、枪械、AI，没有Catalog选用、发布、提交或推送。不宣称全地图、队形、性能、构建、队友、MVP或课程验收。自有原生退出／日志见闭合回执，未终止用户预览。
'''
    docs=ROOT/'Docs/Development/MissionLoopV1'
    for name,body in [('NATIVE_CONVERGENCE_RESULT_20261007.md',english),('NATIVE_CONVERGENCE_RESULT_20261007_ZH.md',chinese)]:
        p=docs/name;assert not p.exists();p.write_text(body,encoding='utf-8')
    closure={'status':'complete_finite_native_convergence_delivery','terrain_bank_cases':138,'roles':stats,'negative_reasons':reasons,
        'crowd':ca['counts'],'protected_rows':703,'guards_exact':True,'source_fine_map_retained':True,'semantic_floor_connections_verified':False,
        'hub_to_origin_return_verified':False,'all_pairs_mutual_reachability_verified':False,
        'native_exits':{e.name:json.loads((e/'exit.json').read_text(encoding='utf-8-sig')) for e in (early,full,crowd)},
        'evidence':{str(p.relative_to(parent)):digest(p) for p in [e/'audit.json' for e in (early,full,crowd)]+[artifact/'manifest.json',parent/'layer_atlas_v1_20261007/layer_atlas.json']},
        'failure_archives_exact':True,'browser_tablet_work_deferred':True,'final_layout_selected':False,'commit_push':False}
    p=parent/'closure_v1_20261007.json';assert not p.exists();p.write_text(json.dumps(closure,indent=2)+'\n')
    handoff=ROOT/'HANDOFF.md';old=handoff.read_text();marker='# Paris Street Combat - new-session handoff\n'
    assert old.startswith(marker)
    head=f'''
**NativeConvergenceV1 finite bank COMPLETE / native slot RELEASED — 7 October:**
User defers browser/iPad work and retains25cm original map. Read MissionLoopV1/
NATIVE_CONVERGENCE_IMPLEMENTATION and dependency/isolation/crowd plans plus RESULT/ZH,
ML018/19 before further map work. Frozen69 physical50m white tiles, each Allied/German,
138 native A* outcomes: Allied{stats['allied'].get('passed',0)}pass/{stats['allied'].get('negative',0)}negative;
German{stats['german'].get('passed',0)}pass/{stats['german'].get('negative',0)}negative.0bank unmeasured;
not all733900white centres certified. Temporary hub feet[187.5,-337.5,107.87759089519764]cm.
Expanded white origins, CURRENT SAVED NAV actual movement; original300cm/s,35cm/overlap/
0.6s standing/distance-scaled gates. Four early_v2 positives reused, Full134fresh cases:
test-character capsule+RVO group isolation only in unsaved world, original enable/profile exact.
Three new simultaneous crowd starts restore original RVO/mutual collision, retain arrived bodies:
{ca['counts']['passed']}pass/{ca['counts']['negative']}negative; zero terrain cells blackened from crowd.
Independent bank/crowd audits pass. Per-role/per-local-stack pure1bit4032² derivatives remove
only actual failed25cm initial centres relative to this hub/currentNav, not tiles/components.
All source fine files/703frozen guards/three helpers exact; no formal assets/nav/map save or
commit/push. ML018 early_v1 setup NameError before any move retained/private exact archive;
distinct v2 complete function dependency. Runtime negatives ML019 archived/no retries.
Private selected Evidence/NativeConvergenceV1/artifact_v1_20261007 plus layer_atlas_v1.
Saved3/full5 stacks retained; higher road white0, semantic floors/stairs/bridge layer links
UNVERIFIED. Early native photos dark/occluded, not visual/full-motion acceptance.
Tests are incoming-only; hub-to-origin return/all-pairs mutual reachability UNVERIFIED.
Figures are measured plots. Browser/iPad deferred, no final mission placements/squad/FPS/MVP pass.
All owned engines normally exited; verify actual process/closure before another writer.

'''
    handoff.write_text(marker+head+old[len(marker):],encoding='utf-8')
    index=ROOT/'Failures/README.md';text=index.read_text();prefix='# 失败案例索引 / Failure case index\n'
    assert text.startswith(prefix)
    index.write_text(prefix+'\n7 October native convergence negatives: [ML019](ML019-20261007-convergence-runtime/ANALYSIS.md).\nComplete138-case finite bank preserves source/path/travel negatives; black only exact role/hub-relative starts.\nSeparate3-person exact-point observation preserves interaction negatives and blackens zero terrain cells.\n'+text[len(prefix):],encoding='utf-8')
    print(json.dumps({'status':closure['status'],'roles':stats,'reasons':reasons,'crowd':ca['counts'],'closure_sha256':digest(p)}))

if __name__=='__main__':main()
