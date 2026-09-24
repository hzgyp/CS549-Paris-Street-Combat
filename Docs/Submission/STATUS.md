# Course submission and approval status

Updated 23 September 2026. Report preparation and external course approval are separate requirements.

## Prepared reports

- [Proposal 1](../Proposal/CS549_Assignment1_Proposal.pdf): revised Assignment 1 report, at most two pages, with group roster/NetIDs/leader, four pillars, a concept summary in the required range, a pillar/work table, regenerated AI street concept and formal game flowchart.
- [Proposal 2](../Proposal/CS549_Assignment2_Proposal.pdf): separate Assignment 2 report, at most two pages, with PRD, user stories, MoSCoW priorities, technical specification, AI strategy, performance constraints, pillar/work table, regenerated street concept, game flowchart and narrow MVP evidence plan.
- Editable Word and Markdown counterparts are in [Docs/Proposal](../Proposal/README.md). The long-form [project proposal](../Proposal/PROJECT_PROPOSAL.md) supplies implementation detail beyond the submission page limit.

The latest team request makes six soldiers an initial configuration, not the final population limit, and adds intermediate mission objectives across a connected part of the existing city. The initial roster is one Allied player, two Allied NPCs and three German NPCs. Additional NPCs, finite groups and objective stages may be configured after pacing, navigation and performance evaluation. All NPCs share AI code with per-NPC team, role, group, patrol-route and search-zone data. The proposed pillars remain Animation, Collision Detection, Pathfinding and Navigation, and NPC AI / Behavior Trees; rendering and physical simulation support implementation.

The flow is now general: start/resume, pursue a current objective, update progress and continue or complete. Reach/Clear are example objective types; their sequence and geography remain open. Checkpoints at selected safe objective boundaries are proposed as a Should feature. Retry restores a saved objective/player/NPC snapshot, falling back to the initial state if none exists. A full new-mission restart remains available. Saving does not automatically heal, refill or revive; resupply/reinforcement rules remain open. During normal forward progression, casualties and ammunition persist.

Population expansion remains a proposed evaluation, not an implemented or approved headcount. A squad coordinator assigns distinct support goals while each NPC retains separate controller/Blackboard/perception state. NavMesh/MoveTo is the navigation baseline; destination selection, local avoidance, waiting and bounded replanning are team work. Custom tactical A* is optional. Compare small finite NPC additions through pacing, bottleneck, responsiveness and frame-time checks before increasing the active-AI budget. Do not hide engaged actors or silently replace casualties. The main challenge is coherent UI/physical interactions inside the city plus coordinated NPC movement and decisions. Version-control tooling remains undecided.

The planned approach, intermediate objectives, end point and alternate route require an editor survey of actual connectivity, collision, sightlines, NavMesh coverage and travel time. No one-block boundary, fixed mission duration or fixed graph-node cap is assumed. Full-route, ally catch-up/bottleneck, sight-loss, no-teleport, actor-persistence, objective-order/group-counter and configurable-roster restart tests are planned, not passed. The existing documentation is a tools/material guide, not validated evidence of a playable route.

Both reports include the regenerated [street concept](../Proposal/Visuals/paris-six-character-concept.png), made with OpenAI ImageGen using both official gallery images as appearance references. The unchanged supplier images remain local inputs and are not separately embedded. The original text-only mockup is archived as `paris-six-character-concept-text-only-v1.png`; it and the earlier ImageGen mission schematic remain provenance only. Both reports also include the [formal flowchart](../Proposal/Visuals/paris-mission-flowchart.svg), an AI-assisted conceptual visual generated deterministically in code from mission rules; its [Mermaid source](../Proposal/Visuals/paris-mission-flowchart.mmd) remains editable. It specifies progression and reset, not city geometry. No visual is a screenshot of implemented gameplay or proof of actual route connectivity. See [visual provenance](../Proposal/Visuals/README.md) and the [current image generation record](../Proposal/Visuals/STREET_MOCKUP_PROMPT.md).

The revised Proposal 2 uses numbered PRD, Technical Specification and MVP sections and the exact flowchart from Proposal 1. Its two-page final PDF and report content have been checked; see the [requirement-by-requirement review](ASSIGNMENT2_REQUIREMENTS_REVIEW.md). This content review does not establish approval or completion of course submission.

## Required before final submission

Assignment 2 explicitly says: "You cannot submit the final assignment documents until this step is complete." The step is formal concept/pillar approval and mentor assignment in an email thread involving the Instructor, Danrui and Sen.

No actual approval thread or assigned mentor is established in the materials reviewed. Obtain or locate the real email evidence for this revised concept and pillar set. Export that thread as a screenshot or PDF and include it as the required attachment, outside the two-page report limit. Do not replace it with a draft, inferred approval, or the former Normandy approval.

The [approval email draft](APPROVAL_EMAIL_DRAFT.md) is prepared but not sent. It identifies the new Assignment 1 report as the concept attachment and the Assignment 2 report as the engineering plan. No email or course submission was sent during this task.

Also verify Canvas group registration, actual course deadlines and any updated instructor formatting instructions. These are administrative follow-ups, not claimed completed work. The old combined English/Chinese PDFs remain superseded snapshots; the Chinese file is not a translation of the new reports.
