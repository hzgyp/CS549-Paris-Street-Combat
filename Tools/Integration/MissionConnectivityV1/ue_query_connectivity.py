"""Read-only current editor-world pairwise and multi-height navigation queries."""
import json
import math
import os
import sys
import time
import traceback
from pathlib import Path
import unreal

ROOT = Path(os.environ["CS549_CONNECT_ROOT"])
sys.path.insert(0, str(ROOT / "Tools/Integration/NPCInteractionV1"))
from common import STORE, guard_rows, guards_match, digest

OUT = Path(os.environ["CS549_CONNECT_OUT"])
assert OUT.is_relative_to(STORE / "Evidence/MissionConnectivityV1")
rows = guard_rows()
assert len(rows) == 703 and guards_match(rows), "Adopt exact current ledger"
assert Path(unreal.Paths.project_dir()).resolve() == (ROOT / "Unreal/ParisStreetCombat").resolve()
report = {"identity": OUT.name, "scope": __doc__, "status": "initializing", "errors": [],
          "current_guards": len(rows), "map_saved": False, "pie_started": False, "nav_rebuilt": False,
          "actors": [], "directed_pairs": [], "nodes": [], "geometry_candidates": [],
          "limitations": ["Query evidence only; physical traversal/vertical connector inspection not passed",
                          "10m XY and 1m Z seeds can miss narrow or unsampled surfaces",
                          "No mission objective coordinates are selected"]}
started = time.monotonic()
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world = nav = nav_data = player = None
roster = []
seeds = []
seen = set()
index = 0
callback = None
phase = "setup"
in_tick = False


def xyz(v):
    return [float(v.x), float(v.y), float(v.z)]


def write():
    report["elapsed_wall_seconds"] = time.monotonic()-started
    (OUT / "query.json").write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")


def finish(error=None):
    global phase
    phase = "finished"
    if error:
        report["errors"].append(error)
    report["protected_bytes_unchanged"] = guards_match(rows)
    if not report["protected_bytes_unchanged"]:
        report["errors"].append("Current guard mismatch after queries")
    report["status"] = "failed" if report["errors"] else "complete_queries_only_physical_and_vertical_acceptance_pending"
    write()
    if callback is not None:
        unreal.unregister_slate_post_tick_callback(callback)
    unreal.SystemLibrary.quit_editor()


def project(point):
    # Use a live receiver, never the Python CLASS world-context wrapper.
    result = nav.call_method("K2_ProjectPointToNavigation", args=(world, point, nav_data, None, unreal.Vector(80,80,60)))
    if isinstance(result, tuple):
        if any(isinstance(v,bool) and not v for v in result):
            return None
        return next((v for v in result if isinstance(v,unreal.Vector)),None)
    assert result is None or isinstance(result, unreal.Vector), repr(result)
    return result


def path_record(start, end, context):
    if start is None or end is None:
        return {"valid":False, "partial":None, "points_cm":[], "reason":"endpoint_unprojected"}
    if (end-start).length() < .01:
        return {"valid":True, "partial":False, "identity":True, "length_cm":0, "points_cm":[xyz(start)]}
    route = nav.call_method("FindPathToLocationSynchronously", args=(world,start,end,context,None))
    if route is None:
        return {"valid":False, "partial":None, "points_cm":[]}
    points = list(route.get_editor_property("path_points"))
    return {"valid":bool(route.is_valid()), "partial":bool(route.is_partial()), "points_cm":[xyz(p) for p in points],
            "length_cm":sum((b-a).length() for a,b in zip(points,points[1:]))}


def complete(path):
    return path["valid"] and not path["partial"]


def setup():
    global world,nav,nav_data,player,roster,seeds,phase
    assert unreal.EditorLevelLibrary.load_level("/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1")
    world = editor.get_editor_world()
    matches = [obj for obj in unreal.ObjectIterator(unreal.NavigationSystemV1)
               if "Default__" not in obj.get_path_name() and obj.get_outer() == world]
    assert len(matches) == 1, ("Require one live editor navigation instance",[obj.get_path_name() for obj in matches])
    nav=matches[0]
    current=list(actors.get_all_level_actors())
    navs=[a for a in current if isinstance(a,unreal.RecastNavMesh)]
    volumes=[a for a in current if isinstance(a,unreal.NavMeshBoundsVolume)]
    assert len(navs)==1 and len(volumes)==1, (len(navs),len(volumes))
    nav_data=navs[0]
    report["nav_instance"]=nav.get_path_name()
    report["agent"]={k:nav_data.get_editor_property(k) for k in ("agent_radius","agent_height","agent_max_slope")}
    assert report["agent"] == {"agent_radius":34.0,"agent_height":193.0,"agent_max_slope":45.0}
    origin,extent=volumes[0].get_actor_bounds(False)
    report["nav_bounds"]={"origin_cm":xyz(origin),"extent_cm":xyz(extent),"not_mission_boundary":True}
    labels=("PC_City_Player","PC_City_Ally1","PC_City_Ally2","PC_City_Enemy1","PC_City_Enemy2","PC_City_Enemy3")
    for label in labels:
        matches=[a for a in current if a.get_actor_label()==label]
        assert len(matches)==1,label
        actor=matches[0]
        assert isinstance(actor,unreal.Character)
        body=actor.get_actor_location()
        capsule=actor.capsule_component
        foot=unreal.Vector(body.x,body.y,body.z-capsule.get_scaled_capsule_half_height())
        point=project(foot)
        roster.append((actor,point))
        report["actors"].append({"id":label,"body_cm":xyz(body),"feet_guess_cm":xyz(foot),
            "projected_cm":xyz(point) if point is not None else None,
            "capsule_radius_cm":capsule.get_scaled_capsule_radius(),"capsule_half_height_cm":capsule.get_scaled_capsule_half_height(),
            "health":actor.get_editor_property("Health"),"ammo":[actor.get_editor_property("LoadedAmmo"),actor.get_editor_property("ReserveAmmo")]})
    player=roster[0][0]
    for i,(source,start) in enumerate(roster):
        for j,(target,end) in enumerate(roster):
            if i!=j:
                report["directed_pairs"].append({"from":labels[i],"to":labels[j],"path":path_record(start,end,source)})
    # Coarse multi-height seeds are a survey window, never automatic layer IDs.
    lo=[origin.x-extent.x,origin.y-extent.y,origin.z-extent.z]
    hi=[origin.x+extent.x,origin.y+extent.y,origin.z+extent.z]
    xs=range(math.ceil(lo[0]/1000),math.floor(hi[0]/1000)+1)
    ys=range(math.ceil(lo[1]/1000),math.floor(hi[1]/1000)+1)
    zs=range(math.ceil(lo[2]/100),math.floor(hi[2]/100)+1)
    seeds=[unreal.Vector(x*1000,y*1000,z*100) for x in xs for y in ys for z in zs]
    report["sampling"]={"xy_step_cm":1000,"z_step_cm":100,"query_extent_cm":[80,80,60],"seed_count":len(seeds)}
    keywords=("stair","step","ramp","ladder","bridge","balcon","terrace","floor","roof")
    for actor in current:
        label=actor.get_actor_label()
        if any(word in label.lower() for word in keywords):
            center,size=actor.get_actor_bounds(False)
            report["geometry_candidates"].append({"label":label,"center_cm":xyz(center),"extent_cm":xyz(size),
                "name_is_not_walkability_proof":True,"extends_above_current_nav_bounds":center.z+size.z>hi[2]})
    report["current_map"] = next(r for r in rows if r["path"]=="Unreal/ParisStreetCombat/Content/ParisCombat/Maps/LV_ParisStreetCombat_V1.umap")
    write()
    phase="scan"


def tick(_delta):
    global in_tick,index
    if in_tick or phase=="finished":
        return
    in_tick=True
    try:
        assert time.monotonic()-started < 240,"Bounded query deadline"
        if phase=="setup":
            setup()
        else:
            start=roster[0][1]
            for _ in range(160):
                if index>=len(seeds):
                    break
                seed=seeds[index]
                index+=1
                point=project(seed)
                if point is None:
                    continue
                key=tuple(round(v/10) for v in xyz(point))
                if key in seen:
                    continue
                seen.add(key)
                forward=path_record(start,point,player)
                reverse=path_record(point,start,player)
                report["nodes"].append({"id":"sample_%04d" % len(report["nodes"]),"seed_cm":xyz(seed),
                    "projected_cm":xyz(point),"outward":forward,"return":reverse,
                    "mutual_query_complete":complete(forward) and complete(reverse)})
            report["processed_seeds"]=index
            if index>=len(seeds):
                mutual=[n for n in report["nodes"] if n["mutual_query_complete"]]
                z=[p[2] for n in mutual for k in ("outward","return") for p in n[k]["points_cm"]]
                report["summary"]={"directed_roster_pairs":len(report["directed_pairs"]),
                    "complete_roster_pairs":sum(complete(p["path"]) for p in report["directed_pairs"]),
                    "roster_all_pairs_query_complete":all(complete(p["path"]) for p in report["directed_pairs"]),
                    "sample_nodes":len(report["nodes"]),"mutual_query_nodes":len(mutual),
                    "mutual_path_z_cm":[min(z),max(z)] if z else None,
                    "same_xy_multiple_height_cells":sum(1 for key in {(round(n['projected_cm'][0]/100),round(n['projected_cm'][1]/100)) for n in report['nodes']}
                        if len({round(n['projected_cm'][2]/25) for n in report['nodes'] if (round(n['projected_cm'][0]/100),round(n['projected_cm'][1]/100))==key})>1)}
                finish()
            elif index % 800==0:
                write()
    except Exception:
        finish(traceback.format_exc())
    finally:
        in_tick=False


callback=unreal.register_slate_post_tick_callback(tick)
