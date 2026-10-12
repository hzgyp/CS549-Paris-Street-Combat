import React, {createContext, useContext, useEffect, useState} from 'react';
import {english} from './translations';
import inventoryTranslations from './inventory-translations.json';
Object.assign(english,inventoryTranslations);

export type Locale='zh'|'en';
const storageKey='paris.asset-workbench.locale';
let activeLocale:Locale='zh';
try{activeLocale=localStorage.getItem(storageKey)==='en'?'en':'zh'}catch{/* storage is optional */}
export const currentLocale=()=>activeLocale==='en'?'en-US':'zh-CN';
export type Translate=<T>(value:T)=>T;
const LocaleContext=createContext<{locale:Locale;setLocale:(value:Locale)=>void;tx:Translate}>(null!);

export function translate<T>(value:T,locale:Locale):T {
 if(typeof value!=='string'||locale==='zh')return value;
 const leading=value.match(/^\s*/)?.[0]||'',trailing=value.match(/\s*$/)?.[0]||'';
 const key=value.trim();
 if(key in english)return (leading+english[key]+trailing) as T;
 const count=key.match(/^(\d+) 件资产$/);if(count)return `${count[1]} assets` as T;
 const evidence=key.match(/^证据记录 (\d+)$/);if(evidence)return `Evidence (${evidence[1]})` as T;
 const limit=key.match(/^登记文件约([\d,]+)字节，超过本次([\d,]+)字节限额，尚未启动$/);
 if(limit)return `Bundle size ${limit[1]} bytes exceeds the ${limit[2]} byte limit. Verification not started.` as T;
 const prefix=key.match(/^([^：]+)：(.+)$/);
 if(prefix&&prefix[1] in english)return `${english[prefix[1]]}: ${prefix[2]}` as T;
 // Interpolated image captions retain their record IDs and dates.
 if(key.includes(' · '))return key.split(' · ').map(x=>translate(x,locale)).join(' · ') as T;
 return value;
}

export function LocaleProvider({children}:{children:React.ReactNode}){
 const [locale,setValue]=useState<Locale>(activeLocale);
 const setLocale=(value:Locale)=>{activeLocale=value;setValue(value);try{localStorage.setItem(storageKey,value)}catch{/* preserve session selection */}};
 useEffect(()=>{document.documentElement.lang=locale==='en'?'en':'zh-CN';document.title=locale==='en'?'Paris Asset Workbench':'Paris 资产管理'},[locale]);
 const tx:Translate=value=>translate(value,locale);
 return <LocaleContext.Provider value={{locale,setLocale,tx}}>{children}</LocaleContext.Provider>;
}
export const useLocale=()=>useContext(LocaleContext);
export function LanguageSwitch(){
 const {locale,setLocale}=useLocale();
 return <div className="language-switch" role="group" aria-label="Language / 语言"><button type="button" lang="zh-CN" aria-pressed={locale==='zh'} onClick={()=>setLocale('zh')}>中文</button><button type="button" lang="en" aria-pressed={locale==='en'} onClick={()=>setLocale('en')}>English</button></div>;
}
export function templateText(template:Record<string,any>,tx:Translate){
 return `# ${tx(template.name)}\n\n${tx('模板')} ${template.version} · ${tx(template.policy)}\n\n`+template.fields.map((f:Record<string,any>)=>`## ${tx(f.label)}\n${tx(f.hint)}\n${tx('填写：')}`).join('\n\n');
}
