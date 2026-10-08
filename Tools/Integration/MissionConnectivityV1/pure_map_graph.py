"""Finite native-tile surface graph and deterministic physical edge schedule."""
import math
from collections import defaultdict, deque


def area(poly):
    vs = poly["vertices_cm"]
    return abs(sum(a[0]*b[1]-b[0]*a[1] for a, b in zip(vs, vs[1:]+vs[:1]))) / 2


def components(adjacency):
    """Iterative Kosaraju, preserving directed/one-way topology."""
    reverse = {n: [] for n in adjacency}
    for node, neighbors in adjacency.items():
        for target in neighbors:
            reverse[target].append(node)
    seen, order = set(), []
    for root in adjacency:
        if root in seen: continue
        seen.add(root)
        stack = [(root, iter(adjacency[root]))]
        while stack:
            node, iterator = stack[-1]
            target = next(iterator, None)
            if target is None:
                order.append(node); stack.pop()
            elif target not in seen:
                seen.add(target); stack.append((target, iter(adjacency[target])))
    result, assigned = [], set()
    for root in reversed(order):
        if root in assigned: continue
        part, pending = [], [root]
        assigned.add(root)
        while pending:
            node = pending.pop(); part.append(node)
            for target in reverse[node]:
                if target not in assigned:
                    assigned.add(target); pending.append(target)
        result.append(sorted(part))
    return sorted(result, key=lambda part: (-len(part), part[0]))


def build(export):
    assert not export.get("error") and export["invalid_records"] == 0
    assert export["active_tiles"] == export["exported_tiles"]
    assert export["sampling_version"] == "native_specific_polygon_surface_v2"
    polys = {p["id"]: p for p in export["polygons"]}
    assert len(polys) == len(export["polygons"]) and polys
    assert all(n["to"] in polys for p in polys.values() for n in p["neighbors"]), "Export has missing neighbor"
    buckets = defaultdict(set)
    for p in polys.values():
        buckets[(p["tile_x"], p["tile_y"], p["tile_layer"])].add(p["id"])
    mapping, regions = {}, []
    # Native Recast layers are explicit surface identities, never rounded floor heights.
    for tile in sorted(buckets):
        available = buckets[tile].copy()
        while available:
            root = min(available); available.remove(root)
            group, pending = [root], [root]
            while pending:
                p = polys[pending.pop()]
                for portal in p["neighbors"]:
                    target = portal["to"]
                    # Same-tile union only for reciprocal native adjacency.
                    if target in available and any(n["to"] == p["id"] for n in polys[target]["neighbors"]):
                        available.remove(target); group.append(target); pending.append(target)
            identifier = "region_%05d" % len(regions)
            representative = max(group, key=lambda n: (area(polys[n]), n))
            z = [v[2] for n in group for v in polys[n]["vertices_cm"]]
            r = {"id": identifier, "tile": list(tile), "polygons": sorted(group),
                 "representative_poly": representative, "point_cm": polys[representative]["surface_cm"],
                 "raw_center_cm": polys[representative]["center_cm"],
                 "area_cm2": sum(area(polys[n]) for n in group), "z_range_cm": [min(z), max(z)]}
            regions.append(r)
            for n in group: mapping[n] = identifier
    assert len(mapping) == len(polys)
    index = {r["id"]: r for r in regions}
    edges = {}
    for p in polys.values():
        source = mapping[p["id"]]
        for portal in p["neighbors"]:
            target = mapping[portal["to"]]
            if source == target: continue
            edge = edges.setdefault((source, target), {"from": source, "to": target, "portals": []})
            edge["portals"].append({"from_poly": p["id"], **portal})
    adjacency = {r["id"]: set() for r in regions}
    for source, target in edges: adjacency[source].add(target)
    groups = components(adjacency)
    tree, visited = set(), set()
    for group in groups:
        root = max(group, key=lambda n: (index[n]["area_cm2"], n))
        allowed = set(group); visited.add(root); queue = deque([root])
        while queue:
            source = queue.popleft()
            for target in sorted(adjacency[source]):
                if target in allowed and target not in visited and (target, source) in edges:
                    tree.add((source, target)); tree.add((target, source))
                    visited.add(target); queue.append(target)
        # SCCs with only directed cycles need all directed edges to witness connectivity.
        if not allowed <= visited:
            tree.update((a, b) for a, b in edges if a in allowed and b in allowed)
            visited.update(allowed)
    required = set(tree)
    for key, edge in edges.items():
        a, b = (index[n] for n in key)
        edge["min_portal_width_cm"] = min(p["width_cm"] for p in edge["portals"])
        edge["vertical"] = abs(a["point_cm"][2]-b["point_cm"][2]) > 50
        edge["max_portal_width_cm"] = max(p["width_cm"] for p in edge["portals"])
        edge["narrow"] = edge["max_portal_width_cm"] < 140
        edge["reciprocal_query_neighbor"] = key[::-1] in edges
        if edge["vertical"] or edge["narrow"] or not edge["reciprocal_query_neighbor"]:
            required.add(key)
    def distance(key):
        a, b = (index[n]["point_cm"] for n in key)
        return math.dist(a, b)
    # Normal-time gate: shortest reasonably nonzero reciprocal flat/wide pair.
    largest = set(groups[0])
    candidates = [key for key in tree if key[0] in largest and key[1] in largest
                  and key[::-1] in tree and 100 <= distance(key) <= 1800
                  and not edges[key]["vertical"] and not edges[key]["narrow"]]
    assert candidates, "No independent short reciprocal early gate"
    early = ("region_09517", "region_09829")
    assert early in candidates, "Previously accepted LV_Proxy lifecycle pair must remain eligible"
    schedule = [early, early[::-1]] + sorted(required - {early, early[::-1]})
    cases = [{"id": "case_%05d" % i, "from": a, "to": b,
              "source_cm": index[a]["point_cm"], "goal_cm": index[b]["point_cm"],
              "source_poly": index[a]["representative_poly"], "target_poly": index[b]["representative_poly"],
              "early_gate": i < 2, "tree_edge": (a, b) in tree,
              "vertical": edges[(a, b)]["vertical"], "narrow": edges[(a, b)]["narrow"], "kind": "movement"}
             for i, (a, b) in enumerate(schedule)]
    covered_sources = {a for a, b in schedule}
    for identifier in sorted(set(index)-covered_sources):
        r = index[identifier]
        cases.append({"id": "case_%05d" % len(cases), "from": identifier, "to": identifier,
                      "source_cm": r["point_cm"], "goal_cm": r["point_cm"],
                      "source_poly": r["representative_poly"], "target_poly": r["representative_poly"],
                      "early_gate": False, "tree_edge": False, "vertical": False, "narrow": False,
                      "kind": "standing_only"})
    return {"scope": "All native polygons mapped; exact-poly grounded representatives and finite connecting edges",
            "sampling_version": export["sampling_version"],
            "native_tile_size_cm": 1000, "polygon_count": len(polys), "regions": regions,
            "polygon_to_region": mapping, "directed_edges": list(edges.values()), "query_components": groups,
            "cases": cases, "summary": {"polygons": len(polys), "mapped_polygons": len(mapping),
              "regions": len(regions), "directed_edges": len(edges), "query_components": len(groups),
              "required_physical_cases": len(cases), "tree_directed_edges": len(tree),
              "isolated_regions": sum(not adjacency[n] for n in adjacency),
              "standing_only_cases": sum(c["kind"] == "standing_only" for c in cases)}}
