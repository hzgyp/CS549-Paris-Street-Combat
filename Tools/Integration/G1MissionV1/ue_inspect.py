"""Read-only original map inspection before mission authoring."""
import json, os, sys, traceback
from pathlib import Path
import unreal
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Integration/NPCInteractionV1'))
from common import guard_rows,guards_match,STORE
from ue_formal_roster import actor_state
rows=guard_rows(); out=STORE/'Evidence/G1MissionV1/inspect_v1_20261008';out.mkdir(parents=True,exist_ok=False)
r={'errors':[],'guards_before':guards_match(rows),'count':len(rows)}
try:
 assert r['guards_before'] and len(rows)==703
 assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level('/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1')
 world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
 settings=world.get_world_settings();gm=settings.get_editor_property('default_game_mode')
 r['game_mode']=gm.get_path_name() if gm else None
 if gm:
  cdo=unreal.get_default_object(gm)
  r['game_mode_defaults']={n:str(cdo.get_editor_property(n)) for n in ('player_controller_class','default_pawn_class','hud_class','start_players_as_spectators')}
 r['actors']=[]
 for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
  if a.get_actor_label().startswith('PC_City_') or isinstance(a,unreal.NavMeshBoundsVolume):
   p=actor_state(a);p['name']=a.get_name()
   if isinstance(a,unreal.Character):
    p['ai_controller_class']=str(a.get_editor_property('ai_controller_class'))
    p['auto_possess_player']=str(a.get_editor_property('auto_possess_player'))
   r['actors'].append(p)
 r['status']='pass_read_only_inspection'
except Exception:r['errors'].append(traceback.format_exc());r['status']='failed_inspection'
r['guards_after']=guards_match(rows)
(out/'result.json').write_text(json.dumps(r,indent=2)+'\n')
unreal.SystemLibrary.quit_editor()
