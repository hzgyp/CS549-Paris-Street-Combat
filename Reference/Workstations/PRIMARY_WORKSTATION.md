# Primary Development Workstation

**Confirmed by Yupu Guo · Hardware inventory captured 17 September 2026 · Paris development plan synchronized 30 September 2026**

This Alienware Aurora R13 is the primary development desktop. Active project: `D:\0.Rutgers\CS549\Project-New`. Blueprints are the primary gameplay implementation approach; C++ requires a demonstrated need. The hardware table below preserves the dated inventory and is not a new scan.

| Component | Observed configuration |
|---|---|
| CPU | Intel Core i9-12900F; 16 cores, 24 logical processors |
| Memory | 32 GB installed, 2 × 16 GB; approximately 31.8 GiB visible to Windows; reported DDR5-4800 modules configured at 4400 MT/s |
| GPU | NVIDIA GeForce RTX 3080, 10,240 MiB VRAM (10 GiB); NVIDIA-reported driver 616.92 |
| OS | Windows 11 Pro Education, build 26200 |
| C: | Crucial CT4000P3SSD8 NVMe SSD; volume 3,722.9 GiB total, 1,769.6 GiB free |
| D: | Separate Crucial CT4000P3SSD8 NVMe SSD; volume 3,725.9 GiB total, 676.2 GiB free |
| Storage health | Windows reports both volumes/disks Healthy |
| Unreal detection on 17 September | No registered installation/project found in that check. Superseded for current planning by the active UE5.8 descriptor and recorded UE5.8.2 baseline; runtime compatibility remains unverified |

Capacity is shown in GiB, not decimal manufacturer GB/TB. This was a read-only inventory using Windows system/storage information and NVIDIA reporting. No synthetic benchmark, sustained thermal test, storage throughput test or Unreal performance capture was run. A Healthy flag is not a full hardware diagnostic. Serial numbers and machine/user identifiers are not included in the saved snapshot.

## Suitability assessment

The machine meets Epic's published recommended 32 GB system-memory and 8 GB-or-more graphics-memory levels. It is a reasonable primary machine for this compact Blueprint project. That is a planning assessment, not a promise of cinematic quality at 60 fps. [Epic hardware requirements](https://dev.epicgames.com/documentation/en-us/unreal-engine/hardware-and-software-specifications-for-unreal-engine)

Start packaged profiling at 1920×1080 with recorded quality settings. Treat 60 fps as a target and measure median/p95 frame time, CPU/GPU timings and memory use. Large textures, volumetric effects and high shadow/reflection settings can pressure 10 GiB VRAM. Change settings based on the graybox/asset lab, not GPU name alone. A memory upgrade is not presently required by this assessment.

## Storage and version plan

Keep source project files on D: as requested. C: currently has more free capacity and is a candidate for engine installation and disposable caches if an installation is needed; this document does not install, move or reconfigure anything. Reserve an initial 200–300 GiB project/asset allowance on D: as a planning budget, not a measured requirement. Track actual growth before downloading large asset packs.

Record an agreed engine **major.minor.patch**, project plugins and the working driver version after the first project opens and packages. Do not select an engine version solely because the documentation currently defaults to it. Store required `.uproject`, configuration and Unreal assets with an agreed binary-asset policy; generated caches and build artifacts should not become accidental source dependencies.

## First measurement gate

1. Validate the active Paris project, record the tested exact engine/plugin versions and establish a Windows package. The current association is UE5.8 and the recorded installed baseline is UE5.8.2; neither establishes a compatibility pass.
2. Survey the connected city and record a repeatable route. Measure the environment alone, then the initial one-player/two-ally/three-German mission with the selected rifle, actions and UI. Do not impose a one-block boundary or fixed duration.
3. Warm shaders before repeatable captures; record startup/shader hitches separately. Keep route, workload and settings fixed across comparisons.
4. Record resolution, quality/upscaling, build mode, engine/plugins, hardware/driver, CPU/GPU frame times, mean/median/p95 frame times and peak memory. Verify the 1080p/60 FPS target; disclose failures rather than treating the target as achieved.
5. Run a separate bounded stress test with finite configured NPC loads at the same bottleneck. Record total roster versus active AI, navigation failures, frame-time changes and the first observed limit. Do not hide engaged actors, revive casualties or retain extra mission population without evaluation.

These are planned Paris measurements under the [Assignment 3 goal](../../Docs/Development/ASSIGNMENT3_GOAL_V1.md) and [acceptance checklist](../../Docs/Development/ASSIGNMENT3_ACCEPTANCE.md). No benchmark or runtime pass is claimed.

See [technical design](../../Docs/Design/TECHNICAL_DESIGN.md) and [raw inventory](hardware_2026-09-17.json). The four pillars are Animation, Collision Detection, Pathfinding and Navigation, and NPC AI / Behavior Trees. Blender 5.2.2 LTS was installed and background-start verified on 30 September; old 4.5/configuration were preserved. This tool update does not reopen the stopped character pilot.
