# Project briefing — 24 September 2026

[Open the editable PowerPoint](CS549_Paris_Street_Combat_Presentation_2026-09-24_Final.pptx).

Slides 1–6 cover the approximately 4.5-minute presentation. Slide 7 is a final Q&A slide with a large, centered, bold title. The deck follows the current Assignment 1 and Assignment 2 proposals and the instructor's briefing announcement.

Text, tables and the mission flowchart are native PowerPoint objects. The concept and supplier images are embedded pictures that can be moved, resized or replaced. The generated concept is labeled, and each relevant slide's notes include sources.

Open the Notes pane or Presenter View for the suggested script and timing. [Presentation notes](PRESENTATION_NOTES.md) provide the same script in a separate file for rehearsal.

| Main slide | Suggested time |
| --- | ---: |
| 1. Paris Street Combat | 20 seconds |
| 2. WW2 – France Liberation | 35 seconds |
| 3. Mission progression and checkpoints | 45 seconds |
| 4. Four pillars and concrete work | 65 seconds |
| 5. Proposed technical stack | 40 seconds |
| 6. Hardest expected challenges | 65 seconds |
| Total | 4 minutes 30 seconds |

The revised deck keeps slide 2 focused on the environment pack, removes Git/LFS as an unagreed commitment, and treats checkpoint placement as a proposed design choice. Navigation uses UE NavMesh as the baseline. The main challenges are UI and physical interaction integration, followed by NPC coordination as groups grow.

The plan remains a proposal. The deck does not claim implemented gameplay, verified map routes, tested engine compatibility, achieved performance or course approval.

The source builder is [build_project_briefing.mjs](../../Tools/build_project_briefing.mjs). Rebuilding with a new `BRIEFING_REVISION` writes a separate PPTX. Direct PowerPoint edits should be retained in a separately named copy because the builder does not import manual changes.
