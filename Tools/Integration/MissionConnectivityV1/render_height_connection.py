"""Standard plot of an audited reciprocal native walking height connection."""
import argparse
import hashlib
import json
import sys
from pathlib import Path
root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(root / "tmp/pure-map-survey-v1/plot-deps"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

parser = argparse.ArgumentParser()
parser.add_argument("identity")
parser.add_argument("svg", type=Path)
parser.add_argument("png", type=Path)
args = parser.parse_args()
directory = root / "Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/PureMapSurveyV1" / args.identity
audit = json.loads((directory / "audit_v1.json").read_text())
assert audit["status"] == "pass_receipt_audit"
report = json.loads((directory / "survey.json").read_text())
cases = [next(c for c in report["cases"] if c["id"] == name) for name in ("case_07537", "case_07910")]
assert (cases[0]["from"], cases[0]["to"]) == (cases[1]["to"], cases[1]["from"])
for c in cases:
    assert c["status"] == "passed" and "SUCCESS" in c["completion"]["result"].upper()
    assert c["xy_cm"] <= 35 and c["foot_error_cm"] <= 35
    assert all("WALKING" in s["mode"] for s in c["samples"])
font_manager.fontManager.addfont("C:/Windows/Fonts/msyh.ttc")
plt.rcParams.update({"font.family": "Microsoft YaHei", "axes.unicode_minus": False, "font.size": 12})
fig, ax = plt.subplots(figsize=(10, 5.5), layout="constrained")
fig.patch.set_facecolor("#f5f7fa")
colors = ("#16814b", "#2777ba")
for c, color, label in zip(cases, colors, ("道路 → 较高表面", "较高表面 → 道路")):
    time = [0.] + [s["game_seconds"]-c["start_game_seconds"] for s in c["samples"]] + [c["elapsed_game_seconds"]]
    heights = [c["standing"]["foot_z_cm"]/100] + [s["foot_z_cm"]/100 for s in c["samples"]] + [(c["final_body_cm"][2]-96.5)/100]
    ax.plot(time, heights, color=color, marker="o", linewidth=2.5, label=label+f" · {c['id']}")
    ax.annotate(f"{heights[-1]:.2f}m", (time[-1], heights[-1]), xytext=(-5, 12), textcoords="offset points", ha="right", color=color)
ax.set(xlabel="各段开始后的模拟游戏时间（秒）", ylabel="实际胶囊脚底 Z（地图坐标，米）", ylim=(0, 8))
ax.grid(alpha=.25)
ax.legend(loc="center left", frameon=False)
fig.suptitle("已实测的双向高度连接：约 0.90m 与 7.0m", fontsize=19)
ax.set_title("两段原生 SUCCESS · 匹配请求编号 · 采样均为步行 · 端点原门槛通过", fontsize=12, pad=14)
fig.text(.5, -.03, "这是一个真实 Z 轴往返实例；不等于所有屋顶、室内或楼梯已可达。位置仅作测试。", ha="center", fontsize=11)
for p in (args.svg, args.png):
    p.parent.mkdir(parents=True, exist_ok=True)
    assert not p.exists()
fig.savefig(args.svg, bbox_inches="tight")
fig.savefig(args.png, dpi=160, bbox_inches="tight")
receipt = {"identity": args.identity, "audit_sha256": hashlib.sha256((directory / "audit_v1.json").read_bytes()).hexdigest(),
    "cases": [c["id"] for c in cases], "not_full_floor_access_or_final_layout": True,
    "matplotlib_version": matplotlib.__version__, "png_sha256": hashlib.sha256(args.png.read_bytes()).hexdigest()}
args.png.with_suffix(".json").write_text(json.dumps(receipt, indent=2)+"\n", encoding="utf-8")
print(args.png)
