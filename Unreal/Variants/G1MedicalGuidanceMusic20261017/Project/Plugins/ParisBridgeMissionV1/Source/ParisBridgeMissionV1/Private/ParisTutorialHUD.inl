// Read-only tutorial presentation. KeyHint shares HudInstruction; lesson acceptance stays unchanged.
FString HudStatus(const AParisBridgeMission* M){
    const auto& S=State(M);auto* P=Pawn(M->GetWorld(),TEXT("Player"));
    if(!P)return FString();
    if(S.Stage==Walk)return FString::Printf(TEXT("MARKER  %.1f m"),FVector::Dist2D(P->GetNavAgentLocation(),WalkFeet)/100);
    if(S.Stage==Run)return FString::Printf(TEXT("RUN  %.1f / 12 m  |  MARKER  %.1f m"),FMath::Min(12.,S.RunDistance/100),FVector::Dist2D(P->GetNavAgentLocation(),RunFeet)/100);
    if(S.Stage==Crawl&&S.CrawlArmed)return FString::Printf(TEXT("W[%s] S[%s] A[%s] D[%s]  |  %.1f / 2.5 m"),S.CrawlAxisTravel[0]>=15?TEXT("OK"):TEXT("--"),S.CrawlAxisTravel[1]>=15?TEXT("OK"):TEXT("--"),S.CrawlAxisTravel[2]>=15?TEXT("OK"):TEXT("--"),S.CrawlAxisTravel[3]>=15?TEXT("OK"):TEXT("--"),FMath::Min(2.5,S.CrawlDistance/100));
    if(S.Stage==Fire)return FString::Printf(TEXT("SHOTS  %d / 2"),int(FMath::Clamp(Num(P,TEXT("ShotSequence"))-S.ShotStart,0.,2.)));
    if(S.Stage==Recruit)return FString::Printf(TEXT("RECRUITED  %d / 2"),int(S.History[0])+int(S.History[1]));
    if(S.Stage==Combat)return FString::Printf(TEXT("%d / 3 GUARDS ELIMINATED"),3-M->LivingDefenders);
    return FString();
}
FString HudInstruction(const AParisBridgeMission* M){
    const auto& S=State(M);const auto& E=ParisTacticalEquipment::Session(M->GetWorld());
    auto* P=Pawn(M->GetWorld(),TEXT("Player"));
    if(S.Stage==Fire||S.Stage==Reload){
        if(E.SelectedSlot!=0)return TEXT("WHEEL: SELECT RIFLE");
        if(P&&Name(P,TEXT("ActionState"))==TEXT("Reloading"))return TEXT("WAIT FOR THE RELOAD TO FINISH");
        if(S.Stage==Reload&&P&&Num(P,TEXT("LoadedAmmo"))+Num(P,TEXT("ReserveAmmo"))<8)return TEXT("AMMO BELOW 8  |  F6: RESTART TRAINING");
        if(S.Stage==Fire&&P&&Num(P,TEXT("LoadedAmmo"))==0)return Num(P,TEXT("ReserveAmmo"))>0?TEXT("R: RELOAD, THEN CONTINUE FIRING"):TEXT("AMMO EMPTY  |  F6: RESTART TRAINING");
    }
    if(S.Stage==Frag||S.Stage==Smoke){
        const bool FragLesson=S.Stage==Frag;
        const bool Thrown=FragLesson?E.FragThrown>S.FragStart:E.SmokeThrown>S.SmokeStart;
        if(Thrown)return FragLesson?TEXT("THROWN  |  WAIT FOR EXPLOSION AND ACTION TO FINISH"):TEXT("THROWN  |  WAIT FOR SMOKE AND ACTION TO FINISH");
        if(E.ReleaseQueued||E.ThrowStage==TEXT("Release"))return TEXT("THROWING  |  WAIT FOR THE ACTION TO FINISH");
        if(!E.ThrowKind.IsEmpty()&&(E.ThrowStage==TEXT("Start")||E.ThrowStage==TEXT("Hold"))){
            if(E.ThrowKind!=(FragLesson?TEXT("Frag"):TEXT("Smoke")))return FragLesson?TEXT("WRONG GRENADE  |  ESC: CANCEL, THEN WHEEL TO FRAG"):TEXT("WRONG GRENADE  |  ESC: CANCEL, THEN WHEEL TO SMOKE");
            return TEXT("RELEASE LEFT MOUSE TO THROW  |  ESC CANCEL");
        }
        if((FragLesson?E.Frag:E.Smoke)==0&&E.ThrowKind.IsEmpty()&&E.Balls.IsEmpty())return TEXT("STOCK EMPTY  |  E AT TEACHING BOX  /  F6 RESTART");
        return FragLesson?TEXT("WHEEL: FRAG  |  HOLD / RELEASE LEFT MOUSE INTO OPEN SPACE"):TEXT("WHEEL: SMOKE  |  HOLD / RELEASE LEFT MOUSE INTO OPEN SPACE");
    }
    if(S.Stage==Crawl)return S.CrawlArmed?TEXT("WASD: EACH DIRECTION + 2.5 m TOTAL  |  MOUSE: LOOK"):TEXT("Z: GO PRONE ON CLEAR, LEVEL GROUND");
    if(S.Stage==Disarm&&E.Traps.Num()==3&&E.Traps[2].State==TEXT("Spent"))return TEXT("TRAINING MINE DESTROYED  |  F6: RESTART");
    if(S.Stage==Recruit&&(!S.History[0]&&Dead(Pawn(M->GetWorld(),TEXT("Ally1")))||!S.History[1]&&Dead(Pawn(M->GetWorld(),TEXT("Ally2")))))return TEXT("ALLY UNAVAILABLE  |  LOOK AWAY + E: REVIEW OPTIONS");
    if(TrainingCheckpoint(M)){
        if(S.CP0Saved)return M->InsideCheckpoint()?TEXT("WALK TOWARDS BRIDGE C TO CONTINUE   |   ENTER  CONTINUE NOW"):TEXT("WALK TOWARDS BRIDGE C TO CONTINUE");
        return M->InsideCheckpoint()?TEXT("E  SAVE IN CIRCLE   |   ENTER  CONTINUE WITHOUT SAVING"):TEXT("ENTER GOLD CIRCLE TO SAVE OR CONTINUE");
    }
    const TCHAR* Hints[]={
        TEXT("ENTER  BEGIN TRAINING"),TEXT("MOUSE: TURN LEFT OR RIGHT  |  ESC: PAUSE / CURSOR"),
        TEXT("WASD: WALK TO THE MARKER"),TEXT("SHIFT + WASD: RUN 12 m AND REACH THE MARKER"),
        TEXT("SPACE: JUMP, THEN LAND"),TEXT("CTRL: CROUCH AND WAIT BRIEFLY"),TEXT(""),TEXT("Z: STAND UP"),
        TEXT("LEFT MOUSE: FIRE TWO SHOTS"),TEXT("R: RELOAD TO 8 ROUNDS AND WAIT"),TEXT(""),TEXT(""),
        TEXT("AIM AT BOX + E: TAKE AVAILABLE STOCK"),TEXT("STAND STILL + AIM AT MINE + HOLD E 2s"),
        TEXT("AIM AT ALLY + E: TALK, THEN CONFIRM JOIN"),TEXT(""),
        TEXT("ELIMINATE ALL THREE GUARDS  |  USE COVER AND YOUR SQUAD"),TEXT("ENTER GOLD CIRCLE + E: SAVE"),
        TEXT("ESC  MENU   |   F9  LOAD CHECKPOINT")};
    return Hints[FMath::Clamp(S.Stage,0,int(Complete))];

}
