"""World-coordinate grid contracts; no Unreal or private assets at import time."""
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

CELL_CM = 100.0
PROFILE = {"radius_cm": 34.0, "half_height_cm": 96.23316,
           "step_cm": 45.0, "slope_degrees": 44.7651, "floor_gap_cm": 2.15}


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""): h.update(block)
    return h.hexdigest()


def grid_spec(nav):
    vertices = [v for p in nav["polygons"] for v in p["vertices_cm"]]
    lo = [math.floor(min(v[i] for v in vertices) / CELL_CM) * CELL_CM for i in range(2)]
    hi = [math.ceil(max(v[i] for v in vertices) / CELL_CM) * CELL_CM for i in range(2)]
    return {"cell_cm": CELL_CM, "xmin_cm": lo[0], "ymax_cm": hi[1],
            "xmax_cm": hi[0], "ymin_cm": lo[1],
            "columns": int(round((hi[0]-lo[0])/CELL_CM)),
            "rows": int(round((hi[1]-lo[1])/CELL_CM)),
            "row_direction": "-Y", "column_direction": "+X",
            "meaning": "Cell center; white does not admit every position in the square"}


def cell_xy(spec, col, row):
    if not (0 <= col < spec["columns"] and 0 <= row < spec["rows"]):
        raise ValueError("Cell outside grid")
    return [spec["xmin_cm"]+(col+.5)*spec["cell_cm"],
            spec["ymax_cm"]-(row+.5)*spec["cell_cm"]]


def world_cell(spec, x, y):
    col = math.floor((x-spec["xmin_cm"])/spec["cell_cm"])
    row = math.floor((spec["ymax_cm"]-y)/spec["cell_cm"])
    return (col, row) if 0 <= col < spec["columns"] and 0 <= row < spec["rows"] else None


def polygon_cells(poly, spec):
    """Inclusive convex-polygon center test. Boundary aliases are retained."""
    import numpy as np
    vs = np.array(poly["vertices_cm"], dtype=float)
    if len(vs) < 3: raise ValueError("Invalid navigation polygon")
    size = spec["cell_cm"]
    c0 = max(0, math.ceil((vs[:, 0].min()-spec["xmin_cm"])/size-.5-1e-9))
    c1 = min(spec["columns"]-1, math.floor((vs[:, 0].max()-spec["xmin_cm"])/size-.5+1e-9))
    r0 = max(0, math.ceil((spec["ymax_cm"]-vs[:, 1].max())/size-.5-1e-9))
    r1 = min(spec["rows"]-1, math.floor((spec["ymax_cm"]-vs[:, 1].min())/size-.5+1e-9))
    if c1 < c0 or r1 < r0: return []
    cs, rs = np.meshgrid(np.arange(c0, c1+1), np.arange(r0, r1+1))
    xs = spec["xmin_cm"]+(cs+.5)*size
    ys = spec["ymax_cm"]-(rs+.5)*size
    positive = np.ones(cs.shape, dtype=bool)
    negative = positive.copy()
    for a, b in zip(vs, np.roll(vs, -1, axis=0)):
        cross = (b[0]-a[0])*(ys-a[1])-(b[1]-a[1])*(xs-a[0])
        positive &= cross >= -1e-5
        negative &= cross <= 1e-5
    keep = positive | negative
    return list(zip(cs[keep].tolist(), rs[keep].tolist()))


def candidate_rows(nav, spec):
    assert nav["active_tiles"] == nav["exported_tiles"] and nav["invalid_records"] == 0
    assert nav["sampling_version"] == "native_specific_polygon_surface_v2"
    rows = []
    omitted = []
    for p in nav["polygons"]:
        cells = polygon_cells(p, spec)
        if not cells: omitted.append(p["id"])
        for col, row in cells:
            x, y = cell_xy(spec, col, row)
            rows.append({"id": len(rows), "c": col, "r": row, "p": p["id"],
                         "xyz": [x, y, p["surface_cm"][2]]})
    return rows, omitted


def write_candidates(nav, spec, directory):
    rows, omitted = candidate_rows(nav, spec)
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "candidates.jsonl"
    if path.exists(): raise FileExistsError("Preserve finite grid candidates")
    with path.open("w", encoding="utf-8") as f:
        for row in rows: f.write(json.dumps(row, separators=(",", ":"))+"\n")
    meta = {"spec": spec, "candidate_count": len(rows), "omitted_polygons": omitted,
            "candidate_sha256": digest(path), "profile": PROFILE}
    (directory/"candidate_manifest.json").write_text(json.dumps(meta, indent=2)+"\n", encoding="utf-8")
    return rows, meta


def connected_components(nodes, edges):
    """Only reciprocal admitted links count as an undirected planning component."""
    parent = {n: n for n in nodes}
    def find(n):
        while parent[n] != n:
            parent[n] = parent[parent[n]]
            n = parent[n]
        return n
    pairs = set(edges)
    for a, b in pairs:
        if (b, a) not in pairs: continue
        aa, bb = find(a), find(b)
        if aa != bb: parent[max(aa, bb)] = min(aa, bb)
    groups = defaultdict(list)
    for n in nodes: groups[find(n)].append(n)
    return sorted(groups.values(), key=lambda g: (-len(g), min(g)))
