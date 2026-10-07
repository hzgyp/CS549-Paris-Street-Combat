# Reload with rifle: preview-only review

4 October 2026. Owner: yg745. Scope: user-requested native animation-editor
preview with the existing M1 appearance; no repair, retarget, native save,
formal-map selection, publication or Git commit/push.

Reviewed: Failures/README.md, AN001 and FP001 failure analyses, and
WEAPON_ANIMATION_REUSE_RESULT_20261004_ZH.md. This review separates the original
full-body source action, existing Allied retarget, and previous first-person
integration evidence. It does not retry the stopped AN001 authoring mechanism.

Use the current user-owned editor PID44632, not a second writer. Inspect the
existing hand/weapon socket and add the existing M1 as an in-memory preview
attachment. No socket/bone/finger/mesh/clip changes or offset search. Preview
attachment metadata may be dirty in memory: do not save it or claim enforced
read-only mode. Review complete motion with play/pause/scrub, then leave it for
human inspection. If a compatible attachment cannot be shown without source
changes, stop that route and report the actual limitation.

Early check: correct existing asset and socket, rifle visibly follows the hand,
no persistent modification. Do not judge action quality from an unaligned gun.
Acceptance evidence: actual observed preview, clearly distinguish source from
target and third-person from first-person. Previous frozen first-person images
support sleeve/obstruction concerns but do not establish a new continuous pass.
Verify protected507 files and5 retained failed drafts after setup. Stop after
review setup; do not tune the rig/camera or implement another repair. Rollback is
discarding in-memory preview metadata, never restoring old bytes over work.

UI recovery: the Add Preview Asset submenu and direct browser drop did not
produce an attachment. A read-only Python probe in this same editor may inspect
native preview metadata and preview-component handles. If a supported in-memory
attachment is available, use it without save; do not add/rebuild a C++ bridge or
launch another writer. This does not authorize changing source sockets or poses.

If native preview-attachment metadata is not exposed, the supported transient
actor API may create one StaticMeshActor only in the existing source animation
preview world and attach it to the unmodified existing hand_rSocket_Aim. This is
not an editor-level actor or native asset. Retain its Python handle for removal;
no per-frame Python updates. Stop if this world/parent is ambiguous or native
attachment is unavailable. An unaligned existing socket is a preview mounting
limitation, not proof of a defective source action.

Read-only API discovery confirms preview metadata and deferred actor spawn are
not Python-exposed. Use the documented SubobjectDataSubsystem instance API
instead: add exactly one transient StaticMeshComponent to the existing native
AnimationEditorPreviewActor (not a Blueprint/class), then native socket attach.
The component must remain under /Engine/Transient, with no Blueprint context,
no collision and no writer/updater. Retain its handle in builtins for cleanup.

## Actual result, 4 October, 16:33 local

Existing M1 is visibly attached in the original D059 mannequin Animation Editor
under /Engine/Transient.World_0 only, via one StaticMeshComponent on the native
AnimationEditorPreviewActor. Socket remains hand_rSocket_Aim with unchanged
source transform; gun relative transform is identity, scale1. Native attachment
moves it during animation; no Python per-frame callback. All Saved is displayed.
Source start0.00 and middle2.01s side views were inspected. Start points forward;
the apparent disappearance in the frontal view was barrel foreshortening, not
attachment loss. No pose or gun offset correction was needed/attempted. The
early frontal/middle crop is not full-weapon proof. This shows a usable source
candidate, not accepted target-soldier deformation, finger/contact, M1-specific
mechanics, first-person framing or gameplay. Keep the source; the stopped target
adaptation remains failed/unselected.

The old actual-city reload_operate.png was directly reinspected: a stretched
triangular sleeve occupies much of the center/right view. This is the concrete
reason the previous adaptation failed; it is not a rejection of the source
full-body motion. No new city test or continuous functional acceptance occurred.

Post-attachment512 size/SHA comparisons (507 protected +5 failed drafts) have
zero differences. No native save/map selection/Catalog/release/commit/push.
Retain the current user-owned editor. Temporary preview vanishes with this
preview world. For explicit later cleanup, the retained builtins tuple contains
component/handle/context; use SubobjectDataSubsystem.k2_delete_subobjects_from_instance
on that context/handle only, then remove the tuple. Do not close the editor or
delete any native asset as cleanup. UI menu/drop failures, missing container
property and unavailable deferred-actor API are preserved in the existing log;
successful component API carries only deprecated-get_object warnings.

Handoff display: source tab, side-on native Front orthographic viewport,
zoomed out after the cropped2.01s observation, looping resumed with the existing
M1. This changes the inspection viewport only, not the gameplay camera.

中文结论：M1已加到原始D059白模的独立预览，随现有右手挂点运动，
未改骨架、手指、动作、枪模或正式地图，也没有保存资产。源动作仍值得
保留；上轮失败的是套到当前士兵第一人称后的效果：袖口拉成三角片并
遮挡画面中心。新预览不代表这些适配问题已解决，也不代表手枪接触或
M1专用换弹验收通过。512个文件大小/哈希复核完全一致。当前留侧面
循环播放供人工查看，不继续重定向/精修/选入游戏/发布或提交。
