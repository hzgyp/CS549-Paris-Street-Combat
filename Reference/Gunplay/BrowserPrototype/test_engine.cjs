/* Run: node test_engine.cjs. No package installation or network required. */
const assert = require('node:assert/strict');
const E = require('./engine.js');
const results = [];
function test(name, fn) { fn(); results.push({ name, status: 'PASS' }); }
function playing() { const g = E.createGame(); E.start(g); return g; }
function tick(g, seconds, input = {}) {
  for (let left = seconds; left > 1e-8; left -= 0.05) E.update(g, Math.min(left, 0.05), input);
}
function quiet(g) { for (const e of g.enemies) e.fireTimer = 1e9; return g; }
function aim(g, target) {
  const eye = E.eye(g.player), dx = target.x - eye.x, dz = target.z - eye.z;
  g.player.yaw = Math.atan2(-dx, -dz);
  g.player.pitch = Math.atan2(target.y - eye.y, Math.hypot(dx, dz));
}
function walkTo(g, target) {
  for (let n = 0; n < 4000; n++) {
    const dx = target.x - g.player.x, dz = target.z - g.player.z;
    if (Math.hypot(dx, dz) < 0.22 || g.phase !== 'playing') return;
    E.update(g, 0.05, { forward: 1, sprint: true, yaw: Math.atan2(-dx, -dz), pitch: 0 });
    assert(E.canOccupy(g, g.player.x, g.player.z), 'The scripted walk entered cover.');
  }
  assert.fail('Scripted walk got stuck before ' + JSON.stringify(target));
}
function clearAt(g, enemy) {
  aim(g, { x: enemy.x, y: enemy.y + 1.5, z: enemy.z });
  assert.equal(E.fire(g).kind, 'enemy');
  tick(g, 0.3);
  assert.equal(E.fire(g).kind, 'enemy');
  assert.equal(enemy.alive, false);
  tick(g, 0.3);
}

test('Fresh state is independent, serializable and has the intended small encounter', () => {
  const a = E.createGame(), b = E.createGame();
  assert.equal(a.allies.length, 4); assert.equal(a.enemies.length, 2);
  assert.equal(a.obstacles.filter(o => o.destructible).length, 1);
  a.obstacles[0].active = false;
  assert.equal(b.obstacles[0].active, true);
  assert.deepEqual(JSON.parse(JSON.stringify(b)), b);
  assert(E.canOccupy(b, b.player.x, b.player.z));
});

test('Ready and paused states freeze movement, combat, reload and elapsed time', () => {
  const g = E.createGame(), before = JSON.stringify(g);
  E.update(g, 0.1, { forward: 1 });
  assert.equal(JSON.stringify(g), before);
  assert.equal(E.fire(g).kind, 'blocked');
  E.update(g, 0, { start: true }); assert.equal(g.phase, 'playing');
  E.fire(g); E.reload(g); E.setPaused(g, true);
  const paused = JSON.stringify(g);
  tick(g, 3, { forward: 1 }); assert.equal(JSON.stringify(g), paused);
  assert.equal(E.fire(g).kind, 'blocked');
  E.setPaused(g, false); tick(g, 0.2); assert(g.time > 0);
});

test('Sprint collision stops before thin cover and diagonal input slides alongside it', () => {
  const g = quiet(playing());
  const wall = g.obstacles.find(o => o.id === 'sandbag-1');
  g.player.x = wall.x; g.player.z = wall.z + 5;
  tick(g, 2, { forward: 1, sprint: true });
  assert(g.player.z >= wall.z + wall.depth / 2 + E.PLAYER_RADIUS - 1e-6);
  const oldX = g.player.x;
  tick(g, 0.4, { forward: 1, strafe: 1 });
  assert(g.player.x > oldX + 0.5);
  assert(E.canOccupy(g, g.player.x, g.player.z));
  g.player.x = 37; g.player.z = 20;
  tick(g, 2, { strafe: 1, sprint: true });
  assert(g.player.x <= E.WORLD.bounds.maxX - E.PLAYER_RADIUS);
});

test('Diagonal movement is normalized and crouching changes speed and eye height', () => {
  const straight = quiet(playing()), diagonal = quiet(playing());
  tick(straight, 0.5, { forward: 1 }); tick(diagonal, 0.5, { forward: 1, strafe: 1 });
  assert(Math.abs(straight.player.distance - diagonal.player.distance) < 1e-8);
  const standingEye = E.eye(straight.player).y;
  tick(straight, 0.05, { crouch: true, forward: 1 });
  assert.equal(E.eye(straight.player).y, 1.08);
  assert(standingEye > E.eye(straight.player).y);
});

test('Nearest cover blocks rifle shots and LOS; visible targets take two hits', () => {
  const g = quiet(playing()), cover = g.obstacles.find(o => o.id === 'wood-cover');
  g.player.x = cover.x; g.player.z = cover.z + 5; g.player.y = 0;
  const enemy = g.enemies[0];
  enemy.x = cover.x; enemy.z = cover.z - 4; enemy.y = 0;
  aim(g, { x: enemy.x, y: 0.9, z: enemy.z });
  const hit = E.fire(g);
  assert.equal(hit.kind, 'cover'); assert.equal(hit.obstacleId, cover.id);
  assert.equal(enemy.health, 100);
  assert(!E.lineOfSight(g, E.eye(g.player), { x: enemy.x, y: 0.9, z: enemy.z }));
  g.player.x = cover.x + 5;
  tick(g, 0.3);
  clearAt(g, enemy);
  assert.equal(g.defeated, 1);
});

test('Shooting removes only the destructible cover and opens movement plus visibility', () => {
  const g = quiet(playing()), cover = g.obstacles.find(o => o.destructible);
  g.player.x = cover.x; g.player.z = cover.z + 5; g.player.y = 0;
  aim(g, { x: cover.x, y: 0.7, z: cover.z });
  assert(!E.canOccupy(g, cover.x, cover.z));
  E.fire(g); tick(g, 0.3); const broken = E.fire(g);
  assert.equal(broken.destroyed, true); assert.equal(cover.active, false);
  assert(E.canOccupy(g, cover.x, cover.z));
  assert(E.lineOfSight(g, { x: cover.x, y: 0.7, z: cover.z + 3 },
    { x: cover.x, y: 0.7, z: cover.z - 3 }));
  const solid = g.obstacles.find(o => o.id === 'tank-1');
  g.player.x = solid.x; g.player.z = solid.z + 6;
  aim(g, { x: solid.x, y: 1, z: solid.z });
  tick(g, 0.3); assert.equal(E.fire(g).obstacleId, solid.id);
  assert.equal(solid.active, true); assert.equal(solid.health, 100);
});

test('Reload and fire cooldown cannot create ammunition or permit firing early', () => {
  const g = quiet(playing());
  g.player.pitch = 0.7;
  for (let i = 0; i < 8; i++) {
    assert.notEqual(E.fire(g).kind, 'blocked');
    assert.equal(E.fire(g).reason, 'cooldown'); tick(g, 0.3);
  }
  assert.equal(g.player.ammo, 0); assert.equal(E.fire(g).kind, 'empty');
  g.player.reserve = 3; assert(E.reload(g)); assert.equal(E.reload(g), false);
  assert.equal(E.fire(g).reason, 'reload'); tick(g, 1.9);
  assert.equal(g.player.ammo, 0); tick(g, 0.1);
  assert.equal(g.player.ammo, 3); assert.equal(g.player.reserve, 0);
  assert.equal(g.player.reloading, false); assert.equal(E.reload(g), false);
});

test('Terrain blocks a shot into the bluff and rays choose the nearest defender', () => {
  const g = quiet(playing());
  assert.equal(E.raycast(g, { x: -35, y: 1.5, z: -62 }, { x: 0, y: 0, z: -1 }).terrain, true);
  g.obstacles = [];
  g.enemies[0] = { ...g.enemies[0], x: 0, z: 4, y: 0 };
  g.enemies[1] = { ...g.enemies[1], x: 0, z: -4, y: 0 };
  const hit = E.raycast(g, { x: 0, y: 1.4, z: 15 }, { x: 0, y: 0, z: -1 });
  assert.equal(hit.enemyId, 'defender-1'); assert(hit.distance < 12);
});

test('Cover protects the crouching player from enemy fire', () => {
  const g = playing(); g.enemies[1].alive = false;
  const e = g.enemies[0]; e.fireTimer = 0;
  g.player.x = -11; g.player.z = -36; g.player.y = 0;
  tick(g, 0.1, { crouch: true }); assert.equal(g.player.health, 100);
  tick(g, 0.1); assert(g.player.health < 100);
  g.player.health = 4; e.fireTimer = 0;
  tick(g, 0.1); assert.equal(g.phase, 'dead');
  assert.equal(E.fire(g).kind, 'blocked');
});

test('Authored ally route is traversable and allies eventually reach the objective', () => {
  const g = quiet(playing());
  tick(g, 100);
  for (const ally of g.allies) {
    assert.equal(ally.waypoint, E.WORLD.route.length, ally.id + ' got stuck.');
    assert(E.canOccupy(g, ally.x, ally.z, 0.3));
  }
});

test('Mission requires both defenders; a scripted movement-and-shooting run can win', () => {
  const g = playing();
  for (const point of E.WORLD.route.slice(0, 8)) walkTo(g, point);
  clearAt(g, g.enemies[0]);
  walkTo(g, E.WORLD.route[8]);
  walkTo(g, E.WORLD.route[9]);
  clearAt(g, g.enemies[1]);
  for (const point of E.WORLD.route.slice(10)) walkTo(g, point);
  assert.equal(g.phase, 'won'); assert.equal(g.objective.complete, true);
  const before = JSON.stringify(g); tick(g, 2, { forward: 1 });
  assert.equal(JSON.stringify(g), before);
  const initial = E.createGame(); E.reset(g); assert.deepEqual(g, initial);
  const premature = quiet(playing());
  premature.player.x = 5; premature.player.z = -79; premature.player.y = E.heightAt(5, -79);
  tick(premature, 0.1); assert.equal(premature.phase, 'playing');
});

test('A longer western flank also reaches both defenders and wins under live fire', () => {
  const g = playing();
  for (const point of [{ x: -30, z: 20 }, { x: -33, z: -40 }]) walkTo(g, point);
  clearAt(g, g.enemies[0]);
  for (const point of [{ x: -32, z: -57 }, { x: -6, z: -62 }, { x: 5, z: -62 }]) walkTo(g, point);
  clearAt(g, g.enemies[1]);
  for (const point of E.WORLD.route.slice(10)) walkTo(g, point);
  assert.equal(g.phase, 'won');
  assert(g.player.health > 0 && g.player.health < 100);
  assert.equal(g.player.ammo, 4);
});

console.log(JSON.stringify({ suite: 'Normandy FPS simulation', passed: results.length, results }, null, 2));
