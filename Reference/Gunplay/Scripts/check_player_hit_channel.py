from pathlib import Path
import json,unreal
w=unreal.EditorLevelLibrary.get_game_world();p=unreal.GameplayStatics.get_player_character(w,0)
r={'visibility':str(p.capsule_component.get_collision_response_to_channel(unreal.CollisionChannel.ECC_VISIBILITY)),'weapon':str(p.capsule_component.get_collision_response_to_channel(unreal.CollisionChannel.cast(15)))}
(Path(__file__).resolve().parents[2]/'Development/Evidence/G1/2026-09-21_battlefield/player-hit-channel.json').write_text(json.dumps(r,indent=2));unreal.log(str(r))
