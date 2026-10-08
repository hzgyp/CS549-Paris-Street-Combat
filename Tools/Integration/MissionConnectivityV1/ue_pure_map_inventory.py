"""P0: isolate saved environment in memory and inventory all Pawn blockers."""
import json
import os
import sys
import time
import traceback
from collections import Counter
from pathlib import Path
import unreal

ROOT = Path(os.environ["CS549_PURE_ROOT"])
OUT = Path(os.environ["CS549_PURE_OUT"])
sys.path.insert(0, str(ROOT / "Tools/Integration/NPCInteractionV1"))
from common import guard_rows, guards_match
rows = guard_rows()
assert len(rows) == 703 and guards_match(rows)
report = {"identity": OUT.name, "status": "initializing", "errors": [], "current_guards": len(rows),
          "map_saved": False, "pie_started": False, "nav_rebuilt": False,
          "positions_are_temporary_tests": True, "removed": [], "blockers": []}
started = time.monotonic()
try:
    assert unreal.EditorLevelLibrary.load_level("/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1")
    editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    world = editor.get_editor_world()
    initial = list(actors.get_all_level_actors())
    report["all_loaded_level_counts"] = dict(Counter(a.get_outer().get_path_name() for a in initial))
    for a in initial:
        path = a.get_class().get_path_name()
        if isinstance(a, unreal.Character) or path.startswith(("/Game/ParisCombat/", "/Script/Paris")) or "GripPolicy" in path:
            report["removed"].append({"label": a.get_actor_label(), "class": path})
            assert actors.destroy_actor(a)
    current = list(actors.get_all_level_actors())
    assert not any(isinstance(a, unreal.Character) for a in current)
    assert not any(a.get_class().get_path_name().startswith(("/Game/ParisCombat/", "/Script/Paris")) or
                   "GripPolicy" in a.get_class().get_path_name() for a in current)
    report["remaining_class_counts"] = dict(Counter(a.get_class().get_path_name() for a in current))
    report["remaining_pawns"] = [{"label": a.get_actor_label(), "class": a.get_class().get_path_name()}
                                  for a in current if isinstance(a, unreal.Pawn)]
    def xyz(v): return [float(v.x), float(v.y), float(v.z)]
    block_members = [(name, getattr(unreal.CollisionResponseType, name)) for name in dir(unreal.CollisionResponseType)
                     if name.upper().endswith("BLOCK") and isinstance(getattr(unreal.CollisionResponseType, name), unreal.CollisionResponseType)]
    assert len(block_members) == 1, "Unique reflected native collision Block member required"
    report["collision_block_binding"] = "CollisionResponseType." + block_members[0][0]
    for a in current:
        for c in a.get_components_by_class(unreal.PrimitiveComponent):
            if c.get_collision_enabled() == unreal.CollisionEnabled.NO_COLLISION:
                continue
            if c.get_collision_response_to_channel(unreal.CollisionChannel.ECC_PAWN) != block_members[0][1]:
                continue
            if isinstance(c, unreal.BrushComponent) and isinstance(a, unreal.NavMeshBoundsVolume):
                continue
            origin, extent, sphere = unreal.SystemLibrary.get_component_bounds(c)
            if max(extent.x, extent.y, extent.z) < .01:
                continue
            report["blockers"].append({"label": a.get_actor_label(), "class": a.get_class().get_path_name(),
                "component": c.get_path_name(), "level": a.get_outer().get_path_name(),
                "origin_cm": xyz(origin), "extent_cm": xyz(extent),
                "profile": str(c.get_collision_profile_name()), "collision": str(c.get_collision_enabled()),
                "mesh": c.static_mesh.get_path_name() if isinstance(c, unreal.StaticMeshComponent) and c.static_mesh else None})
    assert report["blockers"], "No environment blockers inventoried"
    report["collision_bounds_cm"] = {"min": [min(b["origin_cm"][i]-b["extent_cm"][i] for b in report["blockers"]) for i in range(3)],
                                     "max": [max(b["origin_cm"][i]+b["extent_cm"][i] for b in report["blockers"]) for i in range(3)]}
    nav = [n for n in unreal.ObjectIterator(unreal.NavigationSystemV1)
           if "Default__" not in n.get_path_name() and n.get_outer() == world]
    assert len(nav) == 1
    meshes = [a for a in current if isinstance(a, unreal.RecastNavMesh)]
    assert len(meshes) == 1
    report["retained_navigation"] = {"receiver": nav[0].get_path_name(),
        "profile": {k: str(meshes[0].get_editor_property(k)) for k in
                    ("agent_radius", "agent_height", "agent_max_slope", "runtime_generation", "tile_size_uu")},
        "python_surface_api": [n for n in dir(meshes[0]) if any(s in n.lower() for s in ("poly", "tile", "neighbor", "export"))]}
    character = unreal.get_default_object(unreal.Character)
    movement = character.character_movement
    report["native_character_defaults"] = {"class": character.get_class().get_path_name(),
        "radius_cm": character.capsule_component.get_unscaled_capsule_radius(),
        "half_height_cm": character.capsule_component.get_unscaled_capsule_half_height(),
        "movement": {k: float(movement.get_editor_property(k)) for k in
                     ("max_walk_speed", "max_step_height", "max_acceleration", "gravity_scale")},
        "walkable_floor_angle": movement.get_walkable_floor_angle()}
    report["current_map"] = next(r for r in rows if r["path"] == "Unreal/ParisStreetCombat/Content/ParisCombat/Maps/LV_ParisStreetCombat_V1.umap")
    report["summary"] = {"loaded_levels": len(report["all_loaded_level_counts"]), "removed_gameplay_actors": len(report["removed"]),
        "environment_blocking_components": len(report["blockers"]), "original_characters_remaining": 0,
        "physical_or_full_survey_acceptance": False}
except Exception:
    report["errors"].append(traceback.format_exc())
report["protected_bytes_unchanged"] = guards_match(rows)
if not report["protected_bytes_unchanged"]: report["errors"].append("Guard mismatch")
report["elapsed_wall_seconds"] = time.monotonic()-started
report["status"] = "failed" if report["errors"] else "pass_p0_inventory_only"
(OUT / "inventory.json").write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
unreal.SystemLibrary.quit_editor()
