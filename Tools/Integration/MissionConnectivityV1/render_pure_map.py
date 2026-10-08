"""Render measured native navigation and case evidence; never label it a floor plan."""
import argparse
import html
import json
from collections import Counter
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("evidence", type=Path)
parser.add_argument("output", type=Path)
parser.add_argument("--remote-prefix", type=Path)
args = parser.parse_args()
survey = json.loads((args.evidence / "survey.json").read_text())
if args.remote_prefix:
    from vehicle_prefix import verify
    original, count = verify(args.evidence.parent, args.remote_prefix)
    assert original == survey
    survey["cases"] = survey["cases"][:count]
    survey["status"] = "audited_remote_prefix_only_full_survey_incomplete"
    survey["summary"].update({"completed_cases": count,
        "passed_cases": sum(c["status"] == "passed" for c in survey["cases"]),
        "standing_passes": sum(c["status"] == "standing_passed" for c in survey["cases"]),
        "failed_cases": sum(c["status"] == "failed" for c in survey["cases"])})
graph = json.loads((args.evidence / "graph.json").read_text())
nav = json.loads((args.evidence / "navmesh.json").read_text())
regions = {r["id"]: r for r in graph["regions"]}
polys = {p["id"]: p for p in nav["polygons"]}
main = set(graph["query_components"][0])
parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="1020" viewBox="0 0 1500 1020">',
         '<rect width="1500" height="1020" fill="#f5f7fa"/>',
         '<style>text{font-family:"Microsoft YaHei",Arial,sans-serif;fill:#23334b} .label{font-size:18px} .small{font-size:15px}</style>']


def text(x, y, s, size=18, color="#23334b"):
    parts.append(f'<text x="{x}" y="{y}" font-size="{size}" style="fill:{color}">{html.escape(str(s))}</text>')


def map_panel(x, y, w, h, region_ids, bounds, title):
    parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="white" stroke="#d4dce7"/>')
    text(x+20, y+32, title, 22)
    lo, hi = bounds
    scale = min((w-70)/(hi[0]-lo[0]), (h-100)/(hi[1]-lo[1]))
    ox, oy = x+w/2, y+50+(h-80)/2
    cx, cy = (lo[0]+hi[0])/2, (lo[1]+hi[1])/2
    def xy(v): return ox+(v[0]-cx)*scale, oy-(v[1]-cy)*scale
    for r_id in region_ids:
        r = regions[r_id]
        color = "#a2c6e4" if r_id in main else "#9c8ab5"
        for p_id in r["polygons"]:
            points = " ".join("%.2f,%.2f" % xy(v) for v in polys[p_id]["vertices_cm"])
            parts.append(f'<polygon points="{points}" fill="{color}" stroke="{color}" stroke-width="0.4"/>')
    for case in survey["cases"]:
        if case["from"] not in region_ids or case["to"] not in region_ids: continue
        color = "#16814b" if case["status"] in ("passed", "standing_passed") else "#d54842"
        trail = [s["body_cm"] for s in case.get("samples", [])]
        if len(trail) > 1:
            points = " ".join("%.2f,%.2f" % xy(v) for v in trail)
            parts.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="1.4"/>')
        a, b = xy(case["source_cm"]), xy(case["goal_cm"])
        if case["status"] != "passed":
            parts.append(f'<circle cx="{a[0]:.2f}" cy="{a[1]:.2f}" r="3" fill="{color}"/>')
    text(x+20, y+h-22, f"X/Y范围 {(hi[0]-lo[0])/100:.0f} × {(hi[1]-lo[1])/100:.0f} m；横向X / 纵向Y", 15)


def bounds_for(region_ids):
    vertices = [v for n in region_ids for p in regions[n]["polygons"] for v in polys[p]["vertices_cm"]]
    lo = [min(v[i] for v in vertices) for i in range(2)]
    hi = [max(v[i] for v in vertices) for i in range(2)]
    padding = max(hi[i]-lo[i] for i in range(2))*.04+100
    return [v-padding for v in lo], [v+padding for v in hi]


text(32, 45, "纯地图测试：导航表面与原生实走记录", 30)
text(32, 76, "不含原玩家 / NPC / 武器；当前摆放点不是最终出生或任务点", 20)
text(32, 105, f"回执：{args.evidence.name} · {survey['status']}", 15)
map_panel(25, 130, 710, 565, set(regions), bounds_for(regions), "全部已生成表面 · 俯视 XY")
parts.append('<rect x="755" y="130" width="720" height="565" rx="12" fill="white" stroke="#d4dce7"/>')
text(775, 162, "高度记录 · X / 实际 Z（坐标尺度不同）", 22)
points = [r["point_cm"] for r in regions.values()]
x_lo, x_hi = min(v[0] for v in points), max(v[0] for v in points)
z_lo, z_hi = min(v[2] for v in points), max(v[2] for v in points)
def xz(v): return 815+(v[0]-x_lo)/(x_hi-x_lo)*625, 625-(v[2]-z_lo)/(z_hi-z_lo)*405
for i in range(6):
    altitude = z_lo+(z_hi-z_lo)*i/5
    y = 625-i/5*405
    parts.append(f'<line x1="815" y1="{y}" x2="1440" y2="{y}" stroke="#e3e8ef"/>')
    text(769, y+5, f"{altitude/100:.0f}m", 13)
for identifier, r in regions.items():
    x, y = xz(r["point_cm"])
    color = "#6ca4ce" if identifier in main else "#9c8ab5"
    parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="1.25" fill="{color}" opacity="0.6"/>')
for case in survey["cases"]:
    trail = [s["body_cm"][:2]+[s["foot_z_cm"]] for s in case.get("samples", [])]
    if len(trail) > 1:
        trail_points = " ".join("%.2f,%.2f" % xz(v) for v in trail)
        color = "#16814b" if case["status"] == "passed" else "#d54842"
        parts.append(f'<polyline points="{trail_points}" fill="none" stroke="{color}" stroke-width="1.2"/>')
text(815, 651, f"X {x_lo/100:.0f} 至 {x_hi/100:.0f} m；每点对应一个表面区域", 15)
text(775, 678, "高度点按真实Z展开；不是楼层编号或已证明的楼梯连接", 16)
stats = graph["summary"]
result = survey["summary"]
text(35, 732, f"导航多边形 {stats['polygons']:,} / 表面区域 {stats['regions']:,} / 查询分量 {stats['query_components']:,}", 22)
text(35, 767, f"有限用例 {result['planned_cases']:,}；已记录 {result['completed_cases']:,}；实走通过 {result['passed_cases']:,}；站立通过 {result['standing_passes']:,}；失败 {result['failed_cases']:,}", 21)
colors = [("#a2c6e4", "最大查询分量"), ("#9c8ab5", "其他查询分量"), ("#16814b", "通过轨迹 / 站立点"), ("#d54842", "失败轨迹 / 源点")]
for i, (color, label) in enumerate(colors):
    x = 35+i*340
    parts.append(f'<rect x="{x}" y="791" width="20" height="20" fill="{color}"/>')
    text(x+30, 809, label, 17)
z = [v[2] for p in polys.values() for v in p["vertices_cm"]]
stacked = Counter(tuple(r["tile"][:2]) for r in regions.values())
text(35, 853, f"生成表面实际Z：{min(z)/100:.2f} ~ {max(z)/100:.2f} m；同XY含多个区域的瓦片：{sum(n>1 for n in stacked.values()):,}", 20)
text(35, 889, "2.5D记录保留真实XYZ、Recast表面身份和有向连接；同XY叠置不等于楼层，存在高度也不证明楼梯可走。", 18)
text(35, 925, "查询连通来自导航邻接；绿色记录实走轨迹或站立点，站立不证明连通。未测 / 失败区域仍不能选作任务区。", 18)
text(35, 960, "范围仅覆盖已加载环境生成的导航；导航外碰撞表面、未加载内容、室内与小队通行仍需单独核查。", 18)
parts.append("</svg>")
args.output.parent.mkdir(parents=True, exist_ok=True)
assert not args.output.exists(), "Keep unique visual evidence"
args.output.write_text("\n".join(parts), encoding="utf-8")
print(args.output)
