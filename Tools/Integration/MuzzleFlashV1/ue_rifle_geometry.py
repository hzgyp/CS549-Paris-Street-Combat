"""Read current saved native rifle selection and static source geometry; no PIE/save."""
import json
import os
import sys
import traceback
from pathlib import Path
import unreal

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import BASE, guards, intake_rows, write

OUT = BASE / os.environ["CS549_MUZZLE_ID"]
report = {"identity": OUT.name, "errors": [], "rifles": [], "map_saved": False,
          "mesh_saved": False, "pie_started": False}
try:
    report["guard_count"] = len(guards())
    report["original_intake_count"] = len(intake_rows())
    assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level("/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1")
    for actor in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
        path = actor.get_class().get_path_name()
        if path in ("/Script/ParisNPCGripV15.ParisAlliedGripPolicy", "/Script/ParisNPCGripV15.ParisGermanGripPolicy"):
            mesh = actor.get_editor_property("RifleMesh")
            row = json.loads(unreal.ParisMuzzleFlashLibrary.inspect_rifle_geometry(mesh))
            assert row["valid"] and len(row["vertices"]) > 100
            row["selected_by"] = {"class": path, "label": actor.get_actor_label()}
            report["rifles"].append(row)
    assert len(report["rifles"]) == 2 and len({r["path"] for r in report["rifles"]}) == 2
except Exception:
    report["errors"].append(traceback.format_exc())
finally:
    try:
        report["guard_count"] = len(guards())
        report["original_intake_count"] = len(intake_rows())
    except Exception:
        report["errors"].append(traceback.format_exc())
    report["status"] = "failed_rifle_geometry_preserve" if report["errors"] else "pass_saved_rifle_geometry_read_only"
    write(OUT / "result.json", report)
    unreal.SystemLibrary.quit_editor()
