# Proposal visual creation record

Both reports embed the regenerated street concept and formal game flowchart. The two older ImageGen outputs recorded below are superseded and retained only for provenance.

## Current reference-guided street concept

`paris-six-character-concept.png` was regenerated with the built-in OpenAI ImageGen tool using both official gallery images, `paris-environment-01.jpg` and `paris-environment-02.jpg`, as appearance references. The panoramic first-person composition shows connected streets, two allies and three enemies, representing the initial roster rather than a final cap. It is new concept art, not a supplier screenshot or verified layout. The unchanged supplier images remain reference inputs and are not separately embedded. See [STREET_MOCKUP_PROMPT.md](STREET_MOCKUP_PROMPT.md) for the exact prompt and generation record.

## Current formal game flowchart

[Tools/build_mission_flowchart.py](../../../Tools/build_mission_flowchart.py) deterministically generates `paris-mission-flowchart.svg`, `paris-mission-flowchart.png`, and the editable `paris-mission-flowchart.mmd` description. This is an AI-assisted conceptual visual authored in code, not an ImageGen output. The code and Mermaid record the operative game rules and are the reproducible source; no vendor photograph, documentation image or map was used as generation input.

Design brief: show a configurable roster initialized with one player, two Allied NPCs and three German NPCs; ordered Reach rally A → Clear assigned group B → Reach end C objectives; success after the ordered sequence; player death during any playing stage leading to failure; and full mission restart from success/failure. Reach checks the living player. ClearArea requires a nonempty fully registered finite group and zero living members. Restart restores the configured roster and objective state. Six is an initial test configuration, not a final population limit. Additional finite NPC groups, individual patrol/search settings and intermediate objectives are later data-driven extensions subject to evaluation. A, B and C are logical mission markers, not claims about France Liberation's actual geography.

## Superseded street-scene ImageGen image

Generated on 23 September 2026 using the built-in OpenAI ImageGen tool.

Retained workspace asset: `paris-six-character-concept-text-only-v1.png`.

The output is no longer embedded in either report. It is concept art generated from text, not vendor images; its invented compact-street geometry was rejected as a mission restriction.

## Original prompt

Use case: historical-scene. Asset type: AI-generated concept mockup for a university computer graphics game proposal, landscape 1536x1024. Create one image containing two equal wide panels stacked vertically with a thin white gutter, no writing or labels. Both panels depict the SAME small fictional Paris street during August 1944 liberation, rendered as a restrained Unreal Engine game concept: cream stone facades, cobblestones, one damaged low masonry barricade, a side alley, static abandoned street props. Fixed daylight. Top panel: first-person view with a period rifle and hands visible in lower right foreground, two Allied soldier teammates in brown/olive uniforms taking positions nearby, three German soldiers in subdued gray uniforms farther down the street behind cover. Total encounter is six characters including the unseen first-person player; do not add civilians, background crowds, tanks, planes or vehicles in motion. No firing, injury, blood, explosions or graphic content. Bottom panel: an oblique elevated tactical view of the same compact street, showing exactly three blue circular markers for allied positions including the player and three red circular markers for enemy positions. Thin blue and red route arrows follow the walkable street and side alley around the barricade. Show one objective as a small gold ring at the far street end. Concept art, not a claim of actual implemented gameplay or exact historical reconstruction. Clean, legible composition suitable for inclusion at 6.9 inches wide on a proposal page. No text, watermarks, insignia or logos.

## Targeted correction prompt

Edit the provided two-panel concept image. Change only the TOP panel: remove the German soldier standing behind the low stone wall just left of the center of the image (the soldier between the far-left distant soldier and the soldier near the right-side facade). Preserve that wall and fill the removed soldier area naturally with the street background. The top panel must contain exactly two Allied teammates in the foreground, exactly three distant German soldiers, and the first-person player's hands/rifle. Keep the bottom tactical panel completely unchanged with its three blue and three red markers. Preserve all other composition, styling, dimensions and lighting. No new people, no text.

## Superseded connected-city ImageGen schematic

Retained workspace asset: `paris-connected-mission-concept.png`. Generated with the built-in OpenAI ImageGen tool from text only; no vendor image input. The image communicates the earlier intended logic and does not reproduce actual street geometry. It is no longer embedded in either current report.

Use case: infographic-diagram. Create a very wide landscape schematic, aspect ratio 3:1, white background, for a university game project proposal. It is an abstract MISSION FLOW diagram, not an actual map. Show three clearly separated areas from left to right labelled exactly 'APPROACH', 'OBJECTIVE', 'EXIT'. Use large crisp black sans-serif labels, readable when printed at 6 inches wide. One dark gray main route links all three areas. A thin dashed alternate route branches between approach and objective then rejoins, showing a real player choice in the concept. Use only exactly THREE blue circular soldier markers clustered in the APPROACH area: one labelled 'P' and two labelled 'A'. Use only exactly THREE red circular soldier markers across the approach-to-objective and objective region, each labelled 'G'. A small gold outlined diamond at OBJECTIVE and a simple black exit arrow at EXIT. Two short blue arrows indicate the allied group advances together; small red arrows indicate guards can move or reposition. No duplicate soldier icons elsewhere, no extra people or shapes resembling soldier markers. No drawn buildings, city blocks, street geometry, map grid, photorealism, terrain, landmarks, weapons or combat detail. The diagram should communicate a six-person squad skirmish moving across a connected mission route, not six people trapped in an arena. Keep generous horizontal separation, precise alignment and readable arrows. Add a small bottom note exactly 'Concept only - route selected in Unreal'. Do not imply this is the actual France Liberation layout. Restrained blue, muted red and gold, minimal professional diagram.
