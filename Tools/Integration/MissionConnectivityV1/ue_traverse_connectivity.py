"""Unsaved geometry inspection and original-capsule native locomotion only."""
import json
import math
import os
import sys
import time
import traceback
from collections import defaultdict
from pathlib import Path
import unreal

ROOT=Path(os.environ["CS549_CONNECT_ROOT"])
sys.path.insert(0,str(ROOT/"Tools/Integration/NPCInteractionV1"))
from common import STORE, guard_rows, guards_match, digest
OUT=Path(os.environ["CS549_CONNECT_OUT"])
SOURCE=STORE/"Evidence/MissionConnectivityV1/current_query_v1_20261007/query.json"
data=json.loads(SOURCE.read_text())
assert os.environ.get("CS549_CONNECT_KIND")=="height_only","Stopped occupied-anchor fixture; require separate Height plan"
assert not data["errors"] and data["protected_bytes_unchanged"] and data["summary"]["roster_all_pairs_query_complete"]
rows=guard_rows()
assert len(rows)==703 and guards_match(rows)
editor=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
report={"identity":OUT.name,"scope":"Independent two-leg height traversal; stopped anchor cycle is not rerun","source_query_sha256":digest(SOURCE),"status":"initializing","errors":[],"completions":[],
        "moves":[],"geometry":[],"captures":[],"map_saved":False,"nav_rebuilt":False,
        "original_assets_preserved":True,"python_pose_or_behavior_driver":False,
        "arrival_tolerances_cm":{"occupied_anchor_xy":80,"unoccupied_xy":30,"foot_height":35}}
started=time.monotonic()
phase="setup"
callback=None
in_tick=False
world=nav=nav_data=None
staged=[]
roster={}
controllers={}
queue=[]
leg=None
leg_time=0
sample_time=0
perf=None
old_throttle=None
camera=None
error_pending=None
initial={}
completion_callbacks=[]


def xyz(v):return [float(v.x),float(v.y),float(v.z)]


def write():
    report["elapsed_wall_seconds"]=time.monotonic()-started
    (OUT/"traversal.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")


def finish(error=None):
    global phase,error_pending
    if error:
        error_pending=error
        report["errors"].append(error)
    if levels.is_in_play_in_editor():
        for c in controllers.values():c.stop_movement()
        levels.editor_request_end_play()
        phase="ending"
        write()
        return
    for a,hidden in staged:
        if unreal.SystemLibrary.is_valid(a):a.set_actor_hidden_in_game(hidden)
    if perf is not None:perf.set_editor_property("bThrottleCPUWhenNotForeground",old_throttle)
    if camera is not None and unreal.SystemLibrary.is_valid(camera):actors.destroy_actor(camera)
    report["protected_bytes_unchanged"]=guards_match(rows)
    if not report["protected_bytes_unchanged"]:report["errors"].append("Guard mismatch")
    report["status"]="failed" if report["errors"] else "pass_bounded_anchor_approach_and_sample_traversal_not_whole_map"
    report["summary"]={"completed_legs":sum(m.get("arrived",False) for m in report["moves"]),
        "planned_legs":2,"highest_sample_walked_both_directions":len(report["moves"])==2 and all(m.get("arrived") for m in report["moves"]),
        "resource_changes":False if not report["errors"] else "inspect_samples"}
    write()
    if callback is not None:unreal.unregister_slate_post_tick_callback(callback)
    unreal.SystemLibrary.quit_editor()
    phase="done"


def live_nav(w):
    found=[n for n in unreal.ObjectIterator(unreal.NavigationSystemV1) if "Default__" not in n.get_path_name() and n.get_outer()==w]
    assert len(found)==1,"One live world navigation instance required"
    return found[0]


def route(start,end,context):
    p=nav.call_method("FindPathToLocationSynchronously",args=(world,start,end,context,None))
    assert p and p.is_valid() and not p.is_partial(),"Current physical leg needs a complete query"
    points=list(p.get_editor_property("path_points"))
    return {"points_cm":[xyz(q) for q in points],"length_cm":sum((b-a).length() for a,b in zip(points,points[1:]))}


def resource(a):
    return [a.get_editor_property(n) for n in ("Health","LoadedAmmo","ReserveAmmo","ShotSequence","IsDead")]


def decode(hit):
    if hit is None:return {"blocking":False}
    f=hit.to_tuple()
    component=f[10]
    r={"blocking":bool(f[0]),"initial_overlap":bool(f[1]),"impact_cm":xyz(f[5]),"normal":xyz(f[7]),
       "actor":f[9].get_actor_label() if f[9] else None}
    if isinstance(component,unreal.StaticMeshComponent):
        r.update({"mesh":component.static_mesh.get_path_name() if component.static_mesh else None,
                  "profile":str(component.get_collision_profile_name()),"collision":str(component.get_collision_enabled())})
    return r


def geometry_setup(current):
    global camera
    buckets=defaultdict(list)
    for n in data["nodes"]:
        x,y,z=n["projected_cm"];buckets[(round(x),round(y))].append(n)
    probes=[]
    for ns in buckets.values():
        lo=min(ns,key=lambda n:n["projected_cm"][2]);hi=max(ns,key=lambda n:n["projected_cm"][2])
        if hi["projected_cm"][2]-lo["projected_cm"][2]>=193 and (lo["mutual_query_complete"] or hi["mutual_query_complete"]):
            probes.extend((lo,hi))
    highest=max((n for n in data["nodes"] if n["mutual_query_complete"]),key=lambda n:n["projected_cm"][2])
    probes.append(highest)
    ignored=[a for a in current if isinstance(a,unreal.Character)]
    for n in probes:
        x,y,z=n["projected_cm"]
        item={"node":n["id"],"point_cm":n["projected_cm"],"mutual_query":n["mutual_query_complete"],"surface_hits":[]}
        for complex_trace in (False,True):
            hit=unreal.SystemLibrary.line_trace_single(world,unreal.Vector(x,y,z+40),unreal.Vector(x,y,z-100),
                unreal.TraceTypeQuery.ECC_VISIBILITY,complex_trace,ignored,unreal.DrawDebugTrace.NONE,True)
            item["surface_hits"].append({"complex":complex_trace,**decode(hit)})
        report["geometry"].append(item)
    camera=actors.spawn_actor_from_class(unreal.SceneCapture2D,unreal.Vector(*highest["projected_cm"]))
    camera.set_actor_label("MissionConnectivityReadonlyCapture")
    capture=camera.get_component_by_class(unreal.SceneCaptureComponent2D)
    capture.set_editor_property("capture_source",unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
    capture.set_editor_property("capture_every_frame",False)
    capture.set_editor_property("capture_on_movement",False)
    target=unreal.RenderingLibrary.create_render_target2d(world,1200,800,unreal.TextureRenderTargetFormat.RTF_RGBA8,unreal.LinearColor(.05,.05,.05,1),False)
    capture.set_editor_property("texture_target",target)
    x,y,z=highest["projected_cm"]
    for name,pos,aim in (("highest_side",(x+1500,y-1000,z+700),(x,y,z)),
                         ("highest_overhead",(x,y,z+4000),(x,y,z)),
                         ("reachable_upper_disconnected_lower",(-4000,3500,1800),(-4000,6000,250))):
        camera.set_actor_location(unreal.Vector(*pos),False,False)
        camera.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(unreal.Vector(*pos),unreal.Vector(*aim)),False)
        capture.set_editor_property("fov_angle",75)
        for _ in range(4):capture.capture_scene()
        unreal.RenderingLibrary.export_render_target(world,target,str(OUT),name+".png")
        p=OUT/(name+".png")
        assert p.is_file() and p.stat().st_size>1000
        report["captures"].append({"path":p.relative_to(ROOT).as_posix(),"size_bytes":p.stat().st_size,"sha256":digest(p),"camera_cm":pos,"aim_cm":aim})
    actors.destroy_actor(camera);camera=None
    return highest


def tick(_delta):
    global phase,in_tick,world,nav,nav_data,perf,old_throttle,queue,leg,leg_time,sample_time,initial
    if in_tick or phase=="done":return
    in_tick=True
    try:
        assert time.monotonic()-started<600,"Bounded traversal deadline"
        if phase=="ending":
            if editor.get_game_world() is None:finish()
            return
        if phase=="setup":
            assert guards_match(rows)
            assert unreal.EditorLevelLibrary.load_level("/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1")
            world=editor.get_editor_world();nav=live_nav(world)
            current=list(actors.get_all_level_actors())
            highest=geometry_setup(current)
            perf=unreal.get_default_object(unreal.load_class(None,"/Script/UnrealEd.EditorPerformanceSettings"))
            old_throttle=perf.get_editor_property("bThrottleCPUWhenNotForeground")
            perf.set_editor_property("bThrottleCPUWhenNotForeground",False)
            for saved in data["actors"]:
                matches=[a for a in current if a.get_actor_label()==saved["id"]]
                assert len(matches)==1
                a=matches[0]
                assert resource(a)==[100.0,2,16,0,False]
                staged.append((a,a.get_editor_property("hidden")))
                a.set_actor_hidden_in_game(True)
            cycles={"PC_City_Ally1":("PC_City_Player","PC_City_Enemy3","PC_City_Enemy1","PC_City_Enemy2","PC_City_Ally2","PC_City_Ally1",
                                       "PC_City_Ally2","PC_City_Enemy2","PC_City_Enemy1","PC_City_Enemy3","PC_City_Player","PC_City_Ally1"),
                    "PC_City_Enemy1":("PC_City_Player","PC_City_Ally1","PC_City_Ally2","PC_City_Enemy2","PC_City_Enemy3","PC_City_Enemy1",
                                        "PC_City_Enemy3","PC_City_Enemy2","PC_City_Ally2","PC_City_Ally1","PC_City_Player","PC_City_Enemy1")}
            points={a["id"]:a["projected_cm"] for a in data["actors"]}
            queue=[{"pilot":"PC_City_Ally1","target":highest["id"],"goal":highest["projected_cm"],"acceptance":30},
                   {"pilot":"PC_City_Ally1","target":"home_after_height","goal":points["PC_City_Ally1"],"acceptance":30}]
            report["planned_moves"]=queue.copy()
            write();levels.editor_request_begin_play();phase="ready";return
        world=editor.get_game_world()
        if world is None:return
        now=unreal.GameplayStatics.get_time_seconds(world)
        if phase=="ready":
            assert now<15,"Original hidden bootstrap timeout"
            found={a.get_actor_label():a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.Character)}
            if not all(a["id"] in found for a in data["actors"]):return
            temp={a["id"]:found[a["id"]] for a in data["actors"]}
            cs={key:unreal.AIHelperLibrary.get_ai_controller(a) for key,a in temp.items() if key!="PC_City_Player"}
            if not all(c and c.get_editor_property("BootstrapReady") for c in cs.values()):return
            for key,a in temp.items():assert resource(a)==[100.0,2,16,0,False],("Startup changed resources",key,resource(a))
            for key,c in cs.items():
                c.call_method("PC_EnableCombat",args=(False,))
                c.get_editor_property("brain_component").stop_logic("Map connectivity locomotion fixture")
                c.stop_movement()
                sensing=temp[key].get_component_by_class(unreal.PawnSensingComponent)
                assert sensing
                sensing.set_sensing_updates_enabled(False)
                def make_observer(pilot):
                    def completed(request_id,result):
                        report["completions"].append({"pilot":pilot,"result":str(result),
                            "game_time":unreal.GameplayStatics.get_time_seconds(world),"leg_index":len(report["moves"])-1})
                    return completed
                observer=make_observer(key)
                completion_callbacks.append(observer)
                c.receive_move_completed.add_callable(observer)
            roster.update(temp);controllers.update(cs)
            initial={key:resource(a) for key,a in roster.items()}
            for a in roster.values():a.set_actor_hidden_in_game(False)
            nav=live_nav(world)
            report["startup_resources"]=initial
            report["brains_stopped_before_reveal"]=True
            phase="request";write();return
        for key,a in roster.items():assert resource(a)==initial[key],("Unexpected resource change",key,resource(a))
        if phase=="request":
            if not queue:finish();return
            specification=queue.pop(0)
            a=roster[specification["pilot"]];c=controllers[specification["pilot"]]
            goal=unreal.Vector(*specification["goal"])
            p=route(a.get_actor_location(),goal,a)
            result=c.move_to_location(goal,acceptance_radius=specification["acceptance"],stop_on_overlap=False,
                use_pathfinding=True,project_destination_to_navigation=False,can_strafe=True,allow_partial_path=False)
            assert result==unreal.PathFollowingRequestResult.REQUEST_SUCCESSFUL,str(result)
            leg={**specification,"path":p,"request":str(result),"start_cm":xyz(a.get_actor_location()),"samples":[],
                 "deadline_game_seconds":max(12,p["length_cm"]/300*2+10)}
            report["moves"].append(leg);leg_time=now;sample_time=now;phase="moving";write()
        elif phase=="moving":
            a=roster[leg["pilot"]];c=controllers[leg["pilot"]]
            body=a.get_actor_location();goal=unreal.Vector(*leg["goal"])
            xy=math.hypot(body.x-goal.x,body.y-goal.y)
            foot=body.z-a.capsule_component.get_scaled_capsule_half_height()
            dz=abs(foot-goal.z)
            status=c.get_move_status()
            if now>=sample_time:
                leg["samples"].append({"game_seconds":now,"body_cm":xyz(body),"foot_z_cm":foot,"xy_cm":xy,"dz_cm":dz,
                    "status":str(status),"speed_cm_s":a.get_velocity().length(),"frame_seconds":unreal.GameplayStatics.get_world_delta_seconds(world)})
                sample_time=now+.25
            if status==unreal.PathFollowingStatus.IDLE:
                completions=[event for event in report["completions"] if event["pilot"]==leg["pilot"] and event["leg_index"]==len(report["moves"])-1]
                assert completions and "SUCCESS" in completions[-1]["result"].upper(),("Native completion not success",completions)
                assert xy<=leg["acceptance"]+5 and dz<=35,("Native stopped short/wrong height",leg["target"],xy,dz)
                leg.update({"arrived":True,"elapsed_game_seconds":now-leg_time,"xy_cm":xy,"foot_dz_cm":dz})
                phase="request";write()
            else:
                assert now-leg_time<=leg["deadline_game_seconds"],("Native movement stalled",leg["target"],xy,dz)
                if len(leg["samples"])%12==0:write()
    except Exception:
        finish(traceback.format_exc())
    finally:
        in_tick=False


callback=unreal.register_slate_post_tick_callback(tick)
