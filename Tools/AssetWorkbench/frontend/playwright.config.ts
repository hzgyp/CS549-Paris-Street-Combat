import { defineConfig } from '@playwright/test';
import {readFileSync} from 'node:fs';
import {resolve} from 'node:path';
const state=resolve(process.cwd(),'../../../Assets/LocalWorking/AssetWorkbench');
const session=JSON.parse(readFileSync(resolve(state,'runtime/session.json'),'utf8'));
export default defineConfig({testDir:'./tests',workers:1,timeout:60000,retries:0,reporter:[['list'],['json',{outputFile:resolve(state,'runs/ui-results.json')}]],use:{baseURL:`http://127.0.0.1:${session.port}`,channel:'chrome',headless:true,viewport:{width:1920,height:1080},screenshot:'only-on-failure'}});
