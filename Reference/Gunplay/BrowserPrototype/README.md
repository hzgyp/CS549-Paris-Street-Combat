# Normandy / Beachhead

A small 3D FPS concept mockup created for Assignment 1. It demonstrates **Rendering, Animation, and Collision Detection** through a playable beach advance.

The [Assignment 2 specification](../proposal/CS549_Normandy_Assignment2_Proposal.md) defines the current Unreal project. Its MVP is a 30–60-second landing-to-first-cover sequence, with at least three allies disembarking and four allies targeted for the complete mission. This browser mockup does not implement a moving landing craft, ramp opening and disembarkation, shallow-water movement feedback, or the proposed final bunker destruction. It is not the Assignment 2 MVP or a packaged Unreal build. Gameplay development will primarily use Blueprints; the exact Unreal version and measured performance await the first Unreal lab.

## Run locally

No cloud hosting or domain is needed. Keep this entire folder together, including `vendor/`, and use a desktop browser with **WebGL 2** support.

With Python 3 installed, open a terminal in this folder and run:

```sh
python3 serve.py
```

On Windows, use `py serve.py`. From the repository root, use `python3 Docs/prototype/serve.py` instead.

Open **[http://127.0.0.1:8080](http://127.0.0.1:8080)** and select **Begin landing**. Keep the terminal running while you play; press **Ctrl+C** there to stop the server. If port 8080 is occupied, run `python3 serve.py --port 8081` and open `http://127.0.0.1:8081`.

**For reviewers:** `127.0.0.1` always refers to your own computer. This server accepts only local connections, so someone elsewhere cannot open your running demo through that address. Share the complete prototype folder; each reviewer can run the command on their own computer and open their local address.

**Without Python:** open `index.html` directly in the browser. The bundled demo also works this way and needs no build step, login, Unreal Engine, or network connection.

**Previously published alternative:** the [FPS website](https://cs549-normandy-beachhead.cicerocatobrutus.chatgpt.site) was verified as publicly accessible on 15 September 2026. See the [dated comparison](../documentation/DEMO_VERSION_CHECK_2026-09-15.md); availability and parity have not been rechecked for Assignment 2.

## Controls

| Action | Control |
|---|---|
| Move | W, A, S, D |
| Look | Mouse after entering the view; drag if pointer lock is unavailable; arrow keys also work |
| Fire | Left mouse button or Space |
| Aim | Hold the right mouse button; F toggles aiming |
| Reload | R |
| Sprint | Hold Shift |
| Toggle crouch | C |
| Pause / release mouse | Esc |
| Continue | Resume mission |
| Start again | Restart or Try again |

Use **Scene settings** to compare wet sand, fog, and shadows, or toggle sound. The weapon holds eight rounds; reload before continuing when it is empty.

## Suggested demonstration

1. Begin the landing and look across the landing craft, beach obstacles, and coastal defenses.
2. Move between cover objects toward the bunker. Aim and fire at the two defenders; reload and observe the weapon movement.
3. Try moving into solid cover and firing at it. Objects should block movement and shots.
4. Shoot the designated wooden cover until it breaks, then cross the opening. Its visible state and collision should change together.
5. Compare wet sand, fog, and shadows from one viewpoint to show the rendering changes.
6. Clear the defenders and reach the bunker objective. Use Restart to restore the mission, including health and cover.

## Scope

The scene includes one player weapon, four allies, two defenders, and one destructible wooden cover object. The player can move, aim, shoot, reload, crouch, take damage, complete the objective, or restart after defeat. Allied characters provide simple supporting movement. This short encounter is smaller than the proposed semester mission.

Models are built from simple 3D shapes. Character movement, aiming, recoil, and reloading illustrate action transitions. Beach materials, light, fog, and shadows illustrate visual settings. Movement and shot checks illustrate collision behavior.

This browser prototype is a stylized proposal mockup. It does not reproduce the final Unreal scene, Unreal Animation Blueprints or navigation tools, historical geography, or the intended historical speech and soundtrack. Browser performance is not a measurement of the future Unreal project.

## Files and checks

| File | Role |
|---|---|
| `index.html` | Start screen, game view, and controls |
| `style.css` | Interface layout and appearance |
| `engine.js` | Movement, collision, combat, NPC, and mission state |
| `scene.js` | Procedural 3D environment and visual presentation |
| `app.js` | Input handling, interface, and frame updates |
| `serve.py` | Optional Python 3 server at `http://127.0.0.1:8080`, accessible only on the computer running it |
| `vendor/three.js` | Bundled Three.js renderer for offline use |
| `vendor/THREE-LICENSE.txt` | Three.js MIT license |
| `test_engine.cjs` | Automated engine checks, run with `node test_engine.cjs` |
| `test_controller.cjs` | Controller checks with simulated browser APIs, run with `node test_controller.cjs` |
| `public/og.png` | AI-generated concept poster for social previews |
| `public/PROVENANCE.md` | Poster prompt and bundled library source |

See [release checks](../documentation/RELEASE_CHECKS.md) for the actual verification record. Automated checks do not replace playing the demo in the browser used for presentation.

Three.js r180 is bundled locally under the MIT license. The offline demo needs no external fonts, media downloads, tracking, or accounts.
