# Native first-person grip binding

5 October 2026: Yupu accepts the V20 first-person presentation and requests
formal adoption. `AParisFirstPersonApprovedActor` is the persistent selection
wrapper. It references a private DataAsset and existing mesh/gun/holding clip,
waits for the original native owner/Ready source, prepares once and binds once.
It hides the superseded visual only; original action/ammo/weapon ownership stays
unchanged. Existing V18/V19 grip/source/transition algorithms are not rewritten.
See `Docs/Development/FIRST_PERSON_FORMAL_V21_20261005.md` and its result for
actual selection/publication status. The older diagnostic descriptions below
describe prior checkpoints, not authority to re-run failed repairs.

Runtime C++ display adapter for the existing native soldier/action source.
Disabled by default at plugin level; the formal project explicitly enables it. See
`Docs/Development/UE_GRIP_BINDING_V18_20261005.md` for limits and evidence.

- Source animations are evaluated by the original UE skeletal component.
- The actor ticks after that component and copies bone transforms, not skinned
  vertices. The exact existing display mesh/materials are referenced, not copied.
- Private `UParisGripV18Config.BindingJson` supplies the accepted holding pose,
  hand-relative gun/support transforms and distal proportion. No commercial pose
  payload or source asset belongs in this plugin or Git.
- The engine solves the original-length left support chain without stretching.
  Right wrist/source arm are unchanged. The gun is an actual hand_r child.
- Holding overrides are inactive outside Ready. This does not replace or
  certify the existing reload/recoil animations.
- One initial camera-local assembly frame remains constant. No per-action reset,
  source camera edit, Python frame driver or weapon/ammunition transaction write.
- Original WeaponAppearance remains authoritative. The human-approved display
  is now selected by the formal wrapper; near-wall/action/lifecycle equivalence
  remains separate unfinished acceptance, not implied by that selection.

Rebuild host editor (UE5.8, installed C++ toolchain): RunUAT BuildPlugin with
`-NoTargetPlatforms -HostPlatforms=Win64` and a new disposable package directory.
Copy the resulting Binaries into this plugin; never check them into Git. The
approved ordinary project entry enables this plugin in the saved .uproject and
disables Python/ParisEditorBridge during play. The Win64 editor module is private
SFTP data; generic source stays in Git. Shipping/package builds remain separate
acceptance gates and require an appropriate target build.

The ordinary AnimBP graph author attempt stopped after two capability failures;
do not rerun its author/owner scripts to create missing assets.

V19 adds a separate `AParisFPUpperBodyV19Actor` existing-motion source adapter.
The V18 base source hook remains no-op; its stopped full-body proof is not
reopened. A hidden native skeletal component evaluates a measured mature hold
clip for the FP display while original full-body locomotion continues. Source
actions and holding grip/IK fade in parent-local space from the previous display
source pose; assembly frame stays cached once. No new motion or camera/skin edit.
Private source selection/evidence: FPUpperBodyV19. See its bounded implementation
document for gates; the formal wrapper selects these mechanisms through saved
references, not merely by creating source code. Sleeves and AN007 full-return
limitations remain explicitly deferred/unpassed; no new motion is created.
