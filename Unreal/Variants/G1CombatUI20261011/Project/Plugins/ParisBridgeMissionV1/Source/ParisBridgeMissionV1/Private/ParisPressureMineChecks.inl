// Explicit diagnostic modes only; ordinary input and movement are unaffected.
bool MineViewpoint(UWorld* W,FTrap& T,FVector& Feet,double Distance){
    for(const FVector Offset:{FVector(0,-1,0),FVector(0,1,0),FVector(-1,0,0),FVector(1,0,0)})
        if(Site(W,T.Position+Offset*Distance,Feet)&&ClearRay(W,Feet+FVector(0,0,160),T.Position+FVector(0,0,6)))return true;
    return false;
}
void PressureMineCheck(UWorld* W,AParisBridgeMission* M,FEquipmentSession& S,AParisBridgePlayerController* PC,ACharacter* P,float DT){
    auto& T=S.Traps[1];
    if(CheckStep==0){
        if(M->Phase!=TEXT("Ready")||!S.Initialized)return;
        auto* D=Display(W,P);if(!D||!Flag(D,TEXT("Initialized")))return;
        if(CheckMode==TEXT("mine_spent_restore")){Tap(PC,EKeys::F9);CheckStep=188;CheckClock=0;return;}
        M->StartMission();HoldBrains(W);CheckClock=0;
        if(CheckMode==TEXT("mine_visual")||CheckMode==TEXT("mine_range")){
            FVector Feet;if(!Expect(W,MineViewpoint(W,T,Feet,CheckMode==TEXT("mine_range")?205:220),TEXT("mine_actual_viewpoint_floor_capsule_path_and_ray")))return;
            FixtureFeet(W,P,Feet);CheckStep=150;return;
        }
        if(CheckMode==TEXT("mine_contact")){
            FVector Feet;if(!Expect(W,MineViewpoint(W,T,Feet,100),TEXT("mine_noncontact_adjacent_floor")))return;
            FixtureFeet(W,P,Feet);CheckStep=170;return;
        }
        if(CheckMode==TEXT("mine_ally")||CheckMode==TEXT("mine_german")){
            TestAlly=Tagged(W,CheckMode==TEXT("mine_ally")?TEXT("G1_Ally1"):TEXT("G1_German1"));
            if(!Expect(W,TestAlly.IsValid(),TEXT("existing_roster_contact_actor")))return;
            FixtureFeet(W,TestAlly.Get(),T.Position);CheckStep=180;return;
        }
        if(CheckMode==TEXT("mine_post_clear")||CheckMode==TEXT("mine_post_clear_frag")||CheckMode==TEXT("mine_spent_save")){
            if(CheckMode==TEXT("mine_spent_save")){TestAlly=Tagged(W,TEXT("G1_Ally1"));FixtureFeet(W,TestAlly.Get(),T.Position);CheckStep=185;return;}
            for(auto* C:Combatants(W))if(Num(C,TEXT("TeamId"))==1)Invoke(C,TEXT("PC_ApplyDamage"),1000,TEXT("Amount"));
            FixtureFeet(W,P,M->BridgeheadFeet);CheckStep=190;return;
        }
        FinishCheck(W,false,TEXT("unknown_mine_mode"));return;
    }
    if(CheckMode==TEXT("mine_visual")){
        if(CheckStep==150&&CheckClock>1){AimPoint(PC,T.Position+FVector(0,0,6));CheckStep=151;CheckClock=0;return;}
        if(CheckStep==151&&CheckClock>1){
            if(!Expect(W,PressureMineMeshCache.IsValid()&&PressureMineMaterialCache.IsValid()&&PressureMineTextures.Num()==3&&T.Discovered&&MineHints(W).Num()>0,TEXT("actual_PBR_mesh_and_visible_world_hint")))return;
            auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("scope"),TEXT("Actual new runtime mine; admitted fixture camera; normal FOV then detail FOV; held NPCs; no debug marker"));
            O->SetStringField(TEXT("position_cm"),T.Position.ToString());O->SetNumberField(TEXT("triangles"),10809);O->SetNumberField(TEXT("normal_fov"),PC->PlayerCameraManager->GetFOVAngle());
            O->SetStringField(TEXT("material"),PressureMineMaterialCache->GetPathName());TArray<TSharedPtr<FJsonValue>> Textures;for(const auto& Texture:PressureMineTextures){auto R=MakeShared<FJsonObject>();R->SetStringField(TEXT("name"),Texture->GetName());R->SetBoolField(TEXT("sRGB"),Texture->SRGB);R->SetNumberField(TEXT("width"),Texture->GetSizeX());Textures.Add(MakeShared<FJsonValueObject>(R));}O->SetArrayField(TEXT("textures"),Textures);
            FFileHelper::SaveStringToFile(JsonText(O),*(CheckOut/TEXT("MINE_RENDER.json")));Picture(TEXT("01_mine_normal.png"));CheckStep=152;CheckClock=0;return;
        }
        if(CheckStep==152&&CheckClock>.5){PC->PlayerCameraManager->SetFOV(40);CheckStep=153;CheckClock=0;return;}
        if(CheckStep==153&&CheckClock>1){Picture(TEXT("02_mine_detail.png"));CheckStep=154;CheckClock=0;return;}
        if(CheckStep==154&&CheckClock>.5){FinishCheck(W,T.State==TEXT("Armed")&&!Dead(P),TEXT("Runtime finished mine/PBR/hint pictures; no native asset writes"));return;}
    }
    if(CheckMode==TEXT("mine_range")){
        if(CheckStep==150&&CheckClock>.5){AimPoint(PC,T.Position+FVector(0,0,6));CheckStep=151;CheckClock=0;return;}
        if(CheckStep==151&&CheckClock>.5){if(!Expect(W,T.Discovered&&Target(W,S)!=T.Id,TEXT("205cm_outside_disarm_range")))return;FVector Feet;if(!Expect(W,MineViewpoint(W,T,Feet,195),TEXT("195cm_admitted_floor")))return;FixtureFeet(W,P,Feet);CheckStep=152;CheckClock=0;return;}
        if(CheckStep==152&&CheckClock>.3){AimPoint(PC,T.Position+FVector(0,0,6));CheckStep=153;CheckClock=0;return;}
        if(CheckStep==153&&CheckClock>.3){if(!Expect(W,Target(W,S)==T.Id,TEXT("195cm_inside_disarm_range")))return;
            TestShield=W->SpawnActor<AActor>();auto* C=NewObject<UStaticMeshComponent>(TestShield.Get());TestShield->AddInstanceComponent(C);TestShield->SetRootComponent(C);C->SetStaticMesh(Shape(TEXT("Cube")));C->SetCollisionProfileName(TEXT("BlockAll"));C->SetCanEverAffectNavigation(false);C->SetRelativeScale3D(FVector(.1,2,3));C->RegisterComponent();TestShield->SetActorLocation((P->GetActorLocation()+T.Position)*.5+FVector(0,0,40));TestShield->SetActorRotation((T.Position-P->GetActorLocation()).Rotation());CheckStep=154;CheckClock=0;return;}
        if(CheckStep==154&&CheckClock>.2){if(!Expect(W,Target(W,S)!=T.Id&&MineHints(W).IsEmpty(),TEXT("cover_blocks_disarm_and_hint")))return;TestShield->Destroy();CheckStep=155;CheckClock=0;return;}
        if(CheckStep==155&&CheckClock>.2){if(!Expect(W,Target(W,S)==T.Id,TEXT("target_returns_after_cover_removed")))return;PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::E,IE_Pressed,1));CheckStep=156;CheckClock=0;return;}
        if(CheckStep==156&&CheckClock>.5){PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::E,IE_Released,0));if(!Expect(W,T.State==TEXT("Armed")&&!S.EHeld,TEXT("release_cancels_without_disarming")))return;PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::E,IE_Pressed,1));CheckStep=157;CheckClock=0;return;}
        if(CheckStep==157&&CheckClock>2.3){PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::E,IE_Released,0));if(!Expect(W,T.State==TEXT("Disarmed")&&MineHints(W).IsEmpty()&&S.Frag==2&&S.Smoke==2&&S.Grant==0,TEXT("held_E_disarms_removes_hint_no_resource_changes")))return;Picture(TEXT("mine_disarmed.png"));FinishCheck(W,true,TEXT("2m boundary, actual cover/LoS, release cancel, hold2s and hint removal"));return;}
    }
    if(CheckMode==TEXT("mine_contact")){
        if(CheckStep==170&&CheckClock>.4){if(!Expect(W,T.State==TEXT("Armed")&&!FootTouchesMine(P,T),TEXT("standing_100cm_away_does_not_trigger")))return;FixtureFeet(W,P,T.Position+FVector(0,0,90));P->GetCharacterMovement()->SetMovementMode(MOVE_Falling);CheckStep=171;CheckClock=0;return;}
        if(CheckStep==171&&CheckClock>.15){if(!Expect(W,T.State==TEXT("Armed")&&!FootTouchesMine(P,T),TEXT("airborne_above_mine_does_not_trigger")))return;FixtureFeet(W,P,T.Position);P->GetCharacterMovement()->SetMovementMode(MOVE_Walking);CheckStep=172;CheckClock=0;return;}
        if(CheckStep==172&&CheckClock>.4){if(!Expect(W,T.State==TEXT("Spent")&&Num(P,TEXT("Health"))<100,TEXT("grounded_footprint_triggers_original_damage")))return;const double H=Num(P,TEXT("Health"));TrapTick(W,S,.1);if(!Expect(W,Num(P,TEXT("Health"))==H,TEXT("spent_mine_cannot_repeat_damage")))return;FinishCheck(W,true,TEXT("Adjacent safe, airborne safe, actual grounded contact and single original damage"));return;}
    }
    if(CheckStep==180&&CheckClock>.6){if(!Expect(W,T.State==TEXT("Spent")&&Num(TestAlly.Get(),TEXT("Health"))<100,TEXT("both_factions_contact_trigger_and_damage")))return;if(!Expect(W,CheckMode==TEXT("mine_ally")?M->LivingDefenders==3:M->LivingDefenders==2,TEXT("actual_roster_casualty_bookkeeping")))return;FinishCheck(W,true,TEXT("Existing roster actor real mine contact; no faction immunity; original casualty endpoint"));return;}
    if(CheckMode==TEXT("mine_spent_save")){
        if(CheckStep==185&&CheckClock>.6){if(!Expect(W,T.State==TEXT("Spent")&&Dead(TestAlly.Get()),TEXT("actual_mine_spent_and_ally_casualty")))return;for(auto* C:Combatants(W))if(Num(C,TEXT("TeamId"))==1)Invoke(C,TEXT("PC_ApplyDamage"),1000,TEXT("Amount"));FixtureFeet(W,P,M->BridgeheadFeet);CheckStep=186;CheckClock=0;return;}
        if(CheckStep==186&&CheckClock>.3){if(!Expect(W,M->Phase==TEXT("Won")&&M->LivingAllies==1&&M->CheckpointUnlocked(),TEXT("enemy_clear_saves_with_actual_ally_casualty")))return;Tap(PC,EKeys::E);CheckStep=187;CheckClock=0;return;}
        if(CheckStep==187&&M->CheckpointDialogState()==TEXT("Succeeded")){auto J=ReadJson(M->InspectCheckpointJournal());if(!Expect(W,J&&J->GetBoolField(TEXT("valid")),TEXT("spent_mine_real_journal_write_readback")))return;FFileHelper::SaveStringToFile(JsonText(J->GetObjectField(TEXT("snapshot"))),*(CheckOut/TEXT("SAVED_PAYLOAD.json")));FinishCheck(W,true,TEXT("Actual ally-triggered spent mine and casualty saved in original verified journal"));return;}
    }
    if(CheckMode==TEXT("mine_spent_restore")){
        if(CheckStep==0&&M->Phase==TEXT("Ready")){Tap(PC,EKeys::F9);CheckStep=188;CheckClock=0;return;}
        if(CheckStep==188&&M->Phase==TEXT("Won")&&S.Restored){TestAlly=Tagged(W,TEXT("G1_Ally1"));if(!Expect(W,T.State==TEXT("Spent")&&Dead(TestAlly.Get())&&!Dead(P)&&M->LivingAllies==1&&S.Traps[0].State==TEXT("Armed"),TEXT("fresh_process_spent_state_and_original_casualty_restore")))return;CheckStep=189;CheckClock=0;return;}
        if(CheckStep==189&&CheckClock>3.6){auto* I=TestAlly->GetMesh()->GetSingleNodeInstance();if(!Expect(W,I&&!I->IsPlaying()&&T.State==TEXT("Spent"),TEXT("restored_ally_terminal_pose_and_no_mine_retrigger")))return;FinishCheck(W,true,TEXT("Fresh-process original loader, spent mine remains spent, ally terminal death stays stopped"));return;}
    }
    if(CheckMode==TEXT("mine_post_clear")||CheckMode==TEXT("mine_post_clear_frag")){
        if(CheckStep==190&&CheckClock>.3){if(!Expect(W,M->Phase==TEXT("Won")&&M->CheckpointUnlocked()&&T.State==TEXT("Armed"),TEXT("enemy_clear_unlocks_while_mine_armed")))return;Tap(PC,EKeys::E);CheckStep=191;CheckClock=0;return;}
        if(CheckStep==191&&M->CheckpointDialogState()==TEXT("Succeeded")){auto J=ReadJson(M->InspectCheckpointJournal());if(!Expect(W,J&&J->GetBoolField(TEXT("valid"))&&M->SaveSerial==1,TEXT("original_durable_journal_before_hazard")))return;Invoke(P,TEXT("PC_ApplyDamage"),95,TEXT("Amount"));if(CheckMode==TEXT("mine_post_clear_frag")){Tap(PC,EKeys::E);PC->SetControlRotation(FRotator(-75,0,0));Tap(PC,EKeys::G);}else FixtureFeet(W,P,T.Position);CheckStep=192;CheckClock=0;return;}
        if(CheckStep==192&&CheckClock>(CheckMode==TEXT("mine_post_clear_frag")?6:.5)){if(!Expect(W,(CheckMode==TEXT("mine_post_clear_frag")?S.FragThrown==1:T.State==TEXT("Spent"))&&Dead(P)&&M->Phase==TEXT("Lost")&&!M->CheckpointDialogVisible(),TEXT("post_clear_hazard_death_Lost_and_dialog_closed")))return;Picture(TEXT("mine_post_clear_lost.png"));Tap(PC,EKeys::F9);CheckStep=193;CheckClock=0;return;}
        if(CheckStep==193&&M->Phase==TEXT("Won")&&S.Restored){if(!Expect(W,!Dead(P)&&Num(P,TEXT("Health"))==100&&S.Traps[1].State==TEXT("Armed")&&S.Frag==2&&S.Smoke==2&&M->SaveSerial==1,TEXT("F9_restores_alive_and_saved_armed_mine")))return;Tap(PC,EKeys::F6);CheckStep=194;CheckClock=0;return;}
        if(CheckStep==194&&M->Phase==TEXT("Ready")){if(!Expect(W,!Dead(P)&&M->LivingDefenders==3&&S.Frag==2&&S.Smoke==2&&S.Grant==0&&S.Traps[1].State==TEXT("Armed"),TEXT("F6_fresh_restart_original_roster_resources")))return;FinishCheck(W,true,TEXT("Clear/save with armed mine; real hazard death Lost; actual F9 and F6 new-world lifecycle"));return;}
    }
    if(CheckClock>20)FinishCheck(W,false,TEXT("mine_check_timeout"));
}
