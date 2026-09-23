'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=__dirname+'/';
const html=fs.readFileSync(root+'index.html','utf8'),source=fs.readFileSync(root+'app.js','utf8');
const RealEngine=require(root+'engine.js');
const reports=[];
function test(name,fn){fn();reports.push({name,status:'PASS'});}
class Target {
  constructor(){this.listeners={};}
  addEventListener(type,fn){(this.listeners[type]??=[]).push(fn);}
  dispatch(type,extra={}){const event={type,preventDefault(){this.defaultPrevented=true;},...extra};for(const fn of this.listeners[type]??[])fn(event);return event;}
}
function harness({fine=true,sceneFailure=false}={}){
  let now=1000,game;
  const document=new Target(),win=new Target(),elements=new Map(),used=new Set(),raf=[],errors=[],calls={render:0,resize:0,visuals:[]};
  class Element extends Target {
    constructor(id,tag,attrs=''){super();this.id=id;this.tagName=tag.toUpperCase();this.hidden=/\bhidden\b/.test(attrs);this.disabled=/\bdisabled\b/.test(attrs);this.checked=/\bchecked\b/.test(attrs);this.value=/\bvalue="([^"]*)"/.exec(attrs)?.[1]??'';this.textContent='';this.innerHTML='';this.style={};this.dataset={};this.attributes={};const classes=new Set();this.classList={toggle(name,force){const yes=force===undefined?!classes.has(name):force;if(yes)classes.add(name);else classes.delete(name);return yes;},contains(name){return classes.has(name);}};}
    focus(){document.activeElement=this;}
    setAttribute(name,value){this.attributes[name]=String(value);}
    setPointerCapture(){}
    requestPointerLock(){document.pointerLockElement=this;document.dispatch('pointerlockchange');}
  }
  for(const match of html.matchAll(/<([a-z][a-z0-9]*)\b([^>]*\bid="([^"]+)"[^>]*)>/gi)){assert(!elements.has(match[3]),'duplicate id '+match[3]);elements.set(match[3],new Element(match[3],match[1],match[2]));}
  const moves=[];for(const match of html.matchAll(/<button\b([^>]*data-move="([^"]+)"[^>]*)>/g)){const button=new Element('move-'+match[2],'button',match[1]);button.dataset.move=match[2];moves.push(button);}
  document.body=new Element('body','body');document.activeElement=document.body;document.hidden=false;document.pointerLockElement=null;
  document.getElementById=id=>{used.add(id);assert(elements.has(id),'app references missing DOM id '+id);return elements.get(id);};
  document.querySelectorAll=selector=>{assert.equal(selector,'[data-move]');return moves;};
  document.exitPointerLock=()=>{document.pointerLockElement=null;document.dispatch('pointerlockchange');};
  const E={...RealEngine,createGame(){game=RealEngine.createGame();return game;}};
  const scene={create(options){assert.equal(options.canvas,elements.get('gameCanvas'));assert.equal(options.game,game);if(sceneFailure)throw Error('Synthetic renderer failure');return {render(state,dt){assert.equal(state,game);assert(dt>=0&&dt<=.05);calls.render++;},resize(){calls.resize++;},setVisuals(value){calls.visuals.push(value);}};}};
  Object.assign(win,{document,NormandyEngine:E,NormandyScene:scene,THREE:{},performance:{now:()=>now},matchMedia:()=>({matches:fine}),requestAnimationFrame:fn=>raf.push(fn),console:{error:(...x)=>errors.push(x),log(){}}});
  win.window=win;const context=vm.createContext(win);vm.runInContext(source,context,{filename:'app.js'});
  function frames(n=1,ms=16){for(let i=0;i<n;i++){now+=ms;assert(raf.length,'animation frame requested');const fn=raf.shift();fn(now);}}
  function key(code,type='keydown',extra={}){return win.dispatch(type,{code,repeat:false,...extra});}
  function click(id){elements.get(id).dispatch('click');}
  const get=id=>elements.get(id);
  return {get,click,key,frames,document,win,calls,used,elements,moves,errors,get game(){return game;},start(){click('startButton');frames(2);},state(){return JSON.parse(JSON.stringify(win.NormandyDemo.getState()));}};
}

test('All controller DOM ids exist; initial scene, controls and rendering initialize',()=>{
  for(const match of source.matchAll(/\$\('([^']+)'\)/g))assert(html.includes('id="'+match[1]+'"'),match[1]);
  const h=harness();assert.equal(h.errors.length,0);assert.equal(h.game.phase,'ready');assert.equal(h.get('startButton').disabled,false);assert.equal(h.get('briefing').hidden,false);assert.equal(h.get('hud').hidden,true);assert.equal(h.calls.visuals[0].wetness,.75);h.frames();assert.equal(h.calls.render,1);h.win.dispatch('resize');assert.equal(h.calls.resize,1);assert(h.used.size>=35);
});

test('Begin captures mouse; WASD/shift move; mouse/arrows aim; C/F update stance',()=>{
  const h=harness();h.start();assert.equal(h.game.phase,'playing');assert.equal(h.document.pointerLockElement,h.get('gameCanvas'));assert.equal(h.get('hud').hidden,false);
  const start=h.game.player.z;h.key('KeyW');h.key('ShiftLeft');h.frames(20);h.key('KeyW','keyup');h.key('ShiftLeft','keyup');assert(h.game.player.z<start-1.5);assert.equal(h.game.player.sprinting,true);
  const oldX=h.game.player.x;h.key('KeyD');h.frames(10);h.key('KeyD','keyup');assert(h.game.player.x>oldX+.4);
  h.document.dispatch('mousemove',{movementX:100,movementY:-50});assert(h.game.player.yaw<0);assert(h.game.player.pitch>0);
  const yaw=h.game.player.yaw;h.key('ArrowLeft');h.frames(10);h.key('ArrowLeft','keyup');assert(h.game.player.yaw>yaw);
  h.key('KeyC');h.key('KeyC','keyup');h.key('KeyF');h.key('KeyF','keyup');h.frames(6);assert(h.game.player.crouching);assert(h.game.player.aiming);assert.equal(h.get('stance').textContent,'CROUCHED');assert(h.get('crosshair').classList.contains('aim'));
});

test('Mouse and Space fire real ammo; reload blocks shots until completion',()=>{
  const h=harness();h.start();h.get('gameCanvas').dispatch('pointerdown',{button:0,pointerType:'mouse'});assert.equal(h.game.player.ammo,7);h.frames(20);h.key('Space');h.key('Space','keyup');assert.equal(h.game.player.ammo,6);h.key('KeyR');h.key('KeyR','keyup');h.frames(5);assert(h.game.player.reloading);assert.equal(h.get('weaponState').textContent,'RELOADING');h.key('Space');h.key('Space','keyup');assert.equal(h.game.player.ammo,6);h.frames(130);assert.equal(h.game.player.ammo,8);assert.equal(h.game.player.reserve,62);assert.equal(h.get('ammo').textContent,'08');
});

test('Escape and pointer unlock pause; resume clears held inputs; restart rebuilds state',()=>{
  const h=harness();h.start();h.key('KeyW');h.frames(5);h.key('Escape');const before=h.state();h.frames(20);assert.equal(h.game.phase,'paused');assert.deepEqual(h.state(),before);assert.equal(h.get('hud').hidden,true);assert.equal(h.get('briefEyebrow').textContent,'MISSION PAUSED');h.click('startButton');h.frames(5);const resumed=h.game.player.z;h.frames(5);assert.equal(h.game.player.z,resumed);h.document.exitPointerLock();assert.equal(h.game.phase,'paused');h.click('restartBrief');h.frames(5);assert.equal(h.game.phase,'playing');assert.equal(h.game.player.z,21);assert.equal(h.game.player.ammo,8);
});

test('Settings pause safely and send wetness, haze and shadow values to renderer',()=>{
  const h=harness();h.start();h.click('settingsButton');assert.equal(h.game.phase,'paused');assert.equal(h.get('settings').hidden,false);assert.equal(h.get('settingsButton').attributes['aria-expanded'],'true');h.get('wetness').value='20';h.get('fog').checked=false;h.get('shadows').checked=false;h.get('wetness').dispatch('input');assert.deepEqual(JSON.parse(JSON.stringify(h.calls.visuals.at(-1))),{wetness:.2,fog:false,shadows:false});assert.equal(h.get('wetnessValue').textContent,'20%');h.click('closeSettings');assert(h.get('settings').hidden);assert.equal(h.game.phase,'paused');h.click('startButton');h.win.dispatch('blur');assert.equal(h.game.phase,'paused');
});

test('Drag and tap fallback work without pointer lock; touch movement, aim and fire work',()=>{
  const h=harness({fine:false});h.start();assert.equal(h.document.pointerLockElement,null);const canvas=h.get('gameCanvas');canvas.dispatch('pointerdown',{button:0,pointerId:1,pointerType:'touch',clientX:100,clientY:100});canvas.dispatch('pointermove',{pointerId:1,clientX:180,clientY:70});canvas.dispatch('pointerup',{button:0,pointerId:1});assert(h.game.player.yaw<0);assert(h.game.player.pitch>0);assert.equal(h.game.player.ammo,8);
  canvas.dispatch('pointerdown',{button:0,pointerId:2,pointerType:'touch',clientX:100,clientY:100});canvas.dispatch('pointerup',{button:0,pointerId:2});assert.equal(h.game.player.ammo,7);
  const forward=h.moves.find(x=>x.dataset.move==='forward');forward.dispatch('pointerdown',{pointerId:3});const old=h.game.player.z;h.frames(20);forward.dispatch('pointerup');assert(h.game.player.z<old);h.click('touchAim');h.frames(2);assert(h.game.player.aiming);h.get('touchFire').dispatch('pointerdown',{pointerId:4});h.frames(40);h.get('touchFire').dispatch('pointerup');assert(h.game.player.ammo<=4);h.click('touchReload');h.frames(130);assert.equal(h.game.player.ammo,8);
});

test('Defender-hit events update mission messages and destroyed-cover events display',()=>{
  const h=harness();h.start();const g=h.game,e=g.enemies[0];g.player.x=0;g.player.z=-42;g.player.y=0;function aim(target){const from=RealEngine.eye(g.player);g.player.yaw=Math.atan2(from.x-target.x,from.z-target.z);g.player.pitch=Math.atan2(target.y-from.y,Math.hypot(target.x-from.x,target.z-from.z));}
  aim({x:e.x,y:e.y+1.5,z:e.z});h.key('Space');h.key('Space','keyup');h.frames(20);h.key('Space');h.key('Space','keyup');h.frames(6);assert.equal(g.defeated,1);assert.equal(String(h.get('defenders').textContent),'1');assert.equal(h.get('message').textContent,'One defender remains.');
  const o=g.obstacles.find(x=>x.destructible);g.player.x=o.x;g.player.z=o.z+5;g.player.y=0;aim({x:o.x,y:.7,z:o.z});h.frames(20);h.key('Space');h.key('Space','keyup');h.frames(20);h.key('Space');h.key('Space','keyup');h.frames(6);assert.equal(o.active,false);assert.equal(h.get('message').textContent,'Wooden cover destroyed — the opening is clear.');
});

test('Real death and win transitions display correct briefing and restart actions',()=>{
  const h=harness();h.start();h.game.player.x=-11;h.game.player.z=-36;h.game.player.health=1;h.game.enemies[0].fireTimer=0;h.frames(2);assert.equal(h.game.phase,'dead');assert.equal(h.get('briefEyebrow').textContent,'MISSION ENDED');assert(h.get('startButton').innerHTML.includes('Try again'));h.click('startButton');h.frames(2);assert.equal(h.game.phase,'playing');assert.equal(h.game.player.health,100);
  for(const e of h.game.enemies){e.alive=false;e.health=0;}h.game.defeated=2;h.game.player.x=5;h.game.player.z=-79;h.game.player.y=RealEngine.heightAt(5,-79);h.frames(2);assert.equal(h.game.phase,'won');assert.equal(h.get('briefEyebrow').textContent,'OBJECTIVE COMPLETE');assert(h.get('briefText').textContent.includes('Both defenders cleared.'));h.click('startButton');h.frames(2);assert.equal(h.game.phase,'playing');assert.equal(h.game.player.ammo,8);
});

test('FPS uses actual frame interval, while simulation remains capped for slow frames',()=>{
  const h=harness();h.frames(150,100);assert.equal(h.get('fps').textContent,'10 fps');h.start();const old=h.game.time;h.frames(10,100);assert(Math.abs(h.game.time-old-.5)<1e-8);
});

test('Initialization failure presents the visible error state',()=>{
  const h=harness({sceneFailure:true});assert.equal(h.get('error').hidden,false);assert.equal(h.get('briefing').hidden,true);assert(h.get('errorText').textContent.includes('Synthetic renderer failure'));assert.equal(h.errors.length,1);
});
console.log(JSON.stringify({suite:'FPS controller with DOM/API stubs and real simulation',passed:reports.length,limitations:'No native DOM, browser input dispatch, audio, WebGL, GPU or visual-layout validation.',results:reports},null,2));
