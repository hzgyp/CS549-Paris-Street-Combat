# Primary Development Workstation

**Confirmed by Yupu Guo · Inventory captured 17 September 2026 · Development plan synchronized 21 September 2026**

This Alienware Aurora R13 is the primary development desktop. Project location: `D:\0.Rutgers\CS549\Project`. **Blueprints are required as the primary gameplay implementation approach.** C++ is an exception for a demonstrated need, not the default development path.

| Component | Observed configuration |
|---|---|
| CPU | Intel Core i9-12900F; 16 cores, 24 logical processors |
| Memory | 32 GB installed, 2 × 16 GB; approximately 31.8 GiB visible to Windows; reported DDR5-4800 modules configured at 4400 MT/s |
| GPU | NVIDIA GeForce RTX 3080, 10,240 MiB VRAM (10 GiB); NVIDIA-reported driver 616.92 |
| OS | Windows 11 Pro Education, build 26200 |
| C: | Crucial CT4000P3SSD8 NVMe SSD; volume 3,722.9 GiB total, 1,769.6 GiB free |
| D: | Separate Crucial CT4000P3SSD8 NVMe SSD; volume 3,725.9 GiB total, 676.2 GiB free |
| Storage health | Windows reports both volumes/disks Healthy |
| Unreal detection | No Epic Launcher registered installation found in the checked manifest; no `.uproject` found in the project review. A custom installation elsewhere is not ruled out |

Capacity is shown in GiB, not decimal manufacturer GB/TB. This was a read-only inventory using Windows system/storage information and NVIDIA reporting. No synthetic benchmark, sustained thermal test, storage throughput test or Unreal performance capture was run. A Healthy flag is not a full hardware diagnostic. Serial numbers and machine/user identifiers are not included in the saved snapshot.

## Suitability assessment

The machine meets Epic's published recommended 32 GB system-memory and 8 GB-or-more graphics-memory levels. It is a reasonable primary machine for this compact Blueprint project. That is a planning assessment, not a promise of cinematic quality at 60 fps. [Epic hardware requirements](https://dev.epicgames.com/documentation/en-us/unreal-engine/hardware-and-software-specifications-for-unreal-engine)

Start packaged profiling at 1920×1080 with recorded quality settings. Treat 60 fps as a target and measure median/p95 frame time, CPU/GPU timings and memory use. Large textures, volumetric effects and high shadow/reflection settings can pressure 10 GiB VRAM. Change settings based on the graybox/asset lab, not GPU name alone. A memory upgrade is not presently required by this assessment.

## Storage and version plan

Keep source project files on D: as requested. C: currently has more free capacity and is a candidate for engine installation and disposable caches if an installation is needed; this document does not install, move or reconfigure anything. Reserve an initial 200–300 GiB project/asset allowance on D: as a planning budget, not a measured requirement. Track actual growth before downloading large asset packs.

Record an agreed engine **major.minor.patch**, project plugins and the working driver version after the first project opens and packages. Do not select an engine version solely because the documentation currently defaults to it. Store required `.uproject`, configuration and Unreal assets with an agreed binary-asset policy; generated caches and build artifacts should not become accidental source dependencies.

## First measurement gate

1. Locate/install and test the agreed engine, record the exact major.minor.patch, and create a Blueprint First Person graybox. The engine version remains pending this lab.
2. Package Windows and measure the environment without NPC load; then measure the same 30–60-second landing-to-first-cover path with the scripted craft/ramp, at least three allies, weapon, shallow-water feedback and surface effects. Add the fourth ally only after stability.
3. Warm shaders before collecting repeatable captures; separately record startup/shader hitches. Use the same route and duration for each configuration.
4. Capture settings, resolution, build mode, engine version, CPU/GPU frame time, median/p95 frame time and peak memory. Compare against the 1080p/approximately 60 fps target without claiming it has already been met.
5. After the MVP, profile the full mission with four allies, two defenders, cover change and controlled bunker destruction. Dynamic weather and day/night progression are outside the current Assignment 2 semester scope; they are not part of this measurement gate.

These are planned measurements for the [Assignment 2 working proposal](../Docs/proposal/CS549_Normandy_Assignment2_Proposal.md); the browser mockup supplies no Unreal performance evidence.

See [Blueprint specification](../HistoricalReference/06_BLUEPRINT_SPECIFICATION.md) and [raw inventory](hardware_2026-09-17.json). The three core pillars remain Rendering, Animation and Collision Detection.
