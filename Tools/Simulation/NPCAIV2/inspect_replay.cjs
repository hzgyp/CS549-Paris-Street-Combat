// Isolated headless browser; never attaches to a user's browser or UE process.
// node inspect_replay.cjs <run-dir> <absolute-playwright-package-dir> <browser-exe>
const fs=require('node:fs');
const path=require('node:path');
const {pathToFileURL}=require('node:url');
const [runArg,packageArg,browserArg]=process.argv.slice(2);
if(!runArg||!packageArg||!browserArg)throw Error('Expected run-dir, playwright package directory, browser executable');
const run=path.resolve(runArg);
const receiptPath=path.join(run,'BROWSER_VERIFY.json');
if(fs.existsSync(receiptPath))throw Error('Preserve prior browser receipt; select a new run identity');
const {chromium}=require(path.resolve(packageArg));
(async()=>{
const browser=await chromium.launch({headless:true,executablePath:path.resolve(browserArg)});
const page=await browser.newPage({viewport:{width:1380,height:1000}});
const errors=[],checks=[];
page.on('pageerror',e=>errors.push(String(e)));
const check=(name,pass,evidence)=>checks.push({name,pass:!!pass,evidence});
try{
await page.goto(pathToFileURL(path.join(run,'replay.html')).href);
check('13 finite candidate/reference options',await page.locator('#scenario option').count()===13,await page.locator('#scenario option').count());
await page.locator('#scenario').selectOption('6');await page.locator('#agent').selectOption('A1');
await page.locator('#seek').fill('12');await page.locator('#seek').dispatchEvent('input');
check('scrub displays Support and 6 scored candidates',(await page.locator('#state').innerText()).includes('Support')&&await page.locator('#scores tr').count()===6,await page.locator('#time').innerText());
await page.screenshot({path:path.join(run,'replay-desktop.jpg'),type:'jpeg',quality:76,fullPage:true});
await page.locator('#agent').selectOption('A2');
check('independent ally inspection displays Overwatch',(await page.locator('#state').innerText()).includes('Overwatch'),await page.locator('#state').innerText());
await page.locator('#scenario').selectOption('0');await page.locator('#seek').fill('10');await page.locator('#seek').dispatchEvent('input');
check('sight loss trace can be inspected',(await page.locator('#state').innerText()).includes('Search'),await page.locator('#state').innerText());
await page.locator('#truth').uncheck();check('truth visibility toggle responds',!await page.locator('#truth').isChecked(),false);
await page.locator('#reset').click();const before=await page.locator('#seek').inputValue();await page.locator('#speed').selectOption('4');await page.locator('#play').click();await page.waitForTimeout(500);await page.locator('#play').click();
check('finite playback advances recorded time',+(await page.locator('#seek').inputValue())>+before,await page.locator('#time').innerText());
await page.locator('#scenario').selectOption('7');await page.locator('#seek').fill('48');await page.locator('#seek').dispatchEvent('input');
check('bottleneck final frame is reachable',await page.locator('#time').innerText()==='24.0 / 24 s',await page.locator('#time').innerText());
await page.setViewportSize({width:390,height:844});await page.locator('#scenario').selectOption('6');await page.locator('#seek').fill('12');await page.locator('#seek').dispatchEvent('input');
const dimensions=await page.evaluate(()=>({scroll:document.documentElement.scrollWidth,client:document.documentElement.clientWidth}));
check('390px layout has no document horizontal overflow',dimensions.scroll<=dimensions.client,dimensions);
await page.screenshot({path:path.join(run,'replay-mobile.jpg'),type:'jpeg',quality:72,fullPage:true});
check('no browser JavaScript errors',errors.length===0,errors);
}finally{await browser.close();}
const receipt={scope:'independent_headless_local_replay_UI_not_UE',checks,errors,status:checks.every(c=>c.pass)?'pass':'failed_preserve_candidate',screenshots:['replay-desktop.jpg','replay-mobile.jpg']};
fs.writeFileSync(receiptPath,JSON.stringify(receipt,null,2));
console.log(JSON.stringify({status:receipt.status,passed:checks.filter(c=>c.pass).length,total:checks.length,failures:checks.filter(c=>!c.pass)}));
if(receipt.status!=='pass')process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1;});
