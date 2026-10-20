import {test,expect} from '@playwright/test';
import {mkdirSync} from 'node:fs';
import {resolve} from 'node:path';
const shots=resolve(process.cwd(),'../../../Assets/LocalWorking/AssetWorkbench/runs/tree-window-20261017/screenshots');mkdirSync(shots,{recursive:true});
test.beforeEach(async({page})=>{await page.goto('/npc-simulation');await expect(page.locator('#npc-tree-expand')).toBeVisible();});
async function fitBounds(page:any){
 await page.locator('#npc-tree-fit').click();
 const bounds=await page.locator('.npc-bt-viewport').evaluate((el:HTMLElement)=>{const svg=el.querySelector('svg')!.getBoundingClientRect(),box=el.getBoundingClientRect();return {right:svg.right-box.left,bottom:svg.bottom-box.top,width:el.clientWidth,height:el.clientHeight}});
 expect(bounds.right).toBeLessThanOrEqual(bounds.width+2);expect(bounds.bottom).toBeLessThanOrEqual(bounds.height+2);
}
test('large workspace, complete-tree fit, inspector toggle and keyboard restoration',async({page})=>{
 const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
 const inline=await page.locator('.npc-bt-viewport').boundingBox();expect(inline!.height).toBeGreaterThan(480);
 const actor=await page.locator('.npc-bt').getAttribute('data-actor'),at=await page.locator('.npc-bt').getAttribute('data-tick-at');
 await page.locator('#npc-tree-expand').click();const dialog=page.getByRole('dialog',{name:'行为树查看器'});await expect(dialog).toBeVisible();
 expect(await page.locator('#root').evaluate((el:HTMLElement)=>el.inert)).toBeTruthy();
 const rect=await dialog.boundingBox();expect(rect!.width).toBeGreaterThan(1880);expect(rect!.height).toBeGreaterThan(1040);
 await fitBounds(page);await page.locator('#npc-tree-full').check();await fitBounds(page);
 const narrow=await page.locator('.npc-bt-viewport').boundingBox();await page.getByRole('button',{name:'收起详情',exact:true}).click();await expect(page.locator('.npc-bt-inspect')).toBeHidden();
 const wide=await page.locator('.npc-bt-viewport').boundingBox();expect(wide!.width-narrow!.width).toBeGreaterThan(300);
 await fitBounds(page);await page.screenshot({path:resolve(shots,'full-tree-1920.jpg'),type:'jpeg',quality:72});
 await page.getByRole('button',{name:'显示详情',exact:true}).click();await fitBounds(page);
 await page.locator('[data-node-id]').first().click();await expect(page.locator('#npc-tree-node-title')).toBeVisible();
 await expect(dialog).toHaveAttribute('data-actor',actor!);await expect(dialog).toHaveAttribute('data-tick-at',at!);
 await page.keyboard.press('Escape');await expect(page.getByRole('dialog')).toHaveCount(0);
 await expect(page.locator('#npc-tree-expand')).toBeFocused();expect(await page.locator('#root').evaluate((el:HTMLElement)=>el.inert)).toBeFalsy();expect(await page.evaluate(()=>document.body.style.overflow)).not.toBe('hidden');expect(errors).toEqual([]);
});
test('zoom and background dragging preserve node selection and recorded decision',async({page})=>{
 await page.locator('#npc-tree-expand').click();await page.getByRole('button',{name:'收起详情',exact:true}).click();
 await page.getByRole('button',{name:'100%',exact:true}).click();
 const before=await page.locator('.npc-bt').getAttribute('data-tick-at'),picked=await page.locator('.bt-picked').getAttribute('data-node-id');
 await page.getByRole('button',{name:'放大行为树',exact:true}).click();await expect(page.locator('.npc-bt-zoom output')).toHaveText('120%');
 await page.getByRole('button',{name:'缩小行为树',exact:true}).click();await expect(page.locator('.npc-bt-zoom output')).toHaveText('100%');
 const vp=page.locator('.npc-bt-viewport');await vp.evaluate((el:HTMLElement)=>el.scrollTo(150,200));const box=(await vp.boundingBox())!;
 await page.mouse.move(box.x+7,box.y+box.height-25);await page.mouse.down();await page.mouse.move(box.x+7,box.y+box.height-125,{steps:8});await page.mouse.up();
 expect(await vp.evaluate((el:HTMLElement)=>el.scrollTop)).toBeGreaterThan(250);
 await expect(page.locator('.bt-picked')).toHaveAttribute('data-node-id',picked!);await expect(page.locator('.npc-bt')).toHaveAttribute('data-tick-at',before!);
 await page.keyboard.down('Control');await page.mouse.wheel(0,-180);await page.keyboard.up('Control');await expect(page.locator('.npc-bt-zoom output')).not.toHaveText('100%');
 await page.getByRole('button',{name:'显示详情',exact:true}).click();await page.locator('#npc-tree-focus').click();await expect(page.locator('.bt-picked')).not.toHaveAttribute('data-node-id','root');await expect(page.locator('#npc-tree-node-title')).toBeVisible();
 await page.screenshot({path:resolve(shots,'focused-node-1920.jpg'),type:'jpeg',quality:72});
});
test('English fullscreen fits a narrow viewport and restores the normal route',async({page})=>{
 await page.getByRole('button',{name:'English',exact:true}).click();await page.setViewportSize({width:390,height:844});
 await page.locator('#npc-tree-expand').click();await expect(page.getByRole('dialog',{name:'Behavior tree viewer'})).toBeVisible();
 await page.getByRole('button',{name:'Hide details',exact:true}).click();await page.locator('#npc-tree-full').check();await fitBounds(page);
 const bounds=await page.getByRole('dialog').boundingBox();expect(bounds!.x+bounds!.width).toBeLessThanOrEqual(390);expect(bounds!.y+bounds!.height).toBeLessThanOrEqual(844);
 await page.screenshot({path:resolve(shots,'english-fullscreen-390.jpg'),type:'jpeg',quality:72});
 await page.getByRole('button',{name:'Exit fullscreen',exact:true}).click();await expect(page.getByRole('dialog')).toHaveCount(0);await expect(page.locator('#npc-tree-expand')).toBeFocused();
});
