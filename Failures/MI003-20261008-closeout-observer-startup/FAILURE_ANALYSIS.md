# MI003 - Compiled observer was not loaded

8 October 2026. English original; [Chinese review](FAILURE_ANALYSIS_ZH.md).

instrument_v1 compiled successfully. integrated_v1 reached the ordinary native
G1 Ready state but produced no observer marker/samples and never called Start.
Stop receipt records zero scripted mission attempts. Only its exact owned PID
11232 was stopped; exit -1 records that stop, not a G1 asset crash. No whole-loop,
FPS or save result is claimed. Preserve all source/receipts/log/cooked bytes in
the private MVPCloseoutV1 failure archive.

Diagnosis: replacing the monolithic Game binary does not replace the cooked
content-only project descriptor. The compiled primary Game module is not listed
there and its StartupModule is not invoked by project module loading. Installed
LaunchEngineLoop.cpp LoadStartupModules uses the project and enabled plugin
descriptors; ModuleManager.cpp disables the Module Load console command for
monolithic builds. Do not retry that command or the stopped whole test.

Different bounded mechanism: instrument_v2 adds the opt-in observer at the
already-enabled ParisBridgeMissionV1 module startup, in the isolated wrapper
only. Two wiring files differ (module implementation and Build.cs dependencies).
ParisBridgeMission.cpp/header and all original gameplay, weapon, AI, model/pose
sources stay exact. Cooked content is copied exactly from package_v2. Baseline
project/plugin/native files remain untouched. Early gate requires explicit
CLOSEOUT_MODULE_ACTIVATED and actual world samples before60s; otherwise stop the
exact owned game. Existing path/resource/no-teleport/180s/three-run acceptance is
unchanged. No module source or map adoption/publication follows from a test.
