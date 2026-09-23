(function () {
  'use strict';
  const $ = (id) => document.getElementById(id);
  const canvas = $('gameCanvas');
  const keys = new Set();
  const touch = new Set();
  const pad = (v) => String(Math.max(0, Math.round(v))).padStart(2, '0');
  const clamp = (x, a, b) => Math.min(b, Math.max(a, x));
  let game, view, previousPhase, lastTime, wasLocked = false, drag = null;
  let aimed = false, crouched = false, heldFire = false, messageUntil = 0, hitUntil = 0;
  let lastEventId = -1, lastHealth = 100, damageOpacity = 0, smoothedFps = 60, lastHud = 0;
  let audioContext = null;

  function sound(type) {
    if (!$('sound').checked || !audioContext) return;
    if (audioContext.state === 'suspended') audioContext.resume().catch(() => {});
    const at = audioContext.currentTime;
    const gain = audioContext.createGain();
    gain.connect(audioContext.destination);
    if (type === 'shot') {
      const length = Math.floor(audioContext.sampleRate * 0.12);
      const buffer = audioContext.createBuffer(1, length, audioContext.sampleRate);
      const samples = buffer.getChannelData(0);
      for (let i = 0; i < length; i++) samples[i] = (Math.random() * 2 - 1) * Math.exp(-i / (length * 0.18));
      const source = audioContext.createBufferSource(); source.buffer = buffer;
      const filter = audioContext.createBiquadFilter(); filter.type = 'lowpass'; filter.frequency.value = 1600;
      source.connect(filter); filter.connect(gain); gain.gain.setValueAtTime(0.22, at); source.start(at); source.onended = () => { source.disconnect(); filter.disconnect(); gain.disconnect(); };
    } else {
      const oscillator = audioContext.createOscillator(); oscillator.type = 'triangle';
      oscillator.frequency.setValueAtTime(type === 'hit' ? 650 : type === 'reload' ? 190 : 105, at);
      oscillator.frequency.exponentialRampToValueAtTime(type === 'hit' ? 950 : 65, at + 0.09);
      gain.gain.setValueAtTime(0.055, at); gain.gain.exponentialRampToValueAtTime(0.001, at + 0.12);
      oscillator.connect(gain); oscillator.start(at); oscillator.stop(at + 0.13); oscillator.onended = () => { oscillator.disconnect(); gain.disconnect(); };
    }
  }
  function initSound() {
    if (audioContext || !$('sound').checked) return;
    const Audio = window.AudioContext || window.webkitAudioContext;
    if (Audio) { try { audioContext = new Audio(); } catch (_) {} }
  }
  function announce(text, seconds = 2.4) {
    $('message').textContent = text;
    messageUntil = performance.now() + seconds * 1000;
  }
  function clearInput() { keys.clear(); touch.clear(); heldFire = false; drag = null; }
  function releaseMouse() {
    if (document.pointerLockElement === canvas && document.exitPointerLock) document.exitPointerLock();
  }
  function captureMouse() {
    canvas.focus({ preventScroll: true });
    if (!matchMedia('(pointer:fine)').matches || !canvas.requestPointerLock) return;
    try {
      const request = canvas.requestPointerLock();
      if (request && request.catch) request.catch(() => { announce('Drag the scene or use the arrow keys to look.', 4); });
    } catch (_) { announce('Drag the scene or use the arrow keys to look.', 4); }
  }
  function showPhase() {
    if (!game || previousPhase === game.phase) return;
    previousPhase = game.phase;
    document.body.dataset.phase = game.phase;
    const playing = game.phase === 'playing';
    $('briefing').hidden = playing;
    $('hud').hidden = !playing;
    $('footer').hidden = playing;
    if (!playing) { clearInput(); releaseMouse(); }
    $('restartBrief').hidden = game.phase === 'ready';
    if (game.phase === 'ready') {
      $('briefEyebrow').textContent = 'CS549 / PLAYABLE CONCEPT';
      $('briefTitle').innerHTML = 'Make it off<br>the beach.';
      $('briefText').textContent = 'Leave the surf. Move with your squad. Find cover among the wrecks and make your way to the bunker.';
      $('startButton').innerHTML = 'Begin landing <span aria-hidden="true">↗</span>';
      $('startNote').textContent = 'A short, stylized browser FPS. Desktop, keyboard & mouse recommended.';
    } else if (game.phase === 'paused') {
      $('briefEyebrow').textContent = 'MISSION PAUSED';
      $('briefTitle').innerHTML = 'Take a<br>breath.';
      $('briefText').textContent = 'Your position is saved for this session. Resume when you are ready to continue toward the bunker.';
      $('startButton').innerHTML = 'Resume mission <span aria-hidden="true">↗</span>';
      $('startNote').textContent = 'Click Resume to capture the mouse again. Escape pauses the mission.';
    } else if (game.phase === 'dead') {
      $('briefEyebrow').textContent = 'MISSION ENDED';
      $('briefTitle').innerHTML = 'Find another<br>way through.';
      $('briefText').textContent = 'Use the solid wrecks and sandbags to break the defenders’ line of sight. Reload behind cover and let your health recover.';
      $('startButton').innerHTML = 'Try again <span aria-hidden="true">↗</span>';
      $('startNote').textContent = 'Restart the same scene with full health and ammunition.';
    } else if (game.phase === 'won') {
      $('briefEyebrow').textContent = 'OBJECTIVE COMPLETE';
      $('briefTitle').innerHTML = 'Beachhead<br>secured.';
      const elapsed = Math.round(game.time);
      $('briefText').textContent = 'Both defenders cleared. You reached the bunker in ' + Math.floor(elapsed / 60) + ':' + pad(elapsed % 60) + '. The route is open for your squad.';
      $('startButton').innerHTML = 'Play again <span aria-hidden="true">↗</span>';
      $('startNote').textContent = 'Try a different route or compare wet sand, haze, and shadows in Scene settings.';
    }
  }
  function begin() {
    if (!game) return;
    if (game.phase === 'dead' || game.phase === 'won') reset();
    if (game.phase === 'ready') NormandyEngine.update(game, 0, { start: true });
    else NormandyEngine.setPaused(game, false);
    $('settings').hidden = true; $('settingsButton').setAttribute('aria-expanded', 'false');
    clearInput(); initSound(); showPhase(); captureMouse();
    announce('Move between cover. Clear the defenders, then reach the bunker.', 4);
  }
  function pause() {
    if (game && game.phase === 'playing') { NormandyEngine.setPaused(game, true); showPhase(); }
  }
  function reset() {
    NormandyEngine.reset(game);
    aimed = false; crouched = false; lastEventId = -1; lastHealth = 100; damageOpacity = 0;
    messageUntil = hitUntil = 0; clearInput(); previousPhase = null; showPhase(); updateHud(performance.now());
  }
  function shoot() {
    if (!game || game.phase !== 'playing') return;
    const result = NormandyEngine.fire(game);
    if (result.kind === 'enemy') { sound('shot'); sound('hit'); hitUntil = performance.now() + 160; }
    else if (result.kind === 'cover' || result.kind === 'miss') sound('shot');
    else if (result.kind === 'empty') { sound('empty'); announce('Clip empty — press R to reload.'); }
  }
  function reload() {
    if (!game || game.phase !== 'playing') return;
    NormandyEngine.reload(game);
  }
  function eventFeedback() {
    for (const event of game.events) {
      if (event.id <= lastEventId) continue;
      if (event.type === 'coverDestroyed') announce('Wooden cover destroyed — the opening is clear.');
      if (event.type === 'defeated') announce(game.defeated >= 2 ? 'Defenders cleared. Reach the bunker marker.' : 'One defender remains.');
      if (event.type === 'reload') sound('reload');
      if (event.type === 'reloaded') sound('reload');
      lastEventId = Math.max(lastEventId, event.id);
    }
  }
  function updateHud(now) {
    const p = game.player;
    const distance = Math.hypot(p.x - game.objective.x, p.z - game.objective.z);
    const remaining = game.enemies.filter((e) => e.alive).length;
    $('distance').textContent = Math.round(distance);
    $('defenders').textContent = remaining;
    $('objectiveStage').textContent = p.z < -55 ? 'BUNKER APPROACH' : 'BEACH ADVANCE';
    $('objectiveText').textContent = remaining === 0 ? 'Reach the bunker marker' : 'Advance and clear the defenders';
    $('progress').style.width = clamp((1 - distance / 101) * 100, 0, 100) + '%';
    $('health').textContent = Math.ceil(p.health);
    $('healthBar').setAttribute('aria-valuenow', String(Math.ceil(p.health)));
    $('healthFill').style.width = clamp(p.health, 0, 100) + '%';
    $('healthFill').style.background = p.health < 30 ? '#e29b7a' : '#d3dcb3';
    $('stance').textContent = p.crouching ? 'CROUCHED' : p.sprinting && p.moving ? 'SPRINTING' : p.aiming ? 'AIMING' : 'STANDING';
    $('ammo').textContent = pad(p.ammo); $('reserve').textContent = p.reserve;
    $('weaponState').textContent = p.reloading ? 'RELOADING' : p.ammo ? (p.aiming ? 'AIMING' : 'READY') : 'PRESS R TO RELOAD';
    $('reloadFill').style.width = p.reloading ? clamp((1 - p.reloadTime / 2) * 100, 0, 100) + '%' : '0%';
    $('crosshair').classList.toggle('aim', !!p.aiming);
    $('fps').textContent = Math.round(smoothedFps) + ' fps';
    $('message').classList.toggle('visible', now < messageUntil);
  }
  function visuals() {
    const wetness = Number($('wetness').value) / 100;
    $('wetnessValue').textContent = Math.round(wetness * 100) + '%';
    if (view) view.setVisuals({ wetness, fog: $('fog').checked, shadows: $('shadows').checked });
  }
  function setSettings(open) {
    if (open) pause();
    $('settings').hidden = !open;
    $('settingsButton').setAttribute('aria-expanded', String(open));
    if (open) $('closeSettings').focus();
    else $('settingsButton').focus();
  }
  $('startButton').addEventListener('click', begin);
  $('restartBrief').addEventListener('click', () => { reset(); begin(); });
  $('pauseButton').addEventListener('click', pause);
  $('home').addEventListener('click', (e) => { e.preventDefault(); pause(); });
  $('settingsButton').addEventListener('click', () => setSettings($('settings').hidden));
  $('closeSettings').addEventListener('click', () => setSettings(false));
  for (const id of ['wetness', 'fog', 'shadows']) $(id).addEventListener('input', visuals);
  $('sound').addEventListener('change', initSound);

  window.addEventListener('keydown', (e) => {
    const editable = /INPUT|SELECT|TEXTAREA|BUTTON/.test(document.activeElement.tagName);
    if (e.code === 'Escape') { if (!$('settings').hidden) setSettings(false); pause(); return; }
    if (!game || game.phase !== 'playing' || (editable && document.activeElement !== canvas)) return;
    if (['KeyW','KeyA','KeyS','KeyD','Space','ArrowLeft','ArrowRight','ArrowUp','ArrowDown','ShiftLeft','ShiftRight','KeyC','KeyR','KeyF'].includes(e.code)) e.preventDefault();
    keys.add(e.code);
    if (e.repeat) return;
    if (e.code === 'KeyR') reload();
    if (e.code === 'KeyC') crouched = !crouched;
    if (e.code === 'KeyF') aimed = !aimed;
    if (e.code === 'Space') shoot();
  });
  window.addEventListener('keyup', (e) => keys.delete(e.code));
  window.addEventListener('blur', () => { clearInput(); pause(); });
  document.addEventListener('visibilitychange', () => { if (document.hidden) pause(); });
  document.addEventListener('pointerlockchange', () => {
    const locked = document.pointerLockElement === canvas;
    if (wasLocked && !locked) pause();
    wasLocked = locked;
  });
  document.addEventListener('pointerlockerror', () => announce('Drag the scene or use the arrow keys to look.', 4));
  function look(dx, dy) {
    if (!game || game.phase !== 'playing') return;
    game.player.yaw -= dx * 0.0021;
    game.player.pitch = clamp(game.player.pitch - dy * 0.0021, -1.24, 1.24);
  }
  document.addEventListener('mousemove', (e) => { if (document.pointerLockElement === canvas) look(e.movementX, e.movementY); });
  canvas.addEventListener('contextmenu', (e) => e.preventDefault());
  canvas.addEventListener('pointerdown', (e) => {
    if (!game || game.phase !== 'playing') return;
    canvas.focus({ preventScroll: true });
    e.preventDefault();
    if (e.button === 2) { aimed = true; return; }
    if (document.pointerLockElement === canvas && e.pointerType === 'mouse') { shoot(); return; }
    drag = { id: e.pointerId, x: e.clientX, y: e.clientY, distance: 0, time: performance.now(), type: e.pointerType };
    try { canvas.setPointerCapture(e.pointerId); } catch (_) {}
  });
  canvas.addEventListener('pointermove', (e) => {
    if (!drag || drag.id !== e.pointerId || document.pointerLockElement === canvas) return;
    const dx = e.clientX - drag.x, dy = e.clientY - drag.y;
    drag.distance += Math.hypot(dx, dy); look(dx, dy); drag.x = e.clientX; drag.y = e.clientY;
  });
  canvas.addEventListener('pointerup', (e) => {
    if (e.button === 2) aimed = false;
    if (drag && e.pointerId === drag.id) {
      if (drag.distance < 8 && performance.now() - drag.time < 400) shoot();
      drag = null;
    }
  });
  canvas.addEventListener('pointercancel', () => { drag = null; });
  window.addEventListener('pointerup', (e) => { if (e.button === 2) aimed = false; });
  for (const button of document.querySelectorAll('[data-move]')) {
    button.addEventListener('pointerdown', (e) => { e.preventDefault(); touch.add(button.dataset.move); button.setPointerCapture(e.pointerId); });
    const stop = () => touch.delete(button.dataset.move);
    button.addEventListener('pointerup', stop); button.addEventListener('pointercancel', stop); button.addEventListener('lostpointercapture', stop);
  }
  $('touchFire').addEventListener('pointerdown', (e) => { e.preventDefault(); heldFire = true; $('touchFire').setPointerCapture(e.pointerId); shoot(); });
  for (const event of ['pointerup','pointercancel','lostpointercapture']) $('touchFire').addEventListener(event, () => { heldFire = false; });
  $('touchAim').addEventListener('click', () => { aimed = !aimed; });
  $('touchReload').addEventListener('click', reload);

  function frame(now) {
    const frameSeconds = lastTime ? Math.max(0, (now - lastTime) / 1000) : 0;
    const dt = Math.min(frameSeconds, 0.05);
    lastTime = now;
    if (frameSeconds > 0) smoothedFps += (1 / frameSeconds - smoothedFps) * 0.04;
    if (game.phase === 'playing') {
      game.player.yaw += ((keys.has('ArrowLeft') ? 1 : 0) - (keys.has('ArrowRight') ? 1 : 0)) * dt * 1.55;
      game.player.pitch = clamp(game.player.pitch + ((keys.has('ArrowUp') ? 1 : 0) - (keys.has('ArrowDown') ? 1 : 0)) * dt * 1.1, -1.24, 1.24);
      NormandyEngine.update(game, dt, {
        forward: (keys.has('KeyW') || touch.has('forward') ? 1 : 0) - (keys.has('KeyS') || touch.has('back') ? 1 : 0),
        strafe: (keys.has('KeyD') || touch.has('right') ? 1 : 0) - (keys.has('KeyA') || touch.has('left') ? 1 : 0),
        sprint: keys.has('ShiftLeft') || keys.has('ShiftRight'), crouch: crouched, aim: aimed,
        yaw: game.player.yaw, pitch: game.player.pitch
      });
      if (heldFire && game.player.ammo > 0) shoot();
      if (game.player.health < lastHealth) { damageOpacity = 0.65; sound('damage'); }
      lastHealth = game.player.health;
      eventFeedback();
    }
    damageOpacity = Math.max(0, damageOpacity - dt * 1.9);
    $('damageWash').style.opacity = String(damageOpacity);
    $('hitMarker').classList.toggle('visible', now < hitUntil);
    showPhase();
    if (now - lastHud > 75) { updateHud(now); lastHud = now; }
    view.render(game, dt, { aim: aimed });
    requestAnimationFrame(frame);
  }
  try {
    if (!window.THREE || !window.NormandyEngine || !window.NormandyScene) throw new Error('One of the local game files is missing. Keep this folder and its vendor folder together.');
    game = NormandyEngine.createGame();
    view = NormandyScene.create({ canvas, game });
    visuals(); showPhase(); updateHud(performance.now());
    $('startButton').disabled = false;
    window.addEventListener('resize', () => view.resize());
    // Read-only diagnostics for local verification; gameplay still uses normal controls.
    window.NormandyDemo = { getState: () => JSON.parse(JSON.stringify(game)), version: 'fps-concept-1' };
    requestAnimationFrame(frame);
  } catch (error) {
    $('error').hidden = false; $('briefing').hidden = true;
    $('errorText').textContent = 'Open this demo in a desktop browser with WebGL 2 enabled. ' + error.message;
    console.error('Normandy initialization:', error);
  }
})();
