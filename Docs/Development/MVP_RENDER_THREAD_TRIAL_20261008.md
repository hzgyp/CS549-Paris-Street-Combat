# Bounded render-thread performance trial

8 October 2026. [Chinese review](MVP_RENDER_THREAD_TRIAL_20261008_ZH.md).
Cases read: Failures/README, MI004/MI005 and the current closeout/fixture plans.
Native assets, original source758, selected359 and current703 stay protected.

The three complete navrepair_v1 player-route CSVs measure36.84/36.05/36.08FPS,
not the60FPS goal. Render thread is about26ms; GPU is about11ms and hardware
ray-tracing scene gathering is present. This suggests CPU/render-scene work,
not proof that disabling hardware ray tracing will meet the target. Incomplete
cohort CSV prefixes are excluded. Installed UE5.8 D3D12Adapter.cpp explicitly
supports the startup -noraytracing parameter; DefaultEngine.ini enables ray tracing.

After the current squad fixture completes, try ONE separately named private entry
with -noraytracing. Keep actual1920x1080, High/all ten sg2,100% screen percentage,
1536MiB texture pool,VSync0/no cap, original city/models/materials/actions/AI,
exact goals and original gates. Use the same new observer build and native-finish
fixture for the three captures; compare with the same build's RT-on captures
only if their native CSV trailers and complete squad loops are valid. Keep the
earlier player-only capture as context, not a matched performance comparison.
No viewport recording, background hash/cook job or arbitrary hitch trimming.

Early acceptance: no occupied native writer; exact input/binary hashes; activation,
nativeReady, actual resolution/quality/pool and hardware RT disabled confirmed.
Retain a rendered Ready image for visual inspection. An argument alone does not
establish the applied setting. Three bounded complete captures report frames,
span,mean/median/p95/max,CPU/GPU/memory and actual60FPS result, including a miss.
Software rendering-path visual differences remain a declared profile change,
not automatic final visual adoption or asset alteration.

Stop on first functional/path/squad/error/hash failure, overflow, invalid capture
or existing bounds. Do not sweep more console settings/resolutions/pool sizes,
reduce textures/quality silently, or claim a final performance pass from a short
diagnostic. If the current squad fixture fails, retain its cause and prioritize
that functional correction before this performance trial.
