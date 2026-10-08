# Walkable G1 start is not visually suitable

8 October 2026. G1 ReadyV2 and TravelV3 pass native standing/resources and
player movement from old S[-3162.5,-25937.5,110.116898]cm, but screenshots show
a largely dark initial view. Day is loaded/visible, movable sun16.5/skylight2.5,
real player camera266.35cm and yaw35; neither broad lighting nor FP repair is
supported by this evidence.

ViewV1 cardinal screenshots show exterior through openings and opaque dark
interior faces. The camera is inside the visible BP_ProxyActor_C_488 bounds:
centre[-2933.519,-26300.557,598.849], extent[947.208,953.035,500.763]cm,
residence02a_APPROX. Bounds alone do not prove which triangle occludes a pixel;
the actual views establish that this initial staging is unsuitable. Horizontal
visibility ray misses are insufficient because rendered proxy surfaces and
collision traces do not establish identical free space.

Do not hide the building, change city collision, brighten the whole map, move
the FP camera or repair the accepted character to rescue this site. Preserve
the old physical/navigation proofs and raw white-cell sources, while marking
old S staging unavailable for spawn use. This is not proof that all its cells
are physically blocked or that the whole map is dark.

A different bounded plan G1_NEARBANK_STAGING_PLAN selects the previously
physically reached near-bank assembly using exact25cm white centres, verifies
initial views/standing unsaved, then changes only the owned mission staging.
First negative stops it; no coordinate/brightness/pose sweep.

Private evidence: Evidence/G1MissionV1/view_v1_20261008, ready_v2_20261008,
travel_v2_20261008 and travel_v3_20261008. Final manifest authenticates those
raw files without rewriting their statuses.

Resolution evidence: spawn_view_v1's actual initial/four-cardinal originals were reviewed before any new staging save; all six original bodies/resources and703 guards passed. staging_author_v2 then saves only the three Allied transforms/config fingerprint in the owned mission map, retaining defenders/navigation/city. Current-map TravelV4 passes actual player and both-Allies crossing. FunctionalV4's current-map Ready original also shows a readable exterior and native G1 HUD; its ready_visual_review.json records the actual review. The old S stays rejected for production spawning even though isolated save unit tests may use its measured position. Raw grid/old navigation proofs remain unchanged; no camera, lighting, city proxy, model or finger correction was made.
