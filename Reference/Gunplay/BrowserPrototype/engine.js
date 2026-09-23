/* Deterministic FPS simulation. Coordinates are metres; yaw 0 faces -Z.
 * Rendering, browser input and audio live in separate files. No dependencies. */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.NormandyEngine = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  const PLAYER_RADIUS = 0.34, MAGAZINE = 8, RELOAD_SECONDS = 2;
  const clamp = (n, a, b) => Math.max(a, Math.min(b, n));
  const finite = (n, fallback = 0) => Number.isFinite(n) ? n : fallback;
  const distance = (a, b) => Math.hypot(a.x - b.x, a.z - b.z);
  const clone = value => JSON.parse(JSON.stringify(value));
  function heightAt(x, z) { return z < -65 ? Math.min(7, (-z - 65) * 0.32) : 0; }
  function obstacle(id, type, x, z, width, depth, height, extra = {}) {
    // Ground the downhill edge so wide fortifications sit into the slope.
    return { id, type, x, z, width, depth, height, y: heightAt(x, z + depth / 2),
      rotation: 0, active: true, destructible: false, health: 100, ...extra };
  }
  const WORLD = {
    bounds: { minX: -38, maxX: 38, minZ: -97, maxZ: 25 },
    start: { x: 0, z: 21 },
    objective: { x: 5, z: -79, radius: 5 },
    route: [
      { x: 0, z: 14 }, { x: -7, z: 7 }, { x: -7, z: -3 },
      { x: 4, z: -10 }, { x: 4, z: -19 }, { x: -6, z: -27 },
      { x: -6, z: -34 }, { x: 0, z: -42 }, { x: 0, z: -53 },
      { x: 5, z: -62 }, { x: 5, z: -72 }, { x: 5, z: -79 }
    ],
    obstacles: [
      obstacle('hedgehog-1', 'hedgehog', -20, 10, 2.2, 2.2, 1.8),
      obstacle('hedgehog-2', 'hedgehog', -12, 7, 2.1, 2.1, 1.8),
      obstacle('hedgehog-3', 'hedgehog', 7, 9, 2.2, 2.2, 1.8),
      obstacle('hedgehog-4', 'hedgehog', 18, 6, 2.1, 2.1, 1.8),
      obstacle('hedgehog-5', 'hedgehog', -2, 2, 2.2, 2.2, 1.8),
      obstacle('hedgehog-6', 'hedgehog', 12, -4, 2.2, 2.2, 1.8),
      obstacle('hedgehog-7', 'hedgehog', -21, -9, 2.2, 2.2, 1.8),
      obstacle('hedgehog-8', 'hedgehog', 25, -12, 2.2, 2.2, 1.8),
      obstacle('gate-1', 'gate', -15, -1, 4.8, 1.7, 2.3),
      obstacle('gate-2', 'gate', 16, -15, 4.8, 1.7, 2.3),
      obstacle('gate-3', 'gate', -26, -19, 4.8, 1.7, 2.3),
      obstacle('stakes-1', 'stakes', -15, 16, 3, 2.1, 1.9),
      obstacle('stakes-2', 'stakes', 23, -1, 3, 2.1, 1.9),
      obstacle('sandbag-1', 'sandbag', -11, -17, 6, 1.6, 1.25),
      obstacle('sandbag-2', 'sandbag', 11, -25, 7, 1.6, 1.25),
      obstacle('tank-1', 'tank', -17, -27, 3.5, 6, 2.35),
      obstacle('wood-cover', 'crate', 2, -31, 2.8, 1.9, 1.55,
        { destructible: true, health: 100 }),
      obstacle('sandbag-3', 'sandbag', -12, -38, 8, 1.6, 1.25),
      obstacle('halftrack-1', 'halftrack', 13, -38, 3, 6, 2.2),
      obstacle('hedgehog-9', 'hedgehog', -20, -49, 2.2, 2.2, 1.8),
      obstacle('tank-2', 'tank', 22, -58, 3.6, 6, 2.4),
      obstacle('sandbag-4', 'sandbag', 12, -60, 8, 1.6, 1.25),
      obstacle('seawall-west', 'sandbag', -21, -69, 21, 2, 1.45),
      obstacle('seawall-east', 'sandbag', 22, -69, 24, 2, 1.45),
      obstacle('bunker', 'bunker', 5, -88, 18, 10, 7)
    ]
  };

  function createGame() {
    return {
      phase: 'ready', time: 0, sequence: 0, defeated: 0,
      player: { x: 0, z: 21, y: 0, yaw: 0, pitch: 0, health: 100,
        ammo: MAGAZINE, reserve: 64, reloading: false, reloadTime: 0,
        crouching: false, aiming: false, moving: false, sprinting: false,
        shotTime: -10, lastDamage: -10, distance: 0 },
      obstacles: clone(WORLD.obstacles),
      allies: [-3, -1, 1, 3].map((x, i) => ({
        id: 'ally-' + (i + 1), team: 'allied', x, z: 17 + i * 1.25,
        y: 0, yaw: 0, alive: true, state: 'waiting', waypoint: 0,
        wait: i * 0.5, speed: 2.05 + i * 0.07
      })),
      enemies: [
        { id: 'defender-1', x: -11, z: -43, fireTimer: 2.5 },
        { id: 'defender-2', x: 11, z: -66, fireTimer: 3.5 }
      ].map(e => ({ ...e, y: heightAt(e.x, e.z), yaw: Math.PI,
        team: 'defender', alive: true, health: 100, state: 'watching' })),
      objective: { ...WORLD.objective, complete: false }, effects: [], events: []
    };
  }
  function reset(game) {
    const fresh = createGame();
    for (const key of Object.keys(game)) delete game[key];
    Object.assign(game, fresh);
    return game;
  }
  function start(game) {
    if (game.phase !== 'ready') return false;
    game.phase = 'playing';
    event(game, 'start', 'Cross the beach. Defeat both defenders and reach the bunker marker.');
    return true;
  }
  function setPaused(game, paused) {
    if (paused && game.phase === 'playing') game.phase = 'paused';
    else if (!paused && game.phase === 'paused') game.phase = 'playing';
    return game.phase;
  }
  function event(game, type, message, extra = {}) {
    const item = { id: ++game.sequence, type, time: game.time, message, ...extra };
    game.events.push(item);
    if (game.events.length > 24) game.events.shift();
    return item;
  }
  function effect(game, type, point, life, extra = {}) {
    const item = { id: ++game.sequence, type, ...point, life, ...extra };
    game.effects.push(item);
    if (game.effects.length > 80) game.effects.shift();
    return item;
  }
  function eye(player) {
    return { x: player.x, y: player.y + (player.crouching ? 1.08 : 1.68), z: player.z };
  }
  function lookDirection(yaw, pitch) {
    return { x: -Math.sin(yaw) * Math.cos(pitch), y: Math.sin(pitch),
      z: -Math.cos(yaw) * Math.cos(pitch) };
  }

  // Circle against rectangle keeps the player's shoulders outside cover.
  function canOccupy(game, x, z, radius = PLAYER_RADIUS) {
    const b = WORLD.bounds;
    if (!Number.isFinite(x) || !Number.isFinite(z) || x - radius < b.minX ||
        x + radius > b.maxX || z - radius < b.minZ || z + radius > b.maxZ) return false;
    for (const o of game.obstacles) {
      if (!o.active) continue;
      const dx = x - clamp(x, o.x - o.width / 2, o.x + o.width / 2);
      const dz = z - clamp(z, o.z - o.depth / 2, o.z + o.depth / 2);
      if (dx * dx + dz * dz < radius * radius) return false;
    }
    return true;
  }
  function move(game, actor, dx, dz, radius = PLAYER_RADIUS) {
    // Substeps prevent sprinting or a slow frame from skipping thin cover.
    const steps = Math.max(1, Math.ceil(Math.hypot(dx, dz) / 0.15));
    const sx = dx / steps, sz = dz / steps;
    let travelled = 0;
    for (let i = 0; i < steps; i++) {
      const ox = actor.x, oz = actor.z;
      if (canOccupy(game, actor.x + sx, actor.z + sz, radius)) {
        actor.x += sx; actor.z += sz;
      } else {
        // Preserve movement along a wall instead of sticking to it.
        if (canOccupy(game, actor.x + sx, actor.z, radius)) actor.x += sx;
        if (canOccupy(game, actor.x, actor.z + sz, radius)) actor.z += sz;
      }
      travelled += Math.hypot(actor.x - ox, actor.z - oz);
    }
    actor.y = heightAt(actor.x, actor.z);
    return travelled;
  }
  function rayBox(origin, dir, box, maximum) {
    let near = 0, far = maximum;
    for (const axis of ['x', 'y', 'z']) {
      if (Math.abs(dir[axis]) < 1e-9) {
        if (origin[axis] < box.min[axis] || origin[axis] > box.max[axis]) return null;
      } else {
        let a = (box.min[axis] - origin[axis]) / dir[axis];
        let b = (box.max[axis] - origin[axis]) / dir[axis];
        if (a > b) [a, b] = [b, a];
        near = Math.max(near, a); far = Math.min(far, b);
        if (near > far) return null;
      }
    }
    return near >= 0 && near <= maximum ? near : null;
  }
  function obstacleBox(o) {
    return { min: { x: o.x - o.width / 2, y: o.y, z: o.z - o.depth / 2 },
      max: { x: o.x + o.width / 2, y: o.y + o.height, z: o.z + o.depth / 2 } };
  }
  function pointOnRay(origin, dir, t) {
    return { x: origin.x + dir.x * t, y: origin.y + dir.y * t, z: origin.z + dir.z * t };
  }
  function terrainHit(origin, dir, maximum) {
    let previous = 0;
    for (let t = 0.25; t <= maximum + 0.25; t += 0.25) {
      const end = Math.min(t, maximum), p = pointOnRay(origin, dir, end);
      if (p.y <= heightAt(p.x, p.z)) {
        let lo = previous, hi = end;
        for (let n = 0; n < 10; n++) {
          const mid = (lo + hi) / 2, at = pointOnRay(origin, dir, mid);
          if (at.y <= heightAt(at.x, at.z)) hi = mid; else lo = mid;
        }
        return hi;
      }
      previous = end;
    }
    return null;
  }
  function raycast(game, origin, direction, maximum = 140, includeEnemies = true) {
    const length = Math.hypot(direction.x, direction.y, direction.z);
    if (!length || !Number.isFinite(length)) return { kind: 'miss', point: { ...origin }, distance: 0 };
    const dir = { x: direction.x / length, y: direction.y / length, z: direction.z / length };
    let nearest = maximum, result = { kind: 'miss' };
    for (const o of game.obstacles) {
      if (!o.active) continue;
      const t = rayBox(origin, dir, obstacleBox(o), nearest);
      if (t !== null && t < nearest) { nearest = t; result = { kind: 'cover', obstacleId: o.id }; }
    }
    const ground = terrainHit(origin, dir, nearest);
    if (ground !== null && ground < nearest) { nearest = ground; result = { kind: 'cover', terrain: true }; }
    if (includeEnemies) for (const enemy of game.enemies) {
      if (!enemy.alive) continue;
      const t = rayBox(origin, dir, {
        min: { x: enemy.x - 0.43, y: enemy.y + 0.1, z: enemy.z - 0.43 },
        max: { x: enemy.x + 0.43, y: enemy.y + 1.78, z: enemy.z + 0.43 }
      }, nearest);
      if (t !== null && t < nearest) { nearest = t; result = { kind: 'enemy', enemyId: enemy.id }; }
    }
    return { ...result, point: pointOnRay(origin, dir, nearest), distance: nearest };
  }
  function lineOfSight(game, from, to) {
    const dir = { x: to.x - from.x, y: to.y - from.y, z: to.z - from.z };
    const length = Math.hypot(dir.x, dir.y, dir.z);
    if (length < 1e-6) return true;
    return raycast(game, from, dir, length - 0.01, false).kind === 'miss';
  }
  function reload(game) {
    const p = game.player;
    if (game.phase !== 'playing' || p.reloading || p.ammo >= MAGAZINE || p.reserve <= 0) return false;
    p.reloading = true; p.reloadTime = RELOAD_SECONDS;
    event(game, 'reload', 'Reloading…');
    return true;
  }
  function fire(game) {
    const p = game.player;
    if (game.phase !== 'playing') return { kind: 'blocked', reason: 'phase' };
    if (p.reloading) return { kind: 'blocked', reason: 'reload' };
    if (game.time - p.shotTime < 0.25) return { kind: 'blocked', reason: 'cooldown' };
    if (p.ammo <= 0) { event(game, 'empty', 'Magazine empty. Press R to reload.'); return { kind: 'empty' }; }
    p.ammo--; p.shotTime = game.time;
    const origin = eye(p), result = raycast(game, origin, lookDirection(p.yaw, p.pitch));
    effect(game, 'shot', origin, 0.08, { from: origin, to: result.point, friendly: true });
    if (result.kind === 'enemy') {
      const enemy = game.enemies.find(e => e.id === result.enemyId);
      enemy.health = Math.max(0, enemy.health - 50);
      effect(game, 'enemyHit', result.point, 0.22, { enemyId: enemy.id });
      if (enemy.health === 0) {
        enemy.alive = false; enemy.state = 'defeated'; game.defeated++;
        event(game, 'defeated', 'Defender cleared (' + game.defeated + '/2).', { enemyId: enemy.id });
      } else event(game, 'hit', 'Hit confirmed.', { enemyId: enemy.id });
    } else if (result.kind === 'cover') {
      effect(game, 'impact', result.point, 0.35);
      const cover = game.obstacles.find(o => o.id === result.obstacleId);
      if (cover && cover.destructible) {
        cover.health = Math.max(0, cover.health - 50);
        if (cover.health === 0) {
          cover.active = false;
          effect(game, 'debris', { x: cover.x, y: cover.y + 0.3, z: cover.z }, 1.5, { obstacleId: cover.id });
          event(game, 'coverDestroyed', 'Wooden cover broken. The gap is now open.', { obstacleId: cover.id });
          result.destroyed = true;
        } else event(game, 'coverHit', 'Wooden cover damaged.');
      }
    }
    return result;
  }
  function updateAllies(game, dt) {
    for (const ally of game.allies) {
      if (ally.wait > 0) { ally.wait -= dt; ally.state = 'covering'; continue; }
      if (ally.waypoint >= WORLD.route.length) { ally.state = 'covering'; continue; }
      const target = WORLD.route[ally.waypoint];
      const dx = target.x - ally.x, dz = target.z - ally.z, length = Math.hypot(dx, dz);
      if (length < 0.25) {
        ally.waypoint++;
        // Short authored pauses communicate cover-to-cover movement.
        ally.wait = ally.waypoint % 3 === 0 ? 1.3 : 0.2;
        ally.state = 'covering';
        continue;
      }
      ally.yaw = Math.atan2(-dx, -dz);
      const amount = Math.min(length, ally.speed * dt);
      const moved = move(game, ally, dx / length * amount, dz / length * amount, 0.3);
      ally.state = moved > 0.0001 ? 'advancing' : 'covering';
    }
  }
  function updateEnemies(game, dt) {
    const p = game.player;
    for (const e of game.enemies) {
      if (!e.alive) continue;
      e.yaw = Math.atan2(e.x - p.x, e.z - p.z);
      e.fireTimer = Math.max(0, e.fireTimer - dt);
      const from = { x: e.x, y: e.y + 1.52, z: e.z };
      const visible = distance(e, p) < 49 && lineOfSight(game, from, eye(p));
      e.state = visible ? 'aiming' : 'watching';
      if (!visible || e.fireTimer > 0) continue;
      e.fireTimer = e.id === 'defender-1' ? 2.4 : 2.9;
      e.state = 'firing';
      effect(game, 'shot', from, 0.15, { from, to: eye(p), friendly: false });
      p.health = Math.max(0, p.health - (p.sprinting ? 4 : 6));
      p.lastDamage = game.time;
      event(game, 'damage', 'Incoming fire. Use cover.', { amount: p.sprinting ? 4 : 6 });
      if (p.health <= 0) {
        game.phase = 'dead'; p.moving = false;
        event(game, 'dead', 'Advance stopped. Restart to try another route.');
        return;
      }
    }
  }
  function update(game, elapsed, input = {}) {
    if (input.start) start(game);
    if (game.phase !== 'playing') return game;
    // Tab suspension never advances minutes of combat in one browser frame.
    const dt = clamp(finite(elapsed), 0, 0.1);
    if (dt === 0) return game;
    game.time += dt;
    const p = game.player;
    p.yaw = finite(input.yaw, p.yaw);
    p.pitch = clamp(finite(input.pitch, p.pitch), -1.32, 1.32);
    p.crouching = !!input.crouch; p.aiming = !!input.aim;
    let forward = clamp(finite(input.forward), -1, 1);
    let strafe = clamp(finite(input.strafe), -1, 1);
    const magnitude = Math.hypot(forward, strafe);
    if (magnitude > 1) { forward /= magnitude; strafe /= magnitude; }
    p.sprinting = !!input.sprint && !p.crouching && !p.aiming && forward > 0;
    const speed = p.crouching ? 2.0 : p.aiming ? 2.4 : p.sprinting ? 7.0 : 4.3;
    const dx = (-Math.sin(p.yaw) * forward + Math.cos(p.yaw) * strafe) * speed * dt;
    const dz = (-Math.cos(p.yaw) * forward - Math.sin(p.yaw) * strafe) * speed * dt;
    const moved = move(game, p, dx, dz);
    p.distance += moved; p.moving = moved > 0.0001;
    if (p.reloading) {
      p.reloadTime = Math.max(0, p.reloadTime - dt);
      if (p.reloadTime <= 1e-8) {
        const transfer = Math.min(MAGAZINE - p.ammo, p.reserve);
        p.ammo += transfer; p.reserve -= transfer;
        p.reloading = false; p.reloadTime = 0;
        event(game, 'reloaded', 'Rifle ready.');
      }
    }
    for (const fx of game.effects) fx.life -= dt;
    game.effects = game.effects.filter(fx => fx.life > 0);
    updateAllies(game, dt);
    updateEnemies(game, dt);
    if (game.phase !== 'playing') return game;
    if (game.time - p.lastDamage > 6) p.health = Math.min(100, p.health + dt * 5);
    const inObjective = distance(p, game.objective) <= game.objective.radius;
    game.objective.complete = inObjective && game.enemies.every(e => !e.alive);
    if (game.objective.complete) {
      game.phase = 'won'; p.moving = false;
      event(game, 'won', 'Bunker approach secured. Demo complete.');
    }
    return game;
  }
  return { WORLD, PLAYER_RADIUS, MAGAZINE, RELOAD_SECONDS, createGame, start,
    reset, setPaused, update, fire, reload, heightAt, canOccupy, lineOfSight,
    raycast, eye, lookDirection };
});
