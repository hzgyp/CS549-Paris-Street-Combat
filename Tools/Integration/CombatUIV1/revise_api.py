"""Finite template repair for MI032; leave failed candidate_ui_v1 exact."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
def change(p,old,new,count=1):
    data=p.read_text('utf-8');assert data.count(old)==count,(p.name,old)
    p.write_bytes(data.replace(old,new).encode('utf-8'))
cpp=HERE/'ParisCombatUI.cpp'
change(cpp,'PC->bShouldPerformFullTickWhenPaused=U.OldFullTick','PC->SetCombatUIFullTick(U.OldFullTick)',2)
change(cpp,'U.OldFullTick=PC->bShouldPerformFullTickWhenPaused;PC->bShouldPerformFullTickWhenPaused=true','U.OldFullTick=PC->SetCombatUIFullTick(true)')
change(cpp,'auto* Player=PC->GetPawn();','APawn* Player=PC->GetPawn().Get();',2)
author=HERE/'author.py'
change(author,"interaction=private/'ParisMissionInteraction.cpp'","public=private.parent/'Public/ParisBridgeMission.h'\nedit(public,'    bool InteractionMenuVisible() const;', '    bool SetCombatUIFullTick(bool Value){const bool Prior=bShouldPerformFullTickWhenPaused;bShouldPerformFullTickWhenPaused=Value;return Prior;}\\n    bool InteractionMenuVisible() const;')\ninteraction=private/'ParisMissionInteraction.cpp'")
change(author,"edit(mission,'    if(M->CheckpointPromptVisible)\\n    {\\n        Halo(960,822'", "edit(mission,'const double MX=Screen.X/(Canvas->SizeX/1920.0),MY=Screen.Y/(Canvas->SizeY/1080.0);','const double MX=(Screen.X-OX)/S,MY=(Screen.Y-OY)/S;')\nedit(mission,'    if(M->CheckpointPromptVisible)\\n    {\\n        Halo(960,822'")
verify=HERE/'verify.py'
change(verify,'assert set(changed)==allowed,changed',"allowed.add(base.replace('Private/','Public/')+'ParisBridgeMission.h')\nassert set(changed)==allowed,changed")
print('MI032 template repair applied; no failed source changed.')
