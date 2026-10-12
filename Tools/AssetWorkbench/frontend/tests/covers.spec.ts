import {test,expect} from '@playwright/test';
import {readFileSync,mkdirSync} from 'node:fs';
import {resolve} from 'node:path';
const state=resolve(process.cwd(),'../../../Assets/LocalWorking/AssetWorkbench');
test('all animation covers decode and show actual capture labels in both languages',async({page,context})=>{
 test.setTimeout(120000);
 const session=JSON.parse(readFileSync(resolve(state,'runtime/session.json'),'utf8'));
 expect((await context.request.post('/api/v1/session',{data:{token:session.token},headers:{Origin:`http://127.0.0.1:${session.port}`}})).ok()).toBeTruthy();
 await page.goto('/assets?parent=ue4-animation-collection');
 let decoded=0;
 for(let n=0;n<6;n++){
  await expect(page.locator('.asset-card')).toHaveCount(n===5?5:24);
  for(const img of await page.locator('.card-media img').all()){
   await img.scrollIntoViewIfNeeded();
   await img.evaluate((el:HTMLImageElement)=>el.decode());
   await expect(img).toHaveClass('contain');
   expect(await img.getAttribute('src')).toContain('native-cover-');decoded++;
  }
  if(n<5)await page.getByRole('button',{name:'下一页',exact:true}).click();
 }
 expect(decoded).toBe(125);
 await page.goto('/assets/anim-movement-animset-pro');await page.getByRole('button',{name:'图片与音频',exact:true}).click();
 await page.locator('.detail-media img').evaluate((el:HTMLImageElement)=>el.decode());
 await expect(page.locator('.detail-media')).toContainText('外部预览人偶');
 await page.getByRole('button',{name:'English',exact:true}).click();
 await expect(page.locator('.detail-media')).toContainText('external preview mannequin');
 await page.goto('/assets/anim-rifle-animset-pro');await page.getByRole('button',{name:'Images & audio',exact:true}).click();
 await expect(page.locator('.media-thumbs button')).toHaveCount(2);
 await expect(page.locator('.detail-media')).toContainText('Native animation preview');
 await page.locator('.media-thumbs button').last().click();
 await page.locator('.detail-media img').evaluate((el:HTMLImageElement)=>el.decode());
 const shots=resolve(state,'runs/covers');mkdirSync(shots,{recursive:true});
 await page.screenshot({path:resolve(shots,'detail-en.png'),fullPage:true});
 await page.getByRole('button',{name:'中文',exact:true}).click();
 await page.goto('/assets?parent=ue4-animation-collection');
 await expect(page.locator('.asset-card')).toHaveCount(24);
 for(const img of await page.locator('.card-media img').all()){await img.scrollIntoViewIfNeeded();await img.evaluate((el:HTMLImageElement)=>el.decode())}
 await page.evaluate(()=>scrollTo(0,0));await page.screenshot({path:resolve(shots,'library-zh.png'),fullPage:true});
});
