# MI019 — Menu/checkpoint compile and cooked-schema failures

10 October2026. The first isolated child compiles its production mission/controller
interaction changes, but its diagnostic-only readonly-slot negative fails C2039:
UE5.8's IFileManager has no SetReadOnly member. Runtime checks did not start.
Installed GenericPlatformFile.h exposes this operation through IPlatformFile.
Retain candidate_v1/Project, failed_source_snapshot, prepare/build JSON and build.log
under tmp/g1-team-feedback-20261010; do not relabel this source as tested or rebuild
that failed identity. candidate_v2 changes only the probe to
FPlatformFileManager::Get().GetPlatformFile().SetReadOnly; safety/resource/journal
and production interaction behavior are unchanged. All original assets and user
saves stay protected. This is a compile correction, not evidence for Jingdi's E
failure. Before the build, Windows PowerShell5 script policy blocked shell entry;
the existing bundled PowerShell7 ran the generated script without any policy change.
See the bounded team-feedback implementation plan; later native test results must
record exact candidate/run identities and distinguish test fixtures from manual play.

candidate_v2 compiles/links successfully (Gamed31e712d), but is not run: before
testing, its readonly negative is narrowed to copy the existing valid journal
into the next test slot, rather than writing arbitrary text and unnecessarily
testing save-file deserialization. candidate_v3 changes only that diagnostic
setup. v2's compiled_source_snapshot/build/log/Game remain. Production menu and
save/safety code are exact between v2 and v3; no failure of the game journal is
claimed from this unexecuted fixture review.

candidate_v3 builds successfully (Game a2cba18c) but menu_v1 exits 3 before
BeginPlay: AsyncLoading2 reports Bad export index in ParisBridgeMission_0,
SerializeUnversionedProperties. The added reflected InteractionRevision shifted
the native property layout relative to the existing cooked map. This is a failed
candidate, not a corrupt original map. Its Game/runtime, 45-file source snapshot,
build and menu_v1 crash receipts remain private. candidate_v4 removes only that
UPROPERTY annotation; the counter is an ordinary runtime C++ field. Parent
reflection declarations must match exactly before reusing cooked assets. No
recook, asset replacement or save-schema change is authorized by this repair.
