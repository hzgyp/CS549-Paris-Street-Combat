"""Combine retained query layers with actual bounded height trajectories."""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/MissionConnectivityV1"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--identity", required=True)
    args = parser.parse_args()
    assert args.identity.replace("_", "").isalnum()
    query_path = BASE / "current_query_v1_20261007/query.json"
    walk_path = BASE / "height_walk_v1_20261007/traversal.json"
    failed_path = BASE / "current_traversal_v1_20261007/traversal.json"
    query = json.loads(query_path.read_text(encoding="utf-8"))
    walk = json.loads(walk_path.read_text(encoding="utf-8"))
    failed = json.loads(failed_path.read_text(encoding="utf-8"))
    assert walk["source_query_sha256"] == digest(query_path)
    assert not walk["errors"] and walk["protected_bytes_unchanged"]
    assert walk["summary"]["highest_sample_walked_both_directions"]
    assert len(walk["moves"]) == 2 and len(walk["completions"]) == 2
    assert all("SUCCESS" in c["result"] for c in walk["completions"])
    assert failed["status"] == "failed" and len(failed["moves"]) == 8
    original = ROOT / "Docs/Development/MissionLoopV1/Visuals/current_visual_v1_20261007.svg"
    svg_path = original.with_name(args.identity + ".svg")
    out = BASE / args.identity
    assert not svg_path.exists() and not out.exists(), "Preserve prior evidence"
    svg = original.read_text(encoding="utf-8")
    svg = svg.replace('height="850" viewBox="0 0 1280 850"', 'height="1010" viewBox="0 0 1280 1010"', 1)
    svg = svg.replace('<rect width="1280" height="850"', '<rect width="1280" height="1010"', 1)
    svg = svg.replace("Query evidence, not physical walking or confirmed floors.",
                      "Query matrix only. Two independent native height legs pass; occupied-anchor cycle fails leg eight. Floors remain unverified.")
    origin = query["actors"][0]["projected_cm"]
    scale = 560 / 440

    def xy(point):
        return 70 + ((point[0] - origin[0]) / 100 + 220) * scale, 742 - ((point[1] - origin[1]) / 100 + 200) * scale

    trajectory = [m["start_cm"] for m in walk["moves"][:1]]
    for move in walk["moves"]:
        trajectory.extend(s["body_cm"] for s in move["samples"])
    points = " ".join("%.2f,%.2f" % xy(point) for point in trajectory)
    svg, replacements = re.subn(r'<polyline points="[^"]+" fill="none" stroke="#3757ac" stroke-width="2.3"/>',
                               f'<polyline points="{points}" fill="none" stroke="#3757ac" stroke-width="2.3"/>', svg)
    assert replacements == 1
    svg = svg.replace("当前结果仅为 NavMesh 查询；高处结构、身体净空、原角色实走仍须验证",
                      "蓝线：原盟军高点往返实走轨迹；右上矩阵只表示查询，全员实走尚未通过")
    panel = '''<rect x="45" y="855" width="1190" height="135" rx="10" fill="#f3f6f8"/>
<g font-family="Microsoft YaHei, sans-serif" fill="#22323e">
<text x="70" y="884" font-size="20" fill="#167b55">高度测试：出去／返回，两段原生移动成功</text>
<text x="70" y="914" font-size="17">最高目标 Z4.434m；实际脚底采样 Z0.569–4.602m</text>
<text x="70" y="944" font-size="17">高点来自破屋顶碰撞；楼梯／可用建筑楼层仍未确认</text>
<text x="70" y="974" font-size="16">原模型、握姿、动作、100生命／2/16弹药保留；没有保存地图</text>
<text x="735" y="884" font-size="20" fill="#b3452f">人员环路：第8段未到达</text>
<text x="735" y="914" font-size="17">距 Enemy2 为100.936cm，超出原80+5cm准入</text>
<text x="735" y="944" font-size="17">失败归档 ML001；不扩大容差、不改标通过</text>
<text x="735" y="974" font-size="16">任务点尚未锁定；采用 XY＋实际 Z＋表面身份</text>
</g>'''
    svg = svg.replace("</svg>", panel + "\n</svg>")
    out.mkdir(parents=True)
    svg_path.write_text(svg, encoding="utf-8")
    png = out / "current-connectivity-and-height.png"
    deps = Path("C:/Users/hzgyp/.cache/codex-runtimes/codex-primary-runtime/dependencies/node")
    subprocess.run([str(deps / "bin/node.exe"), "-e",
                    "require(process.argv[1])(process.argv[2]).png().toFile(process.argv[3]).catch(e=>{console.error(e);process.exitCode=1});",
                    str(deps / "node_modules/sharp"), str(svg_path), str(png)], check=True)
    record = {"scope": "C1 query layers plus independent two-leg height walk, not full-roster physical acceptance",
              "inputs": [{"path": p.relative_to(ROOT).as_posix(), "sha256": digest(p)}
                         for p in (query_path, walk_path, failed_path, original)],
              "visuals": [{"path": p.relative_to(ROOT).as_posix(), "sha256": digest(p), "bytes": p.stat().st_size}
                          for p in (svg_path, png)], "trajectory_samples": len(trajectory)}
    (out / "analysis.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"png": str(png), "trajectory_samples": len(trajectory)}))


if __name__ == "__main__":
    main()
