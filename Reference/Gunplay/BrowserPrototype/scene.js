/* Procedural Normandy scene. All geometry and textures are generated locally. */
(function (root) {
  'use strict';

  function create(options) {
    const T = root.THREE;
    if (!T) throw new Error('The local Three.js renderer could not be loaded.');
    const canvas = options.canvas;
    const initialGame = options.game;
    const terrainHeight = root.NormandyEngine.heightAt;
    const renderer = new T.WebGLRenderer({ canvas, antialias: true, alpha: false, powerPreference: 'high-performance' });
    renderer.setPixelRatio(Math.min(root.devicePixelRatio || 1, 1.5));
    renderer.outputColorSpace = T.SRGBColorSpace;
    renderer.toneMapping = T.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.05;
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = T.PCFSoftShadowMap;
    const scene = new T.Scene();
    const hazeColor = new T.Color('#9baeb5');
    const atmosphere = new T.Fog(hazeColor, 85, 245);
    scene.background = hazeColor;
    scene.fog = atmosphere;
    const camera = new T.PerspectiveCamera(72, 1, 0.07, 650);
    camera.rotation.order = 'YXZ';
    scene.add(camera);
    const resources = new Set();
    const materials = new Set();
    const trackedTextures = new Set();
    const objects = new Map();
    const soldiers = new Map();
    const smoke = [];
    const activeEffects = new Map();
    let elapsed = 0;
    let previousTime = -1;
    let disposed = false;
    const settings = { wetness: 0.72, fog: true, shadows: true, route: false };
    let seed = 549;
    function random() { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 4294967296; }
    function geo(g) { resources.add(g); return g; }
    function material(color, more) {
      const m = new T.MeshStandardMaterial(Object.assign({ color, roughness: 0.88, metalness: 0.03 }, more || {}));
      materials.add(m);
      return m;
    }
    function basic(color, more) {
      const m = new T.MeshBasicMaterial(Object.assign({ color }, more || {}));
      materials.add(m);
      return m;
    }
    const boxGeo = geo(new T.BoxGeometry(1, 1, 1));
    const sphereGeo = geo(new T.SphereGeometry(1, 10, 7));
    const cylinderGeo = geo(new T.CylinderGeometry(1, 1, 1, 10));
    const bagGeo = geo(new T.SphereGeometry(1, 9, 6));
    function mesh(parent, geometry, mat, x, y, z, sx, sy, sz, cast) {
      const m = new T.Mesh(geometry, mat);
      m.position.set(x || 0, y || 0, z || 0);
      m.scale.set(sx === undefined ? 1 : sx, sy === undefined ? 1 : sy, sz === undefined ? 1 : sz);
      m.castShadow = cast !== false;
      m.receiveShadow = true;
      parent.add(m);
      return m;
    }
    function box(parent, mat, x, y, z, w, h, d, cast) { return mesh(parent, boxGeo, mat, x, y, z, w, h, d, cast); }
    function beam(parent, mat, a, b, width, depth) {
      const av = new T.Vector3(...a), bv = new T.Vector3(...b);
      const mid = av.clone().add(bv).multiplyScalar(0.5);
      const m = box(parent, mat, mid.x, mid.y, mid.z, width, av.distanceTo(bv), depth || width);
      m.quaternion.setFromUnitVectors(new T.Vector3(0, 1, 0), bv.sub(av).normalize());
      return m;
    }
    function compactStatic(group) {
      group.updateMatrixWorld(true);
      const inverse = group.matrixWorld.clone().invert(), batches = new Map();
      group.traverse(o => {
        if (!o.isMesh || o.isInstancedMesh) return;
        const key = o.geometry.uuid + ':' + o.material.uuid + ':' + o.castShadow;
        if (!batches.has(key)) batches.set(key, []);
        batches.get(key).push(o);
      });
      for (const list of batches.values()) {
        if (list.length < 3) continue;
        const batch = new T.InstancedMesh(list[0].geometry, list[0].material, list.length);
        batch.castShadow = list[0].castShadow; batch.receiveShadow = list[0].receiveShadow;
        for (let i = 0; i < list.length; i++) {
          batch.setMatrixAt(i, inverse.clone().multiply(list[i].matrixWorld));
          list[i].parent.remove(list[i]);
        }
        batch.computeBoundingSphere(); group.add(batch);
      }
    }
    function textureCanvas(size, paint, repeats) {
      const c = document.createElement('canvas'); c.width = size; c.height = size;
      paint(c.getContext('2d'), size);
      const texture = new T.CanvasTexture(c);
      texture.colorSpace = T.SRGBColorSpace;
      texture.wrapS = texture.wrapT = T.RepeatWrapping;
      texture.repeat.set(repeats || 1, repeats || 1);
      texture.anisotropy = Math.min(4, renderer.capabilities.getMaxAnisotropy());
      trackedTextures.add(texture);
      return texture;
    }
    const sandTexture = textureCanvas(512, (ctx, n) => {
      ctx.fillStyle = '#a1987f'; ctx.fillRect(0, 0, n, n);
      for (let i = 0; i < 19000; i++) {
        const v = Math.floor(82 + random() * 93), alpha = 0.1 + random() * 0.2;
        ctx.fillStyle = 'rgba(' + v + ',' + (v - 5) + ',' + (v - 20) + ',' + alpha + ')';
        ctx.fillRect(random() * n, random() * n, 1 + random() * 4, 1 + random() * 2);
      }
      for (let i = 0; i < 30; i++) {
        const x = random() * n, y = random() * n, radius = 12 + random() * 65;
        const g = ctx.createRadialGradient(x, y, 0, x, y, radius);
        g.addColorStop(0, 'rgba(54,49,38,0.07)'); g.addColorStop(1, 'rgba(54,49,38,0)');
        ctx.fillStyle = g; ctx.fillRect(x - radius, y - radius, radius * 2, radius * 2);
      }
    }, 19);
    const concreteTexture = textureCanvas(256, (ctx, n) => {
      ctx.fillStyle = '#8b8c7d'; ctx.fillRect(0, 0, n, n);
      for (let i = 0; i < 14000; i++) {
        ctx.fillStyle = random() > 0.5 ? 'rgba(24,28,25,.1)' : 'rgba(205,208,179,.1)';
        ctx.fillRect(random() * n, random() * n, 1 + random() * 3, 1 + random() * 3);
      }
      for (let i = 0; i < 20; i++) {
        ctx.fillStyle = 'rgba(27,35,24,.11)'; ctx.fillRect(random() * n, 0, random() * 7 + 1, random() * n);
      }
      ctx.strokeStyle = 'rgba(33,36,31,.22)'; ctx.lineWidth = 1;
      for (let i = 0; i < 5; i++) { ctx.beginPath(); const x = random() * n; ctx.moveTo(x, 0); ctx.lineTo(x - 20, 70); ctx.lineTo(x + 12, 110); ctx.stroke(); }
    }, 2);
    const sandMat = material('#d1c4a4', { map: sandTexture, roughness: 0.53, metalness: 0.12 });
    const grassMat = material('#62674a');
    const grassDark = material('#48503b');
    const concrete = material('#a2a293', { map: concreteTexture });
    const darkConcrete = material('#565a53', { map: concreteTexture });
    const steel = material('#3d4240', { roughness: 0.73, metalness: 0.56 });
    const rust = material('#655141', { roughness: 0.96, metalness: 0.29 });
    const wood = material('#655b43');
    const sandbagMat = material('#a59b7a');
    const olive = material('#555b42', { roughness: 0.84, metalness: 0.2 });
    const scorched = material('#343832', { roughness: 0.92, metalness: 0.18 });
    const rubber = material('#242825');
    const black = material('#202923');
    const rubbleMat = material('#777970');
    const strapMat = material('#807858');
    const skinMat = material('#b79977');
    const enemyMat = material('#656454');
    const bootMat = material('#343c33');
    const deepSeaMat = material('#637c83', { roughness: 0.33, metalness: 0.3 });
    const whiteMark = material('#c5c7b1');

    const hemi = new T.HemisphereLight('#c4dbea', '#69614e', 2.5); scene.add(hemi);
    const sun = new T.DirectionalLight('#ffdfae', 2.7);
    sun.position.set(-90, 85, -25); sun.target.position.set(0, 0, -35); scene.add(sun, sun.target);
    sun.castShadow = true;
    sun.shadow.mapSize.set(2048, 2048);
    Object.assign(sun.shadow.camera, { left: -65, right: 65, top: 85, bottom: -85, near: 1, far: 230 });
    sun.shadow.bias = -0.0003; sun.shadow.normalBias = 0.035; sun.shadow.radius = 2;
    const skyTexture = textureCanvas(256, (ctx, n) => {
      const g = ctx.createLinearGradient(0, 0, 0, n);
      g.addColorStop(0, '#7795ac'); g.addColorStop(0.4, '#a2b4bf'); g.addColorStop(0.56, '#d3cfb6'); g.addColorStop(1, '#9faeb1');
      ctx.fillStyle = g; ctx.fillRect(0, 0, n, n);
      for (let i = 0; i < 65; i++) {
        ctx.fillStyle = 'rgba(215,219,216,.1)'; ctx.beginPath();
        ctx.ellipse(random() * n, 15 + random() * 87, 20 + random() * 80, 2 + random() * 12, 0, 0, Math.PI * 2); ctx.fill();
      }
    });
    skyTexture.wrapT = T.ClampToEdgeWrapping;
    const sky = mesh(scene, geo(new T.SphereGeometry(490, 32, 18)), basic('#ffffff', { map: skyTexture, side: T.BackSide, fog: false, depthWrite: false }), 0, 0, 0, 1, 1, 1, false);
    sky.renderOrder = -10;
    const sunDisc = mesh(scene, sphereGeo, basic('#ffedc2', { fog: false }), -245, 180, -295, 8, 8, 8, false);

    const groundGeometry = geo(new T.PlaneGeometry(245, 285, 82, 95));
    groundGeometry.rotateX(-Math.PI / 2); groundGeometry.translate(0, 0, -66);
    const groundPos = groundGeometry.attributes.position;
    const groundColors = [];
    for (let i = 0; i < groundPos.count; i++) {
      const x = groundPos.getX(i), z = groundPos.getZ(i);
      const y = z > 25 ? -Math.min(3.5, (z - 25) * 0.2) : terrainHeight(x, z);
      const offset = Math.abs(x) > 33 && z < -66 ? Math.sin(x * 0.12) * Math.cos(z * 0.075) * 1.7 : 0;
      groundPos.setY(i, y + offset - 0.045);
      const green = Math.max(0, Math.min(1, (-z - 66) / 16));
      const c = new T.Color('#ffffff').lerp(new T.Color('#81876a'), green * 0.66);
      groundColors.push(c.r, c.g, c.b);
    }
    groundGeometry.setAttribute('color', new T.Float32BufferAttribute(groundColors, 3));
    groundGeometry.computeVertexNormals(); sandMat.vertexColors = true;
    mesh(scene, groundGeometry, sandMat, 0, 0, 0, 1, 1, 1, false);
    const waterGeometry = geo(new T.PlaneGeometry(750, 530, 60, 42));
    waterGeometry.rotateX(-Math.PI / 2); waterGeometry.translate(0, -0.22, 293);
    const water = mesh(scene, waterGeometry, deepSeaMat, 0, 0, 0, 1, 1, 1, false);
    water.receiveShadow = false;
    const waterPositions = waterGeometry.attributes.position;
    const foamMaterial = basic('#d5e1df', { transparent: true, opacity: 0.24, depthWrite: false });
    const surf = [];
    for (let i = 0; i < 11; i++) {
      const points = [];
      for (let x = -125; x <= 125; x += 2) points.push(new T.Vector3(x, 0.015, 28 + i * 3.5 + Math.sin(x * 0.13 + i) * 0.8));
      const curve = new T.CatmullRomCurve3(points);
      const line = mesh(scene, geo(new T.TubeGeometry(curve, 125, 0.09 + i * 0.014, 3, false)), foamMaterial, 0, 0, 0, 1, 1, 1, false);
      line.receiveShadow = false; surf.push(line);
    }
    // Pebbles and grass are merged into instanced meshes to keep rendering inexpensive.
    const pebbles = new T.InstancedMesh(geo(new T.IcosahedronGeometry(1, 0)), rubbleMat, 680);
    const dummy = new T.Object3D();
    for (let i = 0; i < 680; i++) {
      const x = (random() - 0.5) * 180, z = 24 - random() * 143;
      const size = 0.025 + random() * 0.12;
      dummy.position.set(x, terrainHeight(x, z) + size * 0.25, z);
      dummy.scale.set(size * 1.6, size * 0.5, size); dummy.rotation.set(random(), random() * Math.PI, random()); dummy.updateMatrix();
      pebbles.setMatrixAt(i, dummy.matrix);
    }
    pebbles.receiveShadow = true; scene.add(pebbles);
    const blades = [];
    for (let i = 0; i < 4300; i++) {
      const x = (random() - 0.5) * 215, z = -69 - random() * 105;
      if (Math.abs(x - 5) < 13 && z > -100 || Math.abs(x) < 11 && z > -81) continue;
      const y = terrainHeight(x, z) + (Math.abs(x) > 33 ? Math.sin(x * 0.12) * Math.cos(z * 0.075) * 1.7 : 0);
      const h = 0.2 + random() * 0.6, w = 0.06 + random() * 0.11, a = random() * Math.PI;
      const dx = Math.cos(a) * w, dz = Math.sin(a) * w;
      blades.push(x - dx, y, z - dz, x + dx, y, z + dz, x + dx * 1.6, y + h, z + dz * 1.6);
    }
    const grassGeometry = geo(new T.BufferGeometry()); grassGeometry.setAttribute('position', new T.Float32BufferAttribute(blades, 3)); grassGeometry.computeVertexNormals();
    grassMat.side = T.DoubleSide; mesh(scene, grassGeometry, grassMat, 0, 0, 0, 1, 1, 1, false);

    const scorchTexture = textureCanvas(128, (ctx, n) => {
      const gradient = ctx.createRadialGradient(n / 2, n / 2, 4, n / 2, n / 2, n / 2);
      gradient.addColorStop(0, 'rgba(28,27,22,.7)'); gradient.addColorStop(0.5, 'rgba(39,36,28,.45)'); gradient.addColorStop(1, 'rgba(40,36,29,0)');
      ctx.fillStyle = gradient; ctx.fillRect(0, 0, n, n);
    });
    const scorchMat = basic('#ffffff', { map: scorchTexture, transparent: true, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -1 });
    const flatGeo = geo(new T.PlaneGeometry(1, 1));
    function scorch(parent, x, z, w, d, y) {
      const patch = mesh(parent, flatGeo, scorchMat, x, (y || 0) + 0.005, z, w, d, 1, false); patch.rotation.x = -Math.PI / 2;
    }
    const smokeTexture = textureCanvas(128, (ctx, n) => {
      const g = ctx.createRadialGradient(n / 2, n / 2, 0, n / 2, n / 2, n / 2);
      g.addColorStop(0, 'rgba(177,179,169,.48)'); g.addColorStop(0.5, 'rgba(150,154,145,.25)'); g.addColorStop(1, 'rgba(130,135,133,0)');
      ctx.fillStyle = g; ctx.fillRect(0, 0, n, n);
    });
    function addSmoke(x, y, z, scale) {
      for (let i = 0; i < 6; i++) {
        const sm = new T.SpriteMaterial({ map: smokeTexture, transparent: true, color: '#6a6d65', opacity: 0.27, depthWrite: false }); materials.add(sm);
        const sprite = new T.Sprite(sm); scene.add(sprite);
        smoke.push({ sprite, x, y, z, scale: scale || 1, phase: i / 6 + random() * 0.08 });
      }
    }
    function bagWall(group, w, d, h) {
      const alongX = w >= d, length = Math.max(w, d), thick = Math.min(w, d);
      const layers = Math.max(1, Math.round(h / 0.3)), bags = Math.max(2, Math.ceil(length / 0.77));
      for (let layer = 0; layer < layers; layer++) for (let i = 0; i < bags; i++) {
        const at = -length / 2 + (i + 0.5) * length / bags;
        const bag = mesh(group, bagGeo, sandbagMat, alongX ? at : 0, (layer + 0.5) * h / layers, alongX ? 0 : at,
          alongX ? length / bags * 0.53 : thick * 0.52, h / layers * 0.52, alongX ? thick * 0.52 : length / bags * 0.53);
        bag.rotation.y = (random() - 0.5) * 0.11;
      }
    }
    function buildObstacle(o) {
      const g = new T.Group(); g.position.set(o.x, o.y, o.z); scene.add(g);
      const w = o.width, d = o.depth, h = o.height;
      if (o.type === 'sandbag') bagWall(g, w, d, h);
      else if (o.type === 'hedgehog') {
        const ix = Math.min(w * 0.46, 1.2), iz = Math.min(d * 0.46, 1.2), bar = Math.min(0.22, w * 0.16);
        beam(g, steel, [-ix, 0.06, -iz], [ix, h, iz], bar, bar * 1.45);
        beam(g, rust, [-ix, h, iz], [ix, 0.06, -iz], bar, bar * 1.45);
        beam(g, steel, [-ix, 0.15, iz], [ix, h * 0.78, -iz], bar, bar * 1.45);
        box(g, steel, 0, h * 0.47, 0, bar * 2, bar * 2.3, bar * 2);
        for (let i = 0; i < 3; i++) box(g, rust, 0, h * 0.42 + i * 0.09, bar, 0.06, 0.04, 0.025);
      } else if (o.type === 'gate') {
        const post = 0.13, front = -d * 0.35;
        beam(g, steel, [-w / 2 + post, 0, front], [-w / 2 + post, h, front], post);
        beam(g, steel, [w / 2 - post, 0, front], [w / 2 - post, h, front], post);
        for (let i = 0; i < 4; i++) box(g, rust, 0, (i + 0.5) * h / 4, front, w, 0.095, 0.095);
        for (let i = 1; i < 6; i++) box(g, steel, -w / 2 + i * w / 6, h / 2, front, 0.065, h, 0.065);
        beam(g, steel, [-w / 2, 0, front], [w / 2, h, front], 0.085);
        beam(g, steel, [-w / 2, h, front], [-w / 2, 0.06, d * 0.5], post);
        beam(g, steel, [w / 2, h, front], [w / 2, 0.06, d * 0.5], post);
      } else if (o.type === 'stakes' || o.type === 'stake') {
        for (const x of [-w * 0.35, w * 0.35]) {
          beam(g, wood, [x, 0, d * 0.43], [x, h, -d * 0.35], 0.18, 0.2);
          beam(g, wood, [x, 0, -d * 0.45], [x, h * 0.8, -d * 0.17], 0.14, 0.17);
          box(g, steel, x, h * 0.8, -d * 0.23, 0.25, 0.14, 0.27);
        }
        beam(g, wood, [-w / 2, h * 0.48, 0], [w / 2, h * 0.48, 0], 0.15);
      } else if (o.type === 'crate') {
        const planks = Math.ceil(w / 0.32);
        box(g, wood, 0, h / 2, 0, w, h, d);
        for (let i = 0; i < planks; i++) box(g, strapMat, -w / 2 + (i + 0.5) * w / planks, h / 2, d / 2 + 0.015, w / planks - 0.035, h - 0.12, 0.04);
        for (const x of [-w * 0.32, w * 0.32]) box(g, wood, x, h / 2, d / 2 + 0.05, 0.1, h, 0.06);
        beam(g, strapMat, [-w * 0.45, 0.1, d / 2 + 0.08], [w * 0.45, h - 0.1, d / 2 + 0.08], 0.1, 0.035);
      } else if (o.type === 'tank' || o.type === 'halftrack') {
        const isTank = o.type === 'tank';
        scorch(g, 0.3, 0, w * 1.65, d * 1.45);
        // Deep wheel ruts, detached panels and partially buried running gear join each wreck to the sand.
        for (const side of [-1, 1]) {
          box(g, scorched, side * w * 0.36, 0.01, d * 0.25, w * 0.19, 0.014, d * 2.1, false);
          for (let i = 0; i < 16; i++) box(g, sandMat, side * w * 0.36, 0.022, -d * 0.4 + i * d * 0.13, w * 0.2, 0.045, 0.07, false);
        }
        const chassis = new T.Group(); g.add(chassis); chassis.rotation.z = isTank ? -0.065 : 0.045; chassis.position.y = -0.08;
        box(chassis, scorched, 0, h * 0.25, 0, w * 0.93, h * 0.26, d * 0.9);
        box(chassis, olive, 0, h * 0.48, 0, w * 0.85, h * 0.29, d * 0.82);
        for (const side of [-1, 1]) {
          const trackZ = isTank ? 0 : d * 0.2;
          box(chassis, rubber, side * w * 0.43, h * 0.2, trackZ, w * 0.17, h * 0.33, d * (isTank ? 0.94 : 0.55));
          const count = isTank ? 6 : 4;
          for (let i = 0; i < count; i++) {
            const z = isTank ? -d * 0.36 + i * d * 0.144 : -d * 0.02 + i * d * 0.14;
            const wheel = mesh(chassis, cylinderGeo, olive, side * w * 0.48, h * 0.22, z, h * 0.15, w * 0.065, h * 0.15); wheel.rotation.z = Math.PI / 2;
            const hub = mesh(chassis, cylinderGeo, black, side * w * 0.518, h * 0.22, z, h * 0.063, 0.025, h * 0.063); hub.rotation.z = Math.PI / 2;
          }
          if (!isTank) {
            const frontWheel = mesh(chassis, cylinderGeo, rubber, side * w * 0.43, h * 0.21, -d * 0.34, h * 0.21, w * 0.16, h * 0.21); frontWheel.rotation.z = Math.PI / 2;
          }
          for (let i = 0; i < 16; i++) box(chassis, steel, side * w * 0.43, h * 0.39, -d * 0.42 + i * d * 0.053, w * 0.19, 0.025, 0.07);
        }
        if (isTank) {
          const turret = mesh(chassis, geo(new T.CylinderGeometry(w * 0.28, w * 0.34, h * 0.33, 8)), olive, 0, h * 0.74, -d * 0.08, 1, 1, 1);
          turret.rotation.z = -0.05;
          mesh(chassis, cylinderGeo, scorched, w * 0.08, h * 0.92, -d * 0.1, w * 0.13, 0.05, w * 0.13);
          const hatch = mesh(chassis, cylinderGeo, olive, w * 0.08, h * 0.99, -d * 0.2, w * 0.13, 0.035, w * 0.13); hatch.rotation.x = 1.05;
          beam(chassis, scorched, [0, h * 0.78, -d * 0.22], [-w * 0.22, h * 0.58, -d * 0.51], w * 0.075, w * 0.075);
        } else {
          box(chassis, olive, 0, h * 0.68, -d * 0.28, w * 0.82, h * 0.24, d * 0.28);
          box(chassis, black, 0, h * 0.8, -d * 0.21, w * 0.62, h * 0.15, 0.065);
          box(chassis, scorched, 0, h * 0.65, d * 0.22, w * 0.7, 0.08, d * 0.48);
          for (const side of [-1, 1]) box(chassis, olive, side * w * 0.4, h * 0.73, d * 0.18, w * 0.06, h * 0.37, d * 0.53);
          box(chassis, olive, 0, h * 0.7, d * 0.44, w * 0.8, h * 0.25, 0.09);
          box(chassis, darkConcrete, 0, h * 0.39, -d * 0.46, w * 0.45, h * 0.2, 0.06);
        }
        for (let i = 0; i < 10; i++) {
          const x = (random() - 0.5) * w * 1.6, z = (random() - 0.5) * d * 1.35;
          const panel = box(g, i % 2 ? rust : scorched, x, 0.03, z, 0.15 + random() * 0.55, 0.045, 0.12 + random() * 0.4); panel.rotation.y = random() * Math.PI;
        }
        addSmoke(o.x, o.y + h * 0.7, o.z + d * 0.18, 0.9);
      } else if (o.type === 'bunker') {
        box(g, darkConcrete, 0, h * 0.2, 0, w, h * 0.4, d);
        box(g, concrete, 0, h * 0.84, 0, w, h * 0.32, d);
        box(g, concrete, -w * 0.36, h * 0.535, 0, w * 0.28, h * 0.27, d);
        box(g, concrete, w * 0.36, h * 0.535, 0, w * 0.28, h * 0.27, d);
        box(g, black, 0, h * 0.535, -d * 0.15, w * 0.47, h * 0.28, d * 0.18);
        box(g, concrete, 0, h * 0.665, d * 0.48, w * 0.58, h * 0.065, d * 0.1);
        box(g, darkConcrete, 0, h * 0.405, d * 0.48, w * 0.48, h * 0.035, d * 0.08);
        box(g, grassDark, 0, h + 0.035, 0, w * 0.94, 0.07, d * 0.89);
        beam(g, steel, [0, h * 0.48, d * 0.15], [0, h * 0.48, d * 0.5 + 0.12], 0.11);
        for (const x of [-w * 0.44, w * 0.44]) {
          const bags = new T.Group(); bags.position.set(x, 0, d * 0.53); g.add(bags); bagWall(bags, w * 0.2, 0.85, 0.65);
        }
      } else box(g, rubbleMat, 0, h / 2, 0, w, h, d);
      compactStatic(g);
      objects.set(o.id, g);
      return g;
    }
    for (const obstacle of initialGame.obstacles) buildObstacle(obstacle);

    function landingCraft(x, z, angle, scale) {
      const g = new T.Group(); g.position.set(x, -0.05, z); g.rotation.y = angle; g.scale.setScalar(scale || 1); scene.add(g);
      box(g, steel, 0, 0.36, 0, 3.3, 0.58, 10.8);
      box(g, darkConcrete, 0, 0.69, 0, 2.82, 0.12, 9.5);
      for (const side of [-1, 1]) {
        box(g, olive, side * 1.57, 1.07, 0, 0.17, 1.25, 10.8);
        for (let i = 0; i < 7; i++) box(g, steel, side * 1.45, 1.05, -4.4 + i * 1.4, 0.11, 1.05, 0.1);
      }
      box(g, olive, 0, 1.05, 5.3, 3.3, 1.15, 0.19);
      box(g, steel, 0.78, 1.8, 3.8, 1.1, 1.25, 1.45);
      box(g, black, 0.78, 2.07, 3.05, 0.76, 0.35, 0.02);
      const ramp = box(g, olive, 0, 0.23, -6.35, 3.06, 0.13, 2.24); ramp.rotation.x = -0.15;
      for (let i = 0; i < 9; i++) box(g, steel, 0, 0.73, -4.5 + i * 0.9, 2.8, 0.055, 0.045);
      compactStatic(g);
    }
    landingCraft(-19, 34, -0.09, 1); landingCraft(20, 42, 0.13, 1);
    landingCraft(-51, 49, -0.23, 1); landingCraft(48, 72, 0.18, 1); landingCraft(-28, 110, 0.07, 1);
    // Distant coastal defenses establish the wider landing without expanding the playable level.
    for (const [x, z] of [[-57, -105], [66, -118]]) {
      const g = new T.Group(); g.position.set(x, terrainHeight(x, z), z); scene.add(g);
      box(g, darkConcrete, 0, 2.05, 0, 10, 4.1, 7);
      box(g, black, 0, 2.1, 3.52, 5.5, 0.65, 0.045);
      box(g, concrete, 0, 4.15, 0, 10.5, 0.6, 7.5);
      beam(g, steel, [0, 2, 3.6], [1.4, 2.15, 5.8], 0.18);
    }

    function makeSoldier(actor, friendly) {
      const group = new T.Group(); scene.add(group);
      const uniform = friendly ? olive : enemyMat;
      const torso = new T.Group(); group.add(torso);
      box(torso, uniform, 0, 1.08, 0, 0.47, 0.6, 0.28);
      box(torso, strapMat, 0, 0.84, 0.005, 0.5, 0.085, 0.3);
      box(torso, strapMat, -0.13, 1.13, -0.151, 0.045, 0.53, 0.03);
      box(torso, strapMat, 0.13, 1.13, -0.151, 0.045, 0.53, 0.03);
      for (const x of [-0.14, 0.14]) box(torso, wood, x, 0.97, -0.18, 0.14, 0.16, 0.07);
      box(torso, friendly ? grassDark : scorched, 0, 1.1, 0.23, 0.38, 0.39, 0.2);
      mesh(torso, sphereGeo, skinMat, 0, 1.54, -0.012, 0.15, 0.19, 0.14);
      const helmet = mesh(torso, geo(new T.SphereGeometry(0.185, 10, 6, 0, Math.PI * 2, 0, Math.PI / 2)), friendly ? olive : scorched, 0, 1.59, 0, 1, 0.8, 1);
      mesh(torso, cylinderGeo, friendly ? olive : scorched, 0, 1.59, 0, 0.205, 0.023, 0.19);
      const legs = [];
      for (const side of [-1, 1]) {
        const leg = new T.Group(); leg.position.set(side * 0.135, 0.78, 0); group.add(leg);
        box(leg, uniform, 0, -0.24, 0, 0.19, 0.48, 0.19);
        box(leg, bootMat, 0, -0.58, -0.025, 0.18, 0.25, 0.22);
        box(leg, bootMat, 0, -0.73, -0.065, 0.19, 0.095, 0.3); legs.push(leg);
      }
      beam(torso, uniform, [-0.3, 1.32, 0], [-0.22, 1.1, -0.35], 0.155);
      beam(torso, uniform, [0.3, 1.32, 0], [0.2, 1.14, -0.23], 0.155);
      mesh(torso, sphereGeo, skinMat, -0.18, 1.13, -0.37, 0.075, 0.065, 0.085);
      box(torso, wood, 0.035, 1.19, -0.23, 0.1, 0.11, 0.66);
      box(torso, steel, 0.035, 1.21, -0.72, 0.055, 0.065, 0.47);
      const markMat = basic(friendly ? '#78c4c2' : '#c48266', { transparent: true, opacity: 0.85, depthTest: true });
      const marker = mesh(group, geo(new T.OctahedronGeometry(0.075, 0)), markMat, 0, 1.94, 0, 1, 1, 1, false);
      const entry = { group, torso, legs, marker, friendly, lastX: actor.x, lastZ: actor.z, step: random() * Math.PI * 2 };
      soldiers.set(actor.id, entry); return entry;
    }
    for (const a of initialGame.allies) makeSoldier(a, true);
    for (const a of initialGame.enemies) makeSoldier(a, false);

    const objectiveGroup = new T.Group(); scene.add(objectiveGroup);
    const objective = initialGame.objective;
    objectiveGroup.position.set(objective.x, terrainHeight(objective.x, objective.z) + 0.045, objective.z);
    const ring = mesh(objectiveGroup, geo(new T.TorusGeometry(1.9, 0.025, 4, 48)), basic('#d8b873', { transparent: true, opacity: 0.7 }), 0, 0.03, 0, 1, 1, 1, false); ring.rotation.x = Math.PI / 2;
    const objectiveMarker = mesh(objectiveGroup, geo(new T.OctahedronGeometry(0.28, 0)), basic('#e0c17d', { transparent: true, opacity: 0.85 }), 0, 3.6, 0, 1, 1, 1, false);
    const routeGroup = new T.Group(); routeGroup.visible = false; scene.add(routeGroup);
    const route = root.NormandyEngine.WORLD.route || [];
    const routeMat = basic('#d8bd78', { transparent: true, opacity: 0.55, depthWrite: false });
    const routeArrowGeometry = geo(new T.ConeGeometry(0.14, 0.42, 3));
    for (let i = 1; i < route.length; i++) {
      const a = route[i - 1], b = route[i], dist = Math.hypot(b.x - a.x, b.z - a.z);
      for (let k = 0.7; k < dist; k += 1.8) {
        const f = k / dist, x = a.x + (b.x - a.x) * f, z = a.z + (b.z - a.z) * f;
        const arrow = mesh(routeGroup, routeArrowGeometry, routeMat, x, terrainHeight(x, z) + 0.04, z, 1, 1, 1, false);
        arrow.rotation.x = -Math.PI / 2; arrow.rotation.z = -Math.atan2(b.x - a.x, -(b.z - a.z));
      }
    }
    compactStatic(routeGroup);

    // The weapon is attached to the camera, so movement, recoil and reload remain visible.
    const weapon = new T.Group(); camera.add(weapon);
    const sleeve = material('#626a4c'); const rifleWood = material('#6b4d32', { roughness: 0.71 });
    box(weapon, rifleWood, 0, -0.05, 0.08, 0.1, 0.14, 0.4);
    box(weapon, steel, 0, 0.025, -0.11, 0.085, 0.085, 0.43);
    box(weapon, rifleWood, 0, -0.012, -0.38, 0.075, 0.09, 0.35);
    box(weapon, steel, 0, 0.025, -0.62, 0.028, 0.032, 0.36);
    box(weapon, steel, 0, 0.058, -0.07, 0.046, 0.026, 0.045);
    box(weapon, steel, 0, 0.078, -0.77, 0.036, 0.055, 0.028);
    mesh(weapon, geo(new T.TorusGeometry(0.017, 0.004, 4, 12)), steel, 0, 0.094, -0.08, 1, 1, 1);
    beam(weapon, sleeve, [0.15, -0.32, 0.25], [0.09, -0.1, 0], 0.115, 0.12);
    mesh(weapon, sphereGeo, skinMat, 0.035, -0.07, -0.005, 0.064, 0.075, 0.08);
    const supportingArm = new T.Group(); weapon.add(supportingArm);
    beam(supportingArm, sleeve, [-0.32, -0.32, 0.18], [-0.065, -0.1, -0.34], 0.115, 0.12);
    mesh(supportingArm, sphereGeo, skinMat, -0.035, -0.07, -0.36, 0.065, 0.06, 0.09);
    const flash = mesh(weapon, geo(new T.ConeGeometry(0.055, 0.28, 5)), basic('#ffe0a0', { transparent: true, opacity: 0.95, depthWrite: false }), 0, 0.03, -0.9, 1, 1, 1, false);
    flash.rotation.x = -Math.PI / 2; flash.visible = false;
    // Camera attachments use their own final pass; scenery cannot cut through the rifle.
    weapon.traverse(o => { if (o.isMesh) { o.castShadow = false; o.receiveShadow = false; o.renderOrder = 20; } });
    const weaponScene = new T.Scene();
    const weaponCamera = new T.PerspectiveCamera(72, 1, 0.01, 8); weaponScene.add(weaponCamera); weaponCamera.add(weapon);
    weaponScene.add(new T.HemisphereLight('#e0e5df', '#73745c', 3));
    const weaponLight = new T.DirectionalLight('#ffdfb0', 2); weaponLight.position.set(-3, 4, -1); weaponScene.add(weaponLight);

    function resize() {
      const width = Math.max(1, canvas.clientWidth || canvas.width || 1280);
      const height = Math.max(1, canvas.clientHeight || canvas.height || 720);
      renderer.setSize(width, height, false);
      camera.aspect = width / height; camera.updateProjectionMatrix();
      weaponCamera.aspect = width / height; weaponCamera.updateProjectionMatrix();
    }
    function setVisuals(values) {
      Object.assign(settings, values || {});
      settings.wetness = Math.max(0, Math.min(1, Number(settings.wetness)));
      sandMat.roughness = 0.96 - settings.wetness * 0.59;
      sandMat.metalness = 0.025 + settings.wetness * 0.15;
      sandMat.color.set(settings.wetness > 0.25 ? '#c4bca2' : '#e0d3ae');
      scene.fog = settings.fog ? atmosphere : null;
      renderer.shadowMap.enabled = !!settings.shadows;
      sun.castShadow = !!settings.shadows;
      routeGroup.visible = !!settings.route;
      for (const m of materials) m.needsUpdate = true;
    }
    function updateEffects(game) {
      const ids = new Set();
      for (const e of game.effects || []) {
        ids.add(e.id);
        let v = activeEffects.get(e.id);
        if (!v) {
          if (e.type === 'shot' && e.from && e.to) {
            const geometry = new T.BufferGeometry().setFromPoints([new T.Vector3(e.from.x, e.from.y, e.from.z), new T.Vector3(e.to.x, e.to.y, e.to.z)]);
            const mat = new T.LineBasicMaterial({ color: e.friendly ? '#ffe4ac' : '#e0aa76', transparent: true, opacity: 0.7 });
            v = new T.Line(geometry, mat); v.userData.transientGeometry = true; scene.add(v);
          } else if (e.type === 'impact' || e.type === 'enemyHit' || e.type === 'debris') {
            const mat = basic(e.type === 'enemyHit' ? '#d6b987' : '#b1a58b', { transparent: true, opacity: 0.7, depthWrite: false });
            v = mesh(scene, sphereGeo, mat, e.x || 0, e.y || 0.05, e.z || 0, 0.055, 0.055, 0.055, false);
            v.userData.puff = true;
          }
          if (v) activeEffects.set(e.id, v);
        }
        if (v) {
          v.material.opacity = Math.min(0.8, Math.max(0, e.life * (v.isLine ? 8 : 2)));
          if (v.userData.puff) v.scale.setScalar(0.07 + Math.max(0, 0.6 - e.life) * 0.35);
        }
      }
      for (const [id, v] of activeEffects) if (!ids.has(id)) {
        scene.remove(v); v.material.dispose(); materials.delete(v.material);
        if (v.userData.transientGeometry) v.geometry.dispose(); activeEffects.delete(id);
      }
    }
    function render(game, dt, viewOptions) {
      if (disposed) return;
      const step = Math.max(0, Math.min(0.05, dt || 0)); elapsed += step;
      if (game.time < previousTime) {
        for (const e of soldiers.values()) { e.lastX = Infinity; e.lastZ = Infinity; }
      }
      previousTime = game.time;
      const p = game.player;
      const moving = !!p.moving && game.phase === 'playing';
      const cadence = p.sprinting ? 13 : p.crouching ? 6.5 : 9;
      const bob = moving ? Math.sin(game.time * cadence) * (p.sprinting ? 0.052 : 0.025) : Math.sin(elapsed * 1.6) * 0.004;
      const eye = p.crouching ? 1.08 : 1.68;
      camera.position.set(p.x, p.y + eye + bob, p.z);
      camera.rotation.set(p.pitch || 0, p.yaw || 0, 0, 'YXZ');
      const aim = !!p.aiming || !!(viewOptions && viewOptions.aim);
      const targetFov = aim ? 53 : 72;
      camera.fov += (targetFov - camera.fov) * Math.min(1, Math.max(step, 0.016) * 12); camera.updateProjectionMatrix();
      weaponCamera.fov = camera.fov; weaponCamera.updateProjectionMatrix();
      const sinceShot = game.time - (p.shotTime === undefined ? -100 : p.shotTime);
      const recoil = sinceShot >= 0 && sinceShot < 0.22 ? Math.exp(-sinceShot * 20) : 0;
      const reload = p.reloading ? Math.sin(Math.min(1, Math.max(0, p.reloadTime || 0) / 1.8) * Math.PI) : 0;
      weapon.position.set(aim ? 0.015 : 0.27, (aim ? -0.09 : -0.27) + bob * 0.7 - reload * 0.2, (aim ? -0.22 : -0.35) + recoil * 0.08);
      weapon.rotation.set(recoil * 0.1 - reload * 0.25, aim ? 0 : -0.018, (moving ? Math.cos(game.time * cadence * 0.5) * 0.015 : 0) + reload * 0.48);
      supportingArm.rotation.x = reload * -0.3;
      flash.visible = sinceShot >= 0 && sinceShot < 0.06 && game.phase === 'playing';
      flash.rotation.z = elapsed * 71;
      for (const actor of game.allies.concat(game.enemies)) {
        const v = soldiers.get(actor.id) || makeSoldier(actor, game.allies.includes(actor));
        const moved = Math.hypot(actor.x - v.lastX, actor.z - v.lastZ);
        if (moved > 0.002 && moved < 2) v.step += moved * 3.4;
        v.lastX = actor.x; v.lastZ = actor.z;
        v.group.position.set(actor.x, actor.y || 0, actor.z); v.group.rotation.y = actor.yaw || 0;
        const walk = actor.alive && moved > 0.002 && moved < 2;
        v.legs[0].rotation.x = walk ? Math.sin(v.step) * 0.46 : 0;
        v.legs[1].rotation.x = walk ? -Math.sin(v.step) * 0.46 : 0;
        v.torso.position.y = walk ? Math.abs(Math.sin(v.step)) * 0.035 : 0;
        v.group.rotation.z = actor.alive ? 0 : Math.PI / 2;
        if (!actor.alive) { v.group.position.y += 0.18; v.group.scale.setScalar(0.94); } else v.group.scale.setScalar(1);
        v.marker.visible = !!actor.alive;
        v.marker.rotation.y = elapsed;
      }
      for (const o of game.obstacles) {
        const g = objects.get(o.id);
        if (g) {
          g.visible = o.active !== false;
          if (o.destructible && o.active !== false) g.position.y = o.y + (o.health < 20 ? Math.sin(elapsed * 14) * 0.006 : 0);
        }
      }
      for (const s of smoke) {
        const cycle = (elapsed * 0.073 + s.phase) % 1;
        s.sprite.position.set(s.x + cycle * 2.9, s.y + cycle * 5.5, s.z + cycle * 0.5);
        s.sprite.scale.setScalar((1.1 + cycle * 3) * s.scale);
        s.sprite.material.opacity = Math.sin(cycle * Math.PI) * 0.22;
      }
      if (step > 0) {
        for (let i = 0; i < waterPositions.count; i++) {
          const x = waterPositions.getX(i), z = waterPositions.getZ(i);
          const height = Math.sin(x * 0.082 + z * 0.21 + elapsed * 1.3) * 0.07 + Math.sin(z * 0.46 - elapsed * 1.9) * 0.045;
          waterPositions.setY(i, -0.24 + height);
        }
        waterPositions.needsUpdate = true;
        for (let i = 0; i < surf.length; i++) { surf[i].position.z = Math.sin(elapsed * 0.5 + i * 0.5) * 1.1; surf[i].position.y = Math.sin(elapsed + i) * 0.014; }
      }
      objectiveMarker.position.y = 3.6 + Math.sin(elapsed * 1.8) * 0.12;
      objectiveMarker.rotation.y = elapsed * 0.6;
      objectiveGroup.visible = !game.objective.complete;
      updateEffects(game);
      renderer.autoClear = true; renderer.render(scene, camera);
      renderer.autoClear = false; renderer.clearDepth();
      if (game.phase !== 'dead') renderer.render(weaponScene, weaponCamera);
      renderer.autoClear = true;
    }
    function setQuality(level) {
      renderer.setPixelRatio(Math.min(root.devicePixelRatio || 1, level === 'low' ? 1 : 1.5));
      setVisuals({ shadows: level !== 'low' }); resize();
    }
    function dispose() {
      disposed = true;
      for (const e of activeEffects.values()) { if (e.userData.transientGeometry) e.geometry.dispose(); e.material.dispose(); }
      for (const g of resources) g.dispose();
      for (const m of materials) m.dispose();
      for (const t of trackedTextures) t.dispose();
      renderer.dispose();
    }
    resize(); setVisuals(settings);
    if (options.quality) setQuality(options.quality);
    render(initialGame, 0);
    return { render, resize, dispose, setVisuals, setQuality, renderer, camera, scene };
  }
  root.NormandyScene = { create };
})(typeof window === 'undefined' ? globalThis : window);
