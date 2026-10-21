"""Render two editable proposal sketches without changing survey/source images.

Run from any directory with Python 3.10+. Output is self-contained SVG: the
unchanged team-authored 25 cm survey is embedded beneath vector annotations.
No engine, asset registry, runtime data, or user files are modified.
"""

from base64 import b64encode
from collections import deque
from hashlib import sha256
from html import escape
import json
from pathlib import Path
import struct
import zlib


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Docs/Proposal/Visuals"
SOURCE = ROOT / "Docs/Images/MissionLoopV1/PARIS_GRID_25CM_EXPANDED_L0_20261007.png"
MAP_BYTES = SOURCE.read_bytes()
MAP_DATA = "data:image/png;base64," + b64encode(MAP_BYTES).decode("ascii")
LAYOUT = json.loads((OUT / "adjustment-jingdi-20261020-layout.json").read_text(encoding="utf-8"))
W, H = 1280, 1100
MX, MY, SCALE = 80, 174, 4
XMIN, XMAX, YMIN, YMAX = 5, 145, -225, -18
MW, MH = (XMAX - XMIN) * SCALE, (YMAX - YMIN) * SCALE
INK, MUTED = "#173735", "#56716a"
COLORS = [s["color"] for s in LAYOUT["stages"]]
STAGES = [s["label_m"] for s in LAYOUT["stages"]]
ROUTES = [s["route_m"] for s in LAYOUT["stages"]]


def survey_component():
    """Read the exact 1-bit PNG and find its cardinal white-cell component."""
    assert sha256(MAP_BYTES).hexdigest() == LAYOUT["source_sha256"]
    offset, compressed = 8, []
    while offset < len(MAP_BYTES):
        length = struct.unpack(">I", MAP_BYTES[offset:offset + 4])[0]
        kind, data = MAP_BYTES[offset + 4:offset + 8], MAP_BYTES[offset + 8:offset + 8 + length]
        offset += length + 12
        if kind == b"IHDR":
            width, height, depth, colour, _, _, interlace = struct.unpack(">IIBBBBB", data)
        elif kind == b"IDAT":
            compressed.append(data)
    assert (width, height, depth, colour, interlace) == (4032, 4032, 1, 0, 0)
    raw, stride, rows, previous, offset = zlib.decompress(b"".join(compressed)), 504, [], bytearray(504), 0
    for _ in range(height):
        filter_kind = raw[offset]
        row = bytearray(raw[offset + 1:offset + stride + 1])
        offset += stride + 1
        for x in range(stride):
            left, above, upper_left = row[x - 1] if x else 0, previous[x], previous[x - 1] if x else 0
            if filter_kind == 1:
                row[x] = (row[x] + left) & 255
            elif filter_kind == 2:
                row[x] = (row[x] + above) & 255
            elif filter_kind == 3:
                row[x] = (row[x] + (left + above) // 2) & 255
            elif filter_kind == 4:
                predicted = left + above - upper_left
                dl, da, du = abs(predicted - left), abs(predicted - above), abs(predicted - upper_left)
                row[x] = (row[x] + (left if dl <= da and dl <= du else above if da <= du else upper_left)) & 255
            else:
                assert filter_kind == 0
        rows.append(row)
        previous = row
    x0, y0 = int((XMIN + 504) * 4), int((504 - YMAX) * 4)
    mask = bytearray(int(MW * MH))
    for y in range(int(MH)):
        for x in range(int(MW)):
            mask[y * int(MW) + x] = bool(rows[y0 + y][(x0 + x) // 8] & (128 >> ((x0 + x) % 8)))
    start = grid_point(ROUTES[0][0])
    component, queue = bytearray(len(mask)), deque([start])
    component[start] = 1
    while queue:
        index = queue.popleft()
        x, y = index % int(MW), index // int(MW)
        neighbours = []
        if x:
            neighbours.append(index - 1)
        if x + 1 < MW:
            neighbours.append(index + 1)
        if y:
            neighbours.append(index - int(MW))
        if y + 1 < MH:
            neighbours.append(index + int(MW))
        for neighbour in neighbours:
            if mask[neighbour] and not component[neighbour]:
                component[neighbour] = 1
                queue.append(neighbour)
    assert sum(component) == LAYOUT["route_component_pixel_count"]
    return component


def grid_point(point):
    x, y = point
    return int((YMAX - y) * 4) * int(MW) + int((x - XMIN) * 4)


def validate_layout(component):
    for i, stage in enumerate(LAYOUT["stages"]):
        assert 10 <= stage["enemy_count"] <= 12
        assert len(stage["enemy_positions_m"]) == sum(stage["groups"]) == stage["enemy_count"]
        if i:
            assert ROUTES[i - 1][-1] == ROUTES[i][0], "Stage transition is disconnected"
        for a, b in zip(stage["route_m"], stage["route_m"][1:]):
            assert a[0] == b[0] or a[1] == b[1], "Route must preserve cardinal survey segments"
            count = round((abs(a[0] - b[0]) + abs(a[1] - b[1])) * 4)
            for n in range(count + 1):
                point = [a[0] + (b[0] - a[0]) * n / max(1, count), a[1] + (b[1] - a[1]) * n / max(1, count)]
                assert component[grid_point(point)], (stage["id"], point, "route enters black/unknown cell")
        for point in stage["enemy_positions_m"]:
            assert component[grid_point(point)], (stage["id"], point, "enemy marker is not in connected white cells")
            left, bottom = stage["area_polygon_m"][0]
            right, top = stage["area_polygon_m"][2]
            assert left < point[0] < right and bottom < point[1] < top
    assert sum(s["enemy_count"] for s in LAYOUT["stages"]) == LAYOUT["total_enemies"] == 66


COMPONENT = survey_component()
validate_layout(COMPONENT)


def surface_clip():
    commands = []
    for y in range(int(MH)):
        x = 0
        while x < MW:
            if not COMPONENT[y * int(MW) + x]:
                x += 1
                continue
            start = x
            while x < MW and COMPONENT[y * int(MW) + x]:
                x += 1
            length = x - start
            commands.append(f"M{MX + start} {MY + y}h{length}v1h-{length}z")
    return '<clipPath id="survey-surface" clipPathUnits="userSpaceOnUse"><path d="' + ''.join(commands) + '"/></clipPath>'


def xy(point):
    x, y = point
    return MX + (x - XMIN) * SCALE, MY + (YMAX - y) * SCALE


def text(parts, x, y, value, size=18, color=INK, weight=400, anchor="start"):
    parts.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" '
                 f'font-weight="{weight}" text-anchor="{anchor}">{escape(value)}</text>')


def rect(parts, x, y, width, height, fill="white", stroke="none", rx=14, extra=""):
    parts.append(f'<rect x="{x}" y="{y}" width="{width}" height="{height}" '
                 f'rx="{rx}" fill="{fill}" stroke="{stroke}" {extra}/>')


def line(parts, points, color, width=3, dash="", extra=""):
    pts = " ".join(f"{x:.2f},{y:.2f}" for x, y in points)
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    parts.append(f'<polyline points="{pts}" fill="none" stroke="{color}" '
                 f'stroke-width="{width}" stroke-linecap="round" '
                 f'stroke-linejoin="round"{dash_attr} {extra}/>')


def begin(title, subtitle, desc):
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
             f'viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">',
             f'<title id="title">{escape(title)}</title>',
             f'<desc id="desc">{escape(desc)}</desc>',
             '<metadata>Source: Docs/Images/MissionLoopV1/PARIS_GRID_25CM_EXPANDED_L0_20261007.png; '
             f'SHA256 {sha256(MAP_BYTES).hexdigest()}. Crop X=5..145m, Y=-225..-18m. '
             'Vector annotations are proposed design, not accepted movement or a deletion inventory.</metadata>',
             '<defs>',
             surface_clip(),
             '<marker id="route-arrow" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto" markerUnits="userSpaceOnUse"><path d="M0 0L9 4.5L0 9Z" fill="white"/></marker>',
             '<pattern id="hatch" width="12" height="12" patternUnits="userSpaceOnUse">'
             '<path d="M-3 3L3-3M0 12L12 0M9 15L15 9" stroke="#7a9690" stroke-width="1" opacity=".35"/></pattern>']
    for i, color in enumerate(COLORS):
        parts.append(f'<marker id="arrow{i}" markerWidth="8" markerHeight="8" refX="6" refY="4" '
                     f'orient="auto" markerUnits="userSpaceOnUse"><path d="M0 0L8 4L0 8Z" fill="{color}"/></marker>')
    parts.extend(['</defs>', '<g font-family="Segoe UI, Arial, sans-serif">'])
    rect(parts, 0, 0, W, H, "#f4f7f2", rx=0)
    text(parts, 52, 39, "PARIS STREET COMBAT  /  JINGDI  /  20 OCT 2026", 13, MUTED, 600)
    text(parts, 52, 88, title, 31, INK, 700)
    text(parts, 52, 122, subtitle, 17, MUTED)
    rect(parts, 42, 148, 620, 898, "white", "#dce5dc", 16)
    rect(parts, MX, MY, MW, MH, "#071210", rx=0)
    # Nested viewBox crops the original PNG without resampling or changing its bytes.
    sx, sy = (XMIN + 504) * 4, (504 - YMAX) * 4
    parts.append(f'<svg x="{MX}" y="{MY}" width="{MW}" height="{MH}" '
                 f'viewBox="{sx} {sy} {MW} {MH}"><image width="4032" height="4032" '
                 f'href="{MAP_DATA}" opacity=".82"/></svg>')
    for x in range(20, 141, 20):
        px, _ = xy((x, YMAX))
        line(parts, [(px, MY), (px, MY + MH)], "#7b9b90", 0.7, extra='opacity=".3"')
        text(parts, px, MY + MH + 21, str(x), 12, MUTED, anchor="middle")
    for y in range(-20, -221, -20):
        _, py = xy((XMIN, y))
        line(parts, [(MX, py), (MX + MW, py)], "#7b9b90", 0.7, extra='opacity=".3"')
        text(parts, MX - 8, py + 4, str(y), 12, MUTED, anchor="end")
    text(parts, MX + MW - 6, MY + MH + 39, "UE +X →  /  metres", 12, MUTED, anchor="end")
    text(parts, MX + 8, MY + 22, "↑ UE +Y", 13, "#c7ddd4", 600)
    return parts


def excluded_shortcut(parts):
    for point in [(111, -187), (120, -147)]:
        x, y = xy(point)
        parts.append(f'<circle cx="{x}" cy="{y}" r="9" fill="#271816" fill-opacity=".9"/>')
        line(parts, [(x - 5, y - 5), (x + 5, y + 5)], "#ff8a80", 2.3)
        line(parts, [(x - 5, y + 5), (x + 5, y - 5)], "#ff8a80", 2.3)


def mission_areas(parts, enemies=False):
    for stage in LAYOUT["stages"]:
        points = ' '.join(f'{x},{y}' for x, y in map(xy, stage["area_polygon_m"]))
        parts.append(f'<polygon points="{points}" fill="{stage["color"]}" opacity=".58" clip-path="url(#survey-surface)"/>')
        parts.append(f'<polygon points="{points}" fill="none" stroke="{stage["color"]}" stroke-width="1.7" stroke-dasharray="7 4"/>')
    for route in ROUTES:
        points = list(map(xy, route))
        line(parts, points, "#122a26", 6.5)
        line(parts, points, "#ffffff", 2.7)
        # The final cardinal segment supplies a direction arrow without shortcuts.
        line(parts, points[-2:], "#ffffff", 2.7, extra='marker-end="url(#route-arrow)"')
    if enemies:
        for stage in LAYOUT["stages"]:
            for number, point in enumerate(stage["enemy_positions_m"], 1):
                x, y = xy(point)
                parts.append(f'<path d="M{x} {y - 4.8}l-4.5 8h9z" fill="{stage["color"]}" stroke="#15241f" stroke-width="1.35">'
                             f'<title>{stage["id"]}-E{number:02d}: proposed enemy</title></path>')
    excluded_shortcut(parts)
    for i in range(6):
        stage_badge(parts, i)


def stage_badge(parts, i, position=None):
    x, y = xy(position or STAGES[i])
    parts.append(f'<circle cx="{x}" cy="{y}" r="16" fill="#102723" stroke="{COLORS[i]}" stroke-width="2.5"/>')
    text(parts, x, y + 5, f"C{i + 1}", 13, COLORS[i], 700, "middle")


def footer(parts):
    text(parts, 52, 1070, "Coloured streets: proposed encounter areas. Black: blocked, unknown or unadmitted. Triangles: proposed enemy positions.", 12, MUTED)
    text(parts, 52, 1090, "Route is continuous through white survey centres in 2D; native ground, NavMesh and squad passage still require checks.", 12, MUTED)
    parts.extend(['</g>', '</svg>'])
    return "\n".join(parts) + "\n"


def boundary_map():
    p = begin("P0 / Match playable terrain to the 2D map",
              "Six coloured mission areas, a connected survey route and a matching player-centred minimap.",
              "Top-down survey sketch inspired by image 1's missing minimap terrain and image 3's route. "
              "Six coloured mission areas follow a continuous white-cell route around the far-eastern bypass. "
              "A magnified minimap uses the same survey coordinates as its highlighted window.")
    mission_areas(p)
    gx, gy = xy(ROUTES[-1][-1])
    text(p, gx - 10, gy - 16, "GOAL", 12, "#eeffe9", 700, "end")
    # A world-coordinate window, copied exactly in the illustrative HUD inset.
    player = (120.875, -120.875)
    wx, wy = xy((player[0] - 20, player[1] + 20))
    rect(p, wx, wy, 160, 160, "#79cfff", "#79cfff", 0,
         'fill-opacity=".12" stroke-width="2.5" stroke-dasharray="5 4"')
    px, py = xy(player)
    p.append(f'<path d="M{px} {py - 10}l-7 18 7-4 7 4Z" fill="#b7eeff" stroke="#152f3c" stroke-width="1.5"/>')
    line(p, [(wx + 160, wy + 70), (678, wy + 70), (716, 594), (844, 594)], "#4c98b3", 1.8, "4 4")
    rect(p, 690, 174, 538, 250, "white", "#dce5dc")
    text(p, 714, 211, "01 / Fix the mismatch in image 1", 23, INK, 700)
    text(p, 714, 248, "Every reachable mission street should", 20)
    text(p, 714, 276, "appear on the map around the player.", 20)
    text(p, 714, 319, "Extend map coverage as the route grows.", 18, MUTED)
    text(p, 714, 348, "Block access beyond the intended area.", 18, MUTED)
    text(p, 714, 394, "Colour marks the intended encounter streets;", 16, MUTED)
    text(p, 714, 415, "dashed borders define planning areas.", 16, MUTED)
    rect(p, 690, 448, 538, 300, "white", "#dce5dc")
    text(p, 714, 485, "02 / One coordinate system", 23, INK, 700)
    cx, cy, radius = 940, 600, 88
    p.append(f'<defs><clipPath id="radar"><circle cx="{cx}" cy="{cy}" r="{radius}"/></clipPath></defs>')
    p.append('<g clip-path="url(#radar)">')
    sx = (player[0] - 20 + 504) * 4
    sy = (504 - player[1] - 20) * 4
    p.append(f'<svg x="{cx - radius}" y="{cy - radius}" width="176" height="176" '
             f'viewBox="{sx} {sy} 160 160"><image width="4032" height="4032" href="{MAP_DATA}"/></svg>')
    p.append(f'<rect x="{cx - radius}" y="{cy - radius}" width="176" height="176" fill="#53adbb" opacity=".12"/>')
    p.append('</g>')
    p.append(f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="none" stroke="#4c98b3" stroke-width="3"/>')
    p.append(f'<path d="M{cx} {cy - 11}l-8 20 8-4 8 4Z" fill="#b7eeff" stroke="#152f3c" stroke-width="1.5"/>')
    text(p, cx, cy - 66, "+Y", 13, "white", 700, "middle")
    text(p, 1044, 577, "Same terrain", 17, INK, 600)
    text(p, 1044, 603, "Same player", 17, INK, 600)
    text(p, 1044, 629, "Same window", 17, INK, 600)
    text(p, 714, 724, "Blue square → matching illustrative HUD window", 17, MUTED)
    rect(p, 690, 772, 538, 274, "white", "#dce5dc")
    text(p, 714, 810, "03 / Six areas, 10–12 enemies each", 23, INK, 700)
    for i, stage in enumerate(LAYOUT["stages"]):
        x, y = 714 + (i % 3) * 167, 839 + (i // 3) * 47
        rect(p, x, y, 34, 26, stage["color"], rx=5)
        text(p, x + 17, y + 19, stage["id"], 13, "#102723", 700, "middle")
        text(p, x + 45, y + 19, str(stage["enemy_count"]) + " enemies", 15)
    text(p, 714, 967, "Outside: retain scenery and restrict access.", 16, MUTED)
    text(p, 714, 994, "Remove only unwanted working instances.", 16, MUTED)
    text(p, 714, 1021, "Red × marks the excluded old shortcut.", 16, MUTED)
    return footer(p)


def campaign_map():
    p = begin("P1 / Six missions from the bridge to the upper right",
              "Revised eastern bypass / six coloured areas / 10–12 proposed enemy positions in every area.",
              "Six differently coloured encounter areas and 66 individual enemy markers. "
              "The continuous white-cell route crosses the bridge, detours east to avoid the old disconnected shortcut, "
              "then advances north through the city entry, central junction and northern street to the northeastern goal. "
              "All markers and area limits remain proposals; native traversal has not been tested.")
    mission_areas(p, enemies=True)
    start_x, start_y = xy((18, -201))
    text(p, start_x, start_y, "START / BRIDGE", 12, COLORS[0], 700)
    goal_x, goal_y = xy(ROUTES[-1][-1])
    p.append(f'<circle cx="{goal_x}" cy="{goal_y}" r="5" fill="white" stroke="#173735" stroke-width="1.5"/>')
    text(p, goal_x - 9, goal_y - 13, "GOAL", 12, "#fbb5d0", 700, "end")
    titles = [s["title"] for s in LAYOUT["stages"]]
    details = [
        ["Expand the campaign bridge encounter to 10.", "Three groups: 4 + 3 + 3."],
        ["Detour via X ≈ 132–137 m, not the old gap.", "Secure the bypass; groups: 4 + 3 + 3."],
        ["Turn north-west into the T2 entry street.", "Junction + patrol; groups: 4 + 4 + 4."],
        ["Advance from Y ≈ −110 to −83 m.", "Clear the junction; groups: 4 + 3 + 3."],
        ["Continue north from Y ≈ −83 to −47 m.", "Dispersed defenders; groups: 4 + 4 + 4."],
        ["Finish on the street near (110, −35 m).", "Final clear + objective; groups: 4 + 4 + 4."],
    ]
    counts = [s["enemy_count"] for s in LAYOUT["stages"]]
    for i, title in enumerate(titles):
        top = 174 + i * 112
        rect(p, 690, top, 538, 100, "white", "#dce5dc")
        rect(p, 690, top + 11, 5, 78, COLORS[i], rx=2)
        rect(p, 706, top + 17, 41, 31, "#173831", rx=8)
        text(p, 726.5, top + 39, f"C{i + 1}", 15, COLORS[i], 700, "middle")
        text(p, 761, top + 37, title, 19, INK, 700)
        text(p, 761, top + 62, details[i][0], 16, MUTED)
        text(p, 761, top + 84, details[i][1], 16, MUTED)
        text(p, 1208, top + 37, str(counts[i]), 20, INK, 700, "end")
    rect(p, 690, 860, 538, 186, "#e5eee4", "#cbdac9")
    text(p, 714, 896, "66 enemies total / 10–12 in every area", 21, INK, 700)
    line(p, [(716, 925), (755, 925)], "#173735", 6)
    line(p, [(716, 925), (755, 925)], "white", 2.7)
    text(p, 774, 931, "Continuous 2D survey route", 17)
    p.append('<path d="M736 951l-6 10h12z" fill="#f4b94e" stroke="#173735" stroke-width="1.3"/>')
    text(p, 774, 966, "Each triangle = 1 proposed enemy", 17)
    text(p, 736, 1001, "×", 25, "#c7443e", 700, "middle")
    text(p, 774, 1001, "Old disconnected shortcut excluded", 17)
    text(p, 714, 1030, "Coloured fill = proposed mission streets.", 15, MUTED)
    return footer(p)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    figures = {
        "adjustment-jingdi-20261020-playable-map.svg": boundary_map(),
        "adjustment-jingdi-20261020-campaign-route.svg": campaign_map(),
    }
    for name, svg in figures.items():
        destination = OUT / name
        destination.write_text(svg, encoding="utf-8", newline="\n")
        print(destination.relative_to(ROOT), destination.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
