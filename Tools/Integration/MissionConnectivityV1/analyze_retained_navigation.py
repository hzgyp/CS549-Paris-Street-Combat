"""Export historical query coverage and heights; never claim current traversal."""
import argparse
import hashlib
import json
import subprocess
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
STORE = ROOT / "Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--identity", required=True)
    args = parser.parse_args()
    assert args.identity.replace("_", "").isalnum(), "Unsafe identity"
    out = STORE / "Evidence/MissionConnectivityV1" / args.identity
    svg = ROOT / "Docs/Development/MissionLoopV1/Visuals" / (args.identity + ".svg")
    assert not out.exists() and not svg.exists(), "Preserve prior evidence"
    source = STORE / "Evidence/CityGameplay20261002/NavigationFoundation/fresh_v4/result.json"
    raw = source.read_bytes()
    data = json.loads(raw)
    groups = {"complete": [], "partial": [], "unprojected": [], "identity": []}
    for sample in data["samples"]:
        point = sample.get("projected_cm")
        route = sample.get("path") or {}
        name = ("unprojected" if point is None else "complete" if route.get("valid") and not route.get("partial")
                else "partial" if route.get("partial") else "identity")
        groups[name].append(sample)
    heights = [p[2] for s in groups["complete"] for p in s["path"]["points_cm"]]
    end_heights = [s["projected_cm"][2] for s in groups["complete"]]
    summary = {
        "identity": args.identity, "source": source.relative_to(ROOT).as_posix(),
        "source_sha256": hashlib.sha256(raw).hexdigest(), "source_map": data["before_map"],
        "status": "historical_query_analysis_not_current_map_or_physical_acceptance",
        "counts": {key: len(values) for key, values in groups.items()},
        "complete_endpoint_z_cm": [min(end_heights), max(end_heights)],
        "complete_path_node_z_cm": [min(heights), max(heights)],
        "path_node_count_with_repeated_shared_segments": len(heights),
        "recorded_nav_bounds": data["volume"], "recorded_sampling": data["sampling"],
        "starts": data["starts"],
        "limitations": ["Old map epoch; current actor placement is not revalidated here",
                        "Only player-to-destination queries; reverse/all-pairs/physical routes untested",
                        "Low-height first-hit ray and 10m XY grid can miss stacked/narrow surfaces",
                        "Height range is not proof of floors or stairs", "No objective location selected"],
    }
    # Source-authored vector survey figure; use the bundled renderer, no installs.
    elements = ['<svg xmlns="http://www.w3.org/2000/svg" width="1300" height="760" viewBox="0 0 1300 760" role="img" aria-labelledby="title desc">',
                '<title id="title">Historical Paris query coverage and actual surface heights</title>',
                '<desc id="desc">Old 10m samples: 391 complete, 1157 partial, 51 unprojected and one identity point. Height values do not prove usable floors. This is not current map or physical traversal acceptance.</desc>',
                '<rect width="1300" height="760" fill="#ffffff"/>']

    def text(x, y, value, size=17, anchor="start", color="#22323e"):
        elements.append(f'<text x="{x}" y="{y}" fill="{color}" font-family="Microsoft YaHei, sans-serif" font-size="{size}" text-anchor="{anchor}">{escape(value)}</text>')

    def line(x1,y1,x2,y2,color="#dce2e7",width=1):
        elements.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"/>')

    def circle(x,y,r,color):
        elements.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r}" fill="{color}"/>')

    origin = data["starts"][0]["projected_cm"]
    palette = {"complete": "#167b55", "partial": "#b85a2b", "unprojected": "#858585", "identity": "#2258ad"}
    labels = {"complete": "路径查询完整", "partial": "仅部分路径", "unprojected": "未投影", "identity": "起点自身"}
    origins = (80,710)
    scale=500/440

    def xy(point,panel):
        return origins[panel]+((point[0]-origin[0])/100+220)*scale, 690-((point[1]-origin[1])/100+200)*scale

    text(650,37,"先保留高度，再判断分层",27,"middle")
    text(650,66,"旧样本只查玩家向外的路径，不能据此宣告全图互通",18,"middle")
    text(330,107,"连通查询状态",23,"middle")
    text(960,107,"完整查询终点的真实高度",23,"middle")
    for panel in range(2):
        x0=origins[panel]
        for value in (-200,-100,0,100,200):
            gx=x0+(value+220)*scale
            gy=690-(value+200)*scale
            line(gx,190,gx,690)
            line(x0,gy,x0+500,gy)
            text(gx,711,str(value),14,"middle")
            text(x0-12,gy+5,str(value),14,"end")
        elements.append(f'<rect x="{x0}" y="190" width="500" height="500" fill="none" stroke="#697b88"/>')
        text(x0+250,739,"相对历史玩家起点 X（米）；纵轴为 Y（米）",15,"middle")
    legend_x=80
    for name in ("complete","partial","unprojected","identity"):
        circle(legend_x,136,4,palette[name])
        text(legend_x+11,142,f"{labels[name]} {len(groups[name])}",15)
        legend_x += (160 if name in ("complete","partial") else 112)
    for name in ("unprojected", "partial", "complete", "identity"):
        points = [s.get("projected_cm") or s["ground_cm"] for s in groups[name]]
        for point in points:
            px,py=xy(point,0)
            circle(px,py,2.5 if name != "identity" else 5,palette[name])
    points = [s["projected_cm"] for s in groups["complete"]]
    stops=((53,55,142),(33,145,140),(253,231,37))
    def height_color(z):
        f=max(0,min(1,(z-60)/(401-60)))*2
        index=min(1,int(f)); alpha=f-index
        return '#'+''.join(f'{round(stops[index][i]*(1-alpha)+stops[index+1][i]*alpha):02x}' for i in range(3))
    for point in points:
        px,py=xy(point,1)
        circle(px,py,3.2,height_color(point[2]))
    for i,value in enumerate((60,150,250,401)):
        x0=720+i*123
        circle(x0,136,5,height_color(value))
        text(x0+12,142,f"Z {value/100:.2f} m",15)
    sx,sy=xy(origin,0)
    line(139,337,sx,sy,"#1d315b",1.8)
    text(105,324,"历史六人起点",17)
    highest = max(points, key=lambda p:p[2])
    hx,hy=xy(highest,1)
    line(796,292,hx,hy,"#1d315b",1.8)
    text(735,251,f"最高终点 Z={highest[2]/100:.2f} m",17)
    text(735,278,"尚未证明楼梯或可用楼层",17)
    text(650,171,"2026-10-02 · 10 m 网格 · 旧地图 4c77844f… · 导航点采样图，不是道路底图",16,"middle")
    elements.append('</svg>')
    out.mkdir(parents=True)
    svg.parent.mkdir(parents=True, exist_ok=True)
    svg.write_text('\n'.join(elements)+'\n',encoding='utf-8')
    deps=Path('C:/Users/hzgyp/.cache/codex-runtimes/codex-primary-runtime/dependencies/node')
    subprocess.run([str(deps/'bin/node.exe'),'-e',
        'require(process.argv[1])(process.argv[2]).png().toFile(process.argv[3]).catch(e=>{console.error(e);process.exitCode=1});',
        str(deps/'node_modules/sharp'),str(svg),str(out/'retained-query-coverage.png')],check=True)
    summary["visuals"] = []
    for path in (svg, out / "retained-query-coverage.png"):
        summary["visuals"].append({"path": path.relative_to(ROOT).as_posix(), "size_bytes":path.stat().st_size,
                                   "sha256":hashlib.sha256(path.read_bytes()).hexdigest()})
    (out / "analysis.json").write_text(json.dumps(summary, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"counts":summary["counts"], "path_z_cm":summary["complete_path_node_z_cm"],
                      "output":str(out), "svg":str(svg)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
