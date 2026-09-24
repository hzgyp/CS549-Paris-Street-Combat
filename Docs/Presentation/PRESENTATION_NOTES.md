# Paris Street Combat — presentation notes

24 September 2026. Slides 1–6 total approximately four and a half minutes. Slide 7 is the closing Q&A slide.

## 1. Paris Street Combat (20 seconds)

Paris Street Combat is a single-player first-person squad mission in Unreal Engine 5, set during the August 1944 liberation period. Our goal is to make character actions, cover and NPC decisions work together. This image illustrates the intended experience. It is a concept, not a gameplay screenshot.

## 2. WW2 – France Liberation (35 seconds)

France Liberation is Meshingun Studio’s environment pack. It provides a large existing city with modular architecture, street props, textures, materials and environment-building tools. This gives us the visual setting for street combat. We can spend more of our effort on the interactive experience instead of building the whole city. The image is the supplier’s showcase. It does not demonstrate our gameplay. Soldier and weapon assets will be selected separately.

## 3. Mission progression and checkpoints (45 seconds)

The flow is now a general mission structure rather than a fixed sequence of locations. The player works through objectives such as reaching a point or clearing an assigned group. Completing an objective updates progress and can save a checkpoint at a selected safe boundary. If the player dies, retry restores the latest saved mission state, or returns to the beginning when no checkpoint exists. A checkpoint records the state we choose to preserve, including ammunition and relevant NPC status. It does not automatically refill ammunition or replace fallen allies. Checkpoint locations, resource supplies and reinforcement rules will be decided during mission design and playtesting.

## 4. Four pillars and concrete work (65 seconds)

The four pillars describe the work we will own. Animation means making purchased movement and weapon actions work on our characters, then keeping the transitions and timing coherent. Collision means checking how characters contact the scene and what a shot actually hits. Friendly-fire rules are a separate gameplay choice. Navigation means getting soldiers through the actual streets without everyone occupying the same destination or blocking a narrow passage. We will begin with Unreal’s NavMesh and MoveTo instead of committing to a separate A* implementation. NPC AI decides what soldiers do: observe, move, engage, search, or regroup. Individual decisions need simple squad coordination so roles and positions remain coherent as the population increases.

## 5. Proposed technical stack (40 seconds)

Our proposed stack stays inside Unreal Engine 5. Blueprints connect the character systems, NPC decisions, UI and mission state. Animation Blueprints control motion, with IK Retargeter available when purchased clips use a different skeleton. NavMesh supports movement, while Behavior Trees and perception support NPC decisions. We will add a small squad coordinator for shared assignments. UMG provides the UI, and SaveGame can store selected checkpoint data. The first technical check is compatibility between the environment, engine version and chosen soldier and weapon assets.

## 6. Hardest expected challenges (65 seconds)

We expect two main challenges. The first is integrating gameplay into the purchased environment. A health display or ammunition counter is only useful when it agrees with the actual character and weapon state. Likewise, characters need to move naturally around buildings and cover, and shot feedback must agree with collision results. This requires scene configuration, gameplay integration and visual checking. The second challenge is planning NPC movement and behavior as their number increases. Separate routes alone do not make a squad cooperate. We need shared assignments with individual perception and decisions, different destinations, and recovery when characters block one another. We must test whether the result looks coherent and whether the simulation remains responsive. Coding tools can help implement these parts, but judging their behavior in the actual city requires our own editor work and playtesting.

## 7. Q&A

Questions and discussion.
