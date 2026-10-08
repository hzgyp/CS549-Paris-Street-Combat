"""Write final bilingual records only after complete finite coverage and audit."""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("identity")
args = parser.parse_args()
root = Path(__file__).resolve().parents[3]
docs = root / "Docs/Development/MissionLoopV1"
entry = root / "Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/PureMapSurveyV1" / args.identity
r = json.loads((entry / "survey.json").read_text())
a = json.loads((entry / "audit_v1.json").read_text())
assert r["status"] == "complete_finite_pure_map_survey_with_negative_edges_retained"
assert not r["errors"] and r["protected_bytes_unchanged"]
assert a["status"] == "pass_receipt_audit" and a["full_finite_case_coverage"] and a["unmeasured_cases"] == 0
assert a["exit"]["exit_code"] == a["exit"]["strict_log_errors"] == 0 and a["protected_rows"] == 703
assert a["completed_cases"] == 28684
stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
counts = (a["completed_cases"], a["passed_edges"], a["standing_only_passes"], sum(a["failure_reasons"].values()))
names = {"native_completion_or_endpoint_failed": "完成／端点拒绝",
    "source_previously_rejected_no_retry": "已拒绝源，缓存跳过",
    "source_not_safe_standing_surface": "源站立未过",
    "runtime_query_missing_or_partial": "无完整运行时路径",
    "native_request_not_started": "原生移动请求未启动",
    "native_stall_deadline": "移动停滞期限",
    "previously_rejected_exact_surface_query_no_retry": "已有精确查询负面，关联跳过",
    "previously_rejected_remote_case_no_retry": "已有远处负面，关联跳过"}
reasons_zh = "\n".join(f"| {names.get(k, k)} | {v:,} |" for k, v in a["failure_reasons"].items())
reasons_en = "\n".join(f"| {k} | {v:,} |" for k, v in a["failure_reasons"].items())
groups = ", ".join(f"{n:,}" for n in a["physical_component_sizes"][:8])
feet = a["passed_movement_feet_z_range_cm"]
vertical = a["case_categories"]["vertical"]
narrow = a["case_categories"]["narrow"]
falling = sum(n for mode, n in a["sampled_movement_modes"].items() if "MOVE_FALLING" in mode)
for name in ("PURE_MAP_TEST_RESULT_20261007.md", "PURE_MAP_TEST_RESULT_20261007_ZH.md"):
    source = docs / name
    history = docs / name.replace("RESULT_", "RESULT_EXECUTION_NOTES_")
    assert not history.exists()
    history.write_text("Archived chronological checkpoints; later verified final result supersedes them.\n\n"+source.read_text(encoding="utf-8"), encoding="utf-8")

zh = f'''# 纯地图连通性测试结果

{stamp}。先形成[测试流程](PURE_MAP_TEST_WORKFLOW_20261007_ZH.md)，再执行。**规定精度的28,684项有限清单已全部记录并通过独立回执审计；这不表示全图互通。** [英文原文](PURE_MAP_TEST_RESULT_20261007.md)同步。

| 已核验范围 | 结果 |
| --- | --- |
| 隔离环境 | 8个加载关卡、23,037个阻挡组件；未保存副本移除15个原玩法对象，运行时原玩家／NPC／项目玩法Actor为0。环境车保留碰撞，仅在测试副本静止。 |
| 全范围导航 | 11,828有效／导出瓦片，真正异常0；27,836多边形、15,543表面区域、47,176有向邻接、2,231查询强连通组。 |
| 有限清单 | {counts[0]:,}项已记录：{counts[1]:,}项移动通过、{counts[2]:,}项仅站立通过、{counts[3]:,}项负面／缓存拒绝；未测清单0。控制项不增加主分母。 |
| 高差／窄口标记 | 高差{vertical['completed']:,}项：通过{vertical['passed']:,}、负面{vertical['failed']:,}；窄口{narrow['completed']:,}项：通过{narrow['passed']:,}、负面{narrow['failed']:,}。两类可重叠，不能相加为独立分母。 |
| 真实移动证据 | 原生ACharacter／AAIController、Manny默认无武器显示；请求编号／控制器／SUCCESS／实际端点／CurrentFloor逐项核对。通过移动脚底Z范围{feet[0]/100:.2f}至{feet[1]/100:.2f}m。 |
| 实测有向组 | 仅用通过移动边端点形成{len(a['physical_component_sizes']):,}个强连通证据组；最大几组区域数为{groups}。其余表面不因此被判物理隔绝。 |
| 正常关闭 | 最新自有PID {a['exit']['owned_pid']}正常退出0、严格日志0、703项保护精确；静态车辆组件／边界／碰撞精确、模拟关闭，最大位移0。 |

本次按10米瓦片及真实双向邻接组织表面区域，保留真实XYZ、精确多边形详细表面点、原顶点平均中心和有向连接。同XY叠置的1,049处瓦片位置不能按Z取整合并；Recast层0–5不是六层楼。2.5D图用于阅读，UE保留3D导航。现有BasicShapes Plane／Cube及外围代理几何是测试来源，不能凭最大组面积直接选为巴黎任务区。

![有限清单实走与高度](../../../Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/PureMapSurveyV1/Visuals/PURE_MAP_FINITE_RESULT_20261007.svg)

## Z轴结论

**至少一条真实高度连接已双向实走。** case07537由道路脚底约0.90m走到较高表面约6.99m，case07910由约7.04m返回约0.90m；两段原生SUCCESS、匹配请求编号、采样均步行，端点XY／脚底误差分别20.963／20.641cm和0／8.808cm，原35cm门槛不变。高处独立初始化或站立不能替代这类道路往返证明；其他屋顶、室内及楼梯入口仍须按证据区分。

全清单轨迹采样含{falling:,}个MOVE_FALLING状态，不能把所有记录写成全程步行；通过端点另核对步行落地。上例两段的全部采样步行结论仅适用于该实例。

![双向高度实走实例](../../../Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/PureMapSurveyV1/Visuals/PURE_MAP_HEIGHT_CONNECTION_V2_20261007.svg)

## 负面记录如何使用

| 原因 | 数量 |
| --- | --- |
{reasons_zh}

负面表示该项未按本规格建立移动或站立通过证据，不能一概写成“地形不可达”。例如AlreadyAtGoal没有启动一条实走，端点拒绝、源重叠及不完整查询也各有含义。源拒绝缓存注明没有新物理尝试，不能把缓存行数当成独立失败人数。通过组是实测证据图，不是完整物理隔绝分类；导航外碰撞表面、未加载内容和未经识别的室内另列未知。

已读并保留[ML001–ML007失败索引](../../../Failures/README.md)。ML005污染400条不纳入；ML006旧中心规格7,311条仅诊断，不能合并；仅保留有哈希且源等价的旧负面。V12车辆移动失败只准入排除区外11,633项前缀，12后续记录及一个初始化隔离。ML007的API、旋转对象地址误判及诊断重入崩溃原样保留；V17数值快照／近车控制通过后才续测。V18停止实际迟于预期，远处11637重复一次的事实保留，同静态夹具前缀独立审计后不再重测。详见[静态补充](PURE_MAP_STATIC_VEHICLE_PLAN_20261007_ZH.md)及[历史检查点](PURE_MAP_TEST_RESULT_EXECUTION_NOTES_20261007_ZH.md)。

## 后续布局条件

所有现有坐标仍只是测试点，**本次未选择最终生成点、任务点或盟德位置**。后续从实走证据组提出巴黎范围候选，再验证原FP／盟军／德军规格、同时小队、窄口及任务往返；不能把默认人物单独通过直接当作小队通过。

广泛批次是NullRHI固定20ms应用步长／80ms世界步长、600cm/s的模拟；不建立实时渲染、FPS、原角色300cm/s或可见接触验收。正式9ff地图仍2,720,990字节，采用授权本地3显示DLL增量，其余700项及模型、手指、枪械、动作、AI、Catalog保持精确。无正式保存、资产采用、提交或发布。原始JSON／日志／模板／PNG／工具二进制留在私有Evidence/PureMapSurveyV1；入口{args.identity}的audit_v1.json记录完整批次链及哈希。
'''
en = f'''# Pure map connectivity test result

{stamp}. The [workflow](PURE_MAP_TEST_WORKFLOW_20261007.md) preceded execution.
**All28,684 finite scheduled cases are recorded and independently audited; this
does not establish whole-map mutual connectivity.** [Chinese review](PURE_MAP_TEST_RESULT_20261007_ZH.md) is synchronized.

| Verified scope | Result |
| --- | --- |
| Isolated environment | 8 loaded levels/23,037 blockers;15 gameplay actors removed only in unsaved memory;runtime original player/NPC/project gameplay actors0. Car obstacle retained with test-only stationarity. |
| Full-domain export | 11,828 active/exported tiles/invalid0;27,836 polygons/15,543 regions/47,176 directed edges/2,231 query SCCs. |
| Finite coverage | {counts[0]:,} records:{counts[1]:,} passed movements/{counts[2]:,} standing-only passes/{counts[3]:,} negatives or cached rejections;unmeasured0. Controls excluded from denominator. |
| Height/narrow tags | Height:{vertical['completed']:,} recorded/{vertical['passed']:,} passed/{vertical['failed']:,} negative. Narrow:{narrow['completed']:,} recorded/{narrow['passed']:,} passed/{narrow['failed']:,} negative. Tags overlap and are not additive denominators. |
| Physical evidence | Native Character/AIController/Manny unarmed display;per-case request/controller/SUCCESS/actual endpoint/CurrentFloor audit. Passed feet Z{feet[0]/100:.2f}..{feet[1]/100:.2f}m. |
| Directed groups | {len(a['physical_component_sizes']):,} SCCs of passed-edge endpoints only;largest sizes:{groups}. Other surfaces are not proven physically disconnected. |
| Closure | Latest ownedPID{a['exit']['owned_pid']} exit0/strict log0/703 exact;static car component/bounds/collision exact/simulation disabled/max drift0. |

Ten-metre tiles and reciprocal native adjacency preserve XYZ/exact-poly surface,
raw center and directed connections.1,049 tileXY locations contain stacked
regions; do not round Z or call Recast layers0–5 six floors.2.5D aids reading while
UE retains3D navigation. Existing BasicShapes/outer proxy supports are test geometry,
not automatically a Paris mission area.

![Finite movement and height evidence](../../../Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/PureMapSurveyV1/Visuals/PURE_MAP_FINITE_RESULT_20261007.svg)

## Height conclusion

At least one actual height connector is walked both ways. Case07537 walks from
road feet0.90m to6.99m;07910 returns from7.04m to0.90m. Both nativeSUCCESS/
request match/all sampled states walking. Endpoint XY/feet errors20.963/20.641cm
and0/8.808cm meet unchanged35cm limits. High initialization/standing alone is not
an access route; other roofs/interiors/stair entrances remain evidence-dependent.

The full case trajectory samples include{falling:,} MOVE_FALLING observations;
do not describe every record as entirely walking. Passed endpoints separately
require walking/grounded state. The all-sampled-walking claim above is limited
to those two example legs.

![Reciprocal height example](../../../Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/PureMapSurveyV1/Visuals/PURE_MAP_HEIGHT_CONNECTION_V2_20261007.svg)

## Negative interpretation

| Reason | Count |
| --- | --- |
{reasons_en}

Negatives mean no pass under this specification, not automatically impassable
terrain. AlreadyAtGoal starts no traversal; endpoint/source/query rejections have
different meanings. Cached source rows are not new physical attempts. Evidence
SCCs do not prove complete separation;navigation-external collision, unloaded
content and unidentified interiors remain unknown.

Read and preserve [ML001–ML007](../../../Failures/README.md). ML005's400 polluted
records are excluded;ML006's7311 center-only cases are diagnostics, not merged.
Only authenticated equivalent old negatives survive. V12 admits11633 remote
prefix cases only, quarantines12 suffix records/one initialization. ML007 retains
API/repr-address/parity and diagnostic reentrancy failures;V17 numeric snapshots
and near-car gate precede continuation. V18's stop was later than assumed and
remote11637 was repeated once;retain the fact and audit its same-fixture prefix
before reuse. See [static plan](PURE_MAP_STATIC_VEHICLE_PLAN_20261007.md) and
[chronological notes](PURE_MAP_TEST_RESULT_EXECUTION_NOTES_20261007.md).

## Subsequent layout

All existing positions remain temporary tests;no final spawn/objective/Allied/
German placement is chosen. Propose Paris candidates from evidence groups, then
test original FP/Allied/German profiles, simultaneous squad bottlenecks and mission
returns. A solitary default character pass is not squad acceptance.

Broad execution uses NullRHI fixed20ms application/80ms world steps and600cm/s;
no real-time rendering/FPS/original300cm/s/visible-contact acceptance. Formal9ff
map remains2,720,990bytes;authorized3-display-DLL local increment adopted, other
700 rows/models/fingers/guns/actions/AI/Catalog exact. No formal save/adoption/
commit/publication. Raw receipts/logs/template/PNG/binaries stay private in
Evidence/PureMapSurveyV1;{args.identity}/audit_v1.json authenticates the full chain.
'''
(docs / "PURE_MAP_TEST_RESULT_20261007_ZH.md").write_text(zh, encoding="utf-8")
(docs / "PURE_MAP_TEST_RESULT_20261007.md").write_text(en, encoding="utf-8")
handoff = root / "HANDOFF.md"
text = handoff.read_text(encoding="utf-8")
start = text.index("**Pure-map survey priority")
end = text.index("**Map connectivity priority", start)
history = docs / "PURE_MAP_HANDOFF_HISTORY_20261007.md"
assert not history.exists()
history.write_text("Archived dated checkpoints, superseded by final finite audit.\n\n"+text[start:end], encoding="utf-8")
block = f'''**Pure-map finite survey COMPLETE — {stamp}:**
Workflow written first, isolated default-character execution and independent
audit now cover all28684 scheduled cases: {counts[1]} movements passed,
{counts[2]} standing-only passes, {counts[3]} negatives/cached rejections, unmeasured0.
Not whole-map mutual connectivity.8levels/23037blockers/15gameplay removals;
runtime project gameplay0.11828active/exported tiles/invalid0,27836polygons,
15543regions/47176directed query edges/2231query SCCs. Passed-edge evidence SCC
count{len(a['physical_component_sizes'])};unknown/standing-only are not disconnected proof.
Read PURE_MAP_TEST_WORKFLOW/RESULT and Chinese reviews, static plan and ML001–007.
Keep XYZ/exact-poly surfaces/directed connectors;2.5D is recording only.
Actual road0.90m↔surface7m reciprocal native walking passes;not all floors.
Existing BasicShapes/proxy supports are not final Paris mission area. Existing
roster coordinates remain temporary;no final player/NPC/objective placement.
V12 only authenticated remote11633prefix;12 suffix cases/one init quarantined.
V17 numeric static-car fixture passes,car collision retained/component bounds
exact/drift0. V18 typed interruption really followed14 cases,remote11637 repeated
once;raw fact retained/audited before continued prefix. Source V5/core/profile
parity and prior negative caches retained;old polluted/center-only positives excluded.
Latest{args.identity} owned{a['exit']['owned_pid']} normal exit0/log0/current703exact,
audit_v1 full coverage. Adopt authorized LOCAL3recoil DLLs;other700/map9ff/models/
fingers/weapons/actions/AI/Catalog exact. No formal save/adoption/commit/publication.
NullRHI fixed20/80ms600cm/s is simulation,notFPS/original-role/squad/MVP acceptance.
Next select candidate connected Paris scope and test original roles/squad/mission
returns. Raw files/template/PNG/binaries private;full chain in entry/audit_v1.json.
Owned native slot RELEASED;check actual processes before later entry and preserve
foreign/user editors. Chronological prior checkpoints archived in MissionLoopV1.

'''
handoff.write_text(text[:start]+block+text[end:], encoding="utf-8")
print(json.dumps({"identity": args.identity, "counts": counts, "written": "bilingual final results and own HANDOFF block"}))
