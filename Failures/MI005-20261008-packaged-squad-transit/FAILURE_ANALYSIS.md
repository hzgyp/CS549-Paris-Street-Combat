# MI005 - Player success does not establish squad transit

8 October 2026. [Chinese review](FAILURE_ANALYSIS_ZH.md).
cohort_v1/instrument_v6 uses the single witnessed polygon exclusion from MI004,
unchanged city/capsules/actions/AI, original player input and far-bank goal. It
waits at the far bank before G1, applying the original two-Allied55cm/25s gate.
It FAILS failed_original_cohort_25sec_bound,79.755s observer wall, normal exit0.

Final Player(5837.618,-20290.487,206.383), HP100,17shots/1+0 ammo. Both Allies
alive100HP/2+16 ammo/0shots; all Germans killed by actual player shots. Ally1
(5708.730,-20918.983,277.048), velocity0, HeldGoal error110.488cm. Ally2
(2105.849,-20810.376,212.582), velocity0, HeldGoal error3408.397cm. Both report
SquadFailed=false. That flag and a target/query are insufficient arrival proof.
The earlier navrepair_v1 three player-only wins/save/load/restarts remain valid
within that narrower scope, not squad, natural two-sided combat or whole MVP.

Stop the cohort proof and one-polygon repair route here. Do not add blacklisted
polygons, expand time/acceptance radius, adjust formation, capsule, speed, damage
or AI from guesses. Formal runtime/map/Catalog are unchanged. Cause of the NPC
stalls was not recorded by this version; it contains no NPC path status or
actual capsule impact information. Do not infer a geometry or AI defect yet.

Different cause-only squad_diagnose_v1/instrument_v7: same sealed map/input and
single existing trial exclusion, but records original NPC path state/targets,
request-finished results, actual capsule dimensions/step/nav properties and
forward60cm sweeps including hit normal/step eligibility/static mesh/nav collision
metadata. Stop on the first4s Ready stationary NPC whose held-goal error>100cm,
or existing180s/loss/error bound; no complete cohort proof, new exclusion or
gameplay change. Require actual observer activation and exact protected inputs.
Retain raw receipts/binary/source/CSV in private MVPCloseoutV1/failures/cohort_v1
and instrument_v6; archive after exact owned process closure. This is diagnosis,
not another attempt to pass the stopped gate unchanged.

CSV qualification: this failure exits directly after EndCapture. Its raw CSV
lacks the native final repeated-header/metadata trailer; retain it as an
incomplete prefix, NOT a valid full-span performance capture. The first summary
is retained; later csv_validation.json explicitly invalidates its FPS reading.
Future summary code checks that trailer. Native diagnose_v1 and all three
navrepair_v1 CSVs have the complete trailer; their narrower reported data stand.

Later squad_diagnose_v1/instrument_v7 normal exit0,183.009s: round0 passes
both Allies' original gate, then round1 fails25s. Ally1 held-goal error34.618cm;
Ally2 error3551.617cm, path Idle/Ready/SquadFailed=false. Its last request54
returns Aborted3/flags328. Installed UE AIController::StopMovement supplies
MovementStop|ForcedScript; path flags also include UserAbort. This is an explicit
script stop, NOT native Blocked. Which policy stopped it was not recorded.
The four-second detector only ran during playing; regroup reached25s instead.
Do not hide this observer coverage error or count round0 as repeatability.
Moving samples hit debris with a walkable normal while speed300cm/s; such a sweep
alone is not proof of an NPC physical obstruction. Actual physics and navigation
convex buffers both contain61vertices, not proof of equal full surfaces.

The successful earlier PIE fixture left player SimpleMove running inside55cm;
the failed packaged fixture cancelled it there. A distinct fixture correction
and read-only blackboard/request diagnostic is planned in
Docs/Development/MVP_G1_SQUAD_FIXTURE_DIAGNOSTIC_20261008.md. It preserves the
original arrival bounds and all gameplay, and does not assert that this input
discrepancy caused the NPC failure. Do not modify AI without recorded cause.
