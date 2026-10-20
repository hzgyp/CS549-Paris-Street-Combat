// Isolated owned browser, never attaches to user/UE sessions.
const fs=require('node:fs'),path=require('node:path'),{pathToFileURL}=require('node:url');
const [runArg,packageArg,browserArg]=process.argv.slice(2),run=path.resolve(runArg);
if(!runArg||!packageArg||!browserArg)throw Error('run dir, Playwright package dir, browser executable required');
if(fs.existsSync(path.join(run,'BROWSER_VERIFY.json')))throw Error('Preserve receipts; choose a unique run');
const {chromium}=require(path.resolve(packageArg));
(async()=>{const browser=await chromium.launch({headless:true,executablePath:path.resolve(browserArg)});
const page=await browser.newPage({viewport:{width:1450,height:1080}}),checks=[],errors=[];
const check=(name,passed,evidence)=>checks.push({name,passed:!!passed,evidence});
page.on('pageerror',e=>errors.push(String(e)));
try{
await page.addInitScript(()=>{window.invalidCanvasArcs=0;const arc=CanvasRenderingContext2D.prototype.arc;CanvasRenderingContext2D.prototype.arc=function(...args){if(!args.every(Number.isFinite))window.invalidCanvasArcs++;return arc.apply(this,args);};});
await page.goto(pathToFileURL(path.join(run,'index.html')).href);
await page.waitForFunction(()=>window.mapSketchInspect?.().mapLoaded);
const state=()=>page.evaluate(()=>window.mapSketchInspect());
check('default six-member finite replay',Object.keys((await state()).units).length===6,await page.locator('#state').innerText());
check('ten canonical scenarios',await page.locator('#scenario option').count()===10,10);
check('CP1 world pixel centre',(await state()).worldToPixel.join(',')==='299,827',(await state()).worldToPixel);
check('surface scopes remain independent',await page.locator('#layer option').count()===5,(await state()).scope);
for(const scope of ['saved','bounded_expanded']){await page.locator('#scope').selectOption(scope);const count=await page.locator('#layer option').count();for(let layer=0;layer<count;layer++){await page.locator('#layer').selectOption(String(layer));await page.waitForFunction(()=>window.mapSketchInspect().mapLoaded);for(const display of ['status','candidate']){await page.locator('#display').selectOption(display);await page.waitForFunction(()=>window.mapSketchInspect().mapLoaded);}}check(scope+' all image pairs readable',count===(scope==='saved'?3:5),count);}
await page.locator('#layer').selectOption('0');await page.waitForFunction(()=>window.mapSketchInspect().mapLoaded);
await page.locator('#agent').selectOption('A2');await page.locator('#seek').fill('12');await page.locator('#seek').dispatchEvent('input');
check('private state scrubbed', (await page.locator('#state').innerText()).includes('Overwatch'),await page.locator('#state').innerText());
await page.locator('#reset').click();await page.locator('#speed').selectOption('4');await page.locator('#play').click();await page.waitForTimeout(500);await page.locator('#play').click();check('finite playback advances',(await state()).frame>0,(await state()).frame);
await page.locator('#seek').fill(await page.locator('#seek').getAttribute('max'));await page.locator('#seek').dispatchEvent('input');check('last frame stays bounded',!(await state()).playing,await page.locator('#time').innerText());
await page.locator('#scenario').selectOption('0');await page.locator('#seek').fill('10');await page.locator('#seek').dispatchEvent('input');await page.locator('#truth').uncheck();check('hidden target stays unshown',await page.locator('#units').innerText().then(s=>s.includes('回放隐藏')),await page.locator('#state').innerText());await page.locator('#truth').check();
await page.locator('#scenario').selectOption('6');await page.locator('#focus').click();await page.screenshot({path:path.join(run,'map-focus.jpg'),type:'jpeg',quality:76,fullPage:true});
await page.locator('#whole').click();await page.screenshot({path:path.join(run,'map-overview.jpg'),type:'jpeg',quality:72,fullPage:true});check('full surveyed extent fits canvas',(await state()).view.scale<5,(await state()).view);
await page.locator('#focus').click();let before=await state();const rect=await page.locator('#map').boundingBox(),cx=rect.x+rect.width/2,cy=rect.y+rect.height/2;
await page.mouse.move(cx,cy);await page.mouse.down();await page.mouse.move(cx+30,cy+20,{steps:3});await page.mouse.up();let after=await state();check('projection origin draggable',Math.abs(after.origin[0]-before.origin[0])>1,[before.origin,after.origin]);
await page.locator('#mode').selectOption('layout');await page.locator('#agent').selectOption('A1');before=await state();const ar=before.units.A1.position,sx=rect.x+rect.width/2+(ar[0]-before.view.x)*before.view.scale,sy=rect.y+rect.height/2-(ar[1]-before.view.y)*before.view.scale;
await page.mouse.move(sx,sy);await page.mouse.down();await page.mouse.move(sx+50,sy+30,{steps:3});await page.mouse.up();after=await state();check('individual unit drag',Math.hypot(...after.units.A1.position.map((v,i)=>v-before.units.A1.position[i]))>1,after.units.A1.position);
await page.locator('#note').fill('看见目标后支援；丢失视线只搜索最后观察点。');await page.locator('#targetTool').click();await page.mouse.click(cx+100,cy-70);check('desired target arrow authored',(await state()).units.A1.target!==null,(await state()).units.A1.target);
await page.locator('#anchor').selectOption('T2');check('anchor relocation retains unique notes and targets',(await state()).units.A1.note.includes('最后观察点')&&(await state()).units.A1.target!==null,(await state()).units.A1);
await page.locator('#export').click();const draft=JSON.parse(await page.locator('#draft').inputValue());check('local export retains coordinate/provenance/intent',draft.units.A1.target&&draft.units.A1.note&&draft.survey_scope==='bounded_expanded'&&draft.schema==='paris.npc.interaction-layout.v1',draft.scope);
await page.locator('#clearTarget').click();check('intent cleared without unit reset',(await state()).units.A1.target===null&&(await state()).units.A1.note===draft.units.A1.note,(await state()).units.A1.note);
await page.locator('#mode').selectOption('replay');await page.locator('#mode').selectOption('layout');check('mode switch preserves layout edits',(await state()).units.A1.note===draft.units.A1.note,(await state()).units.A1.note);
await page.setViewportSize({width:390,height:844});await page.locator('#focus').click();await page.screenshot({path:path.join(run,'map-mobile.jpg'),type:'jpeg',quality:68,fullPage:true});check('390px viewport without horizontal overflow',await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),await page.evaluate(()=>({page:document.documentElement.scrollWidth,viewport:innerWidth})));
check('finite canvas arguments',await page.evaluate(()=>window.invalidCanvasArcs===0),await page.evaluate(()=>window.invalidCanvasArcs));check('clear map versus projected trace boundary',(await page.locator('.footer').innerText()).includes('候选点不证明连通')&&(await page.locator('#boundary').innerText()).includes('尚未执行'),await page.locator('#boundary').innerText());check('no JavaScript errors',errors.length===0,errors);
}catch(e){errors.push(String(e));check('browser workflow completes',false,String(e));}finally{await browser.close();const receipt={scope:'local_design_board_UI_not_UE_or_measured_route_acceptance',checks,errors,passed:checks.filter(c=>c.passed).length,total:checks.length};fs.writeFileSync(path.join(run,'BROWSER_VERIFY.json'),JSON.stringify(receipt,null,2)+'\n');console.log(JSON.stringify({passed:receipt.passed,total:receipt.total,failed:checks.filter(c=>!c.passed)}));if(receipt.passed!==receipt.total)process.exitCode=1;}
})();
