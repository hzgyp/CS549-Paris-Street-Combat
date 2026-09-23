# Demo asset provenance

This record belongs to the Assignment 1 browser concept mockup, retained under `Docs/prototype/`. It is not an asset or implementation record for the Assignment 2 Unreal MVP. The current project scope is recorded in `Docs/proposal/CS549_Normandy_Assignment2_Proposal.md` relative to the repository root; the playable browser scene remains a stylized design approximation.

## Scene and sound

The playable scene uses procedural geometry, generated canvas textures, and synthesized Web Audio effects. The two proposal concept PNGs are separate design references and are not used as gameplay screenshots.

## Bundled rendering library

- Library: Three.js r180 (0.180.0).
- Official package source: https://unpkg.com/three@0.180.0/build/three.cjs
- License source: https://unpkg.com/three@0.180.0/LICENSE
- Local license: `../vendor/THREE-LICENSE.txt`.
- The unmodified CommonJS build is wrapped in a function with a local `exports` object and exposed as `globalThis.THREE` for offline classic-script loading.

## Social preview poster

- File: `og.png`.
- Generated with OpenAI image generation on 14 September 2026.
- Original generation: `01a0a22a-a362-70a1-b30e-afa304aefba2/exec-48fb94d6-cd76-4f02-83a6-2cb8efe24951.png`.
- Text-only generation; no reference images supplied.
- This is illustrative concept artwork, not a screenshot of the running game.
- The poster is used for link previews at https://cs549-normandy-beachhead.cicerocatobrutus.chatgpt.site/public/og.png.

### Exact prompt

```text
Create ONE finished landscape 16:9 social preview card for a student browser game demo. Title exactly 'NORMANDY', subtitle exactly 'BEACHHEAD', small footer exactly 'FIRST-PERSON CONCEPT / CS549'. Visual style matches a lightweight stylized 3D browser FPS: low-poly sandy Normandy coast with wet sand, small gray landing craft near surf, several steel hedgehog obstacles, a weathered olive armored wreck, and a modest concrete bunker beneath grassy coastal bluffs. Restrained khaki olive, charcoal, warm sand, muted sea blue, and cream text; warm hazy coastal light, simple geometric models, attractive game concept illustration rather than a realistic engine screenshot. Composition: bold large elegant cream serif title on the left with small widely spaced uppercase sans-serif supporting text; coastal scene stretches across the right and lower half. Make a cohesive finished poster with generous margins, legible typography for small link previews and crisp detail. No game HUD, no bodies/gore, no logos or watermarks, no additional words. This is a social card for the actual simple playable first-person concept, with an original illustrated scene.
```
