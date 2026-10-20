"""Bounded local historical research adapter. Source registers remain authoritative."""
import csv
import io
import json
import re
from pathlib import Path
from urllib.parse import urlsplit
from .security import WorkbenchError, read_file, relative_path, safe_path, sha

SCOPES = {'paris', 'background', 'equipment'}
KINDS = {'source', 'image', 'note', 'motion', 'weather'}


def build(root, config, reader=None, asset_ids=None, gameplay_ids=None):
    root = Path(root)
    fingerprints = {}
    def reject(message): raise WorkbenchError('RESEARCH_SCHEMA_INVALID', message, 422)
    def allowed(path):
        p = relative_path(path)
        if not (p.startswith('HistoricalReference/') or
                (p.startswith('Tools/AssetCreation/') and p.endswith('/reference_notes.md')) or
                p in ('Docs/Development/MissionLoopV1/MEDKIT_REAL_REFERENCE_AUDIT_20261017.md',
                      'Docs/Development/MissionLoopV1/MEDKIT_MODEL_IMPLEMENTATION_20261017.md') or
                p.startswith('Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-v1/references/originals/')):
            reject('历史资料路径未登记')
        return p
    def read(path):
        path = allowed(path)
        raw = reader(path) if reader else read_file(root, path, 64*1024**2)
        fingerprints[path] = sha(raw)
        return raw
    def text(path): return read(path).decode('utf-8-sig')
    def csv_rows(path): return list(csv.DictReader(io.StringIO(text(path))))
    def url(value):
        if not value: return ''
        parsed = urlsplit(value)
        if parsed.scheme not in ('https','http') or not parsed.hostname or parsed.username or parsed.password:
            reject('来源链接必须是HTTP(S)')
        return value
    if config.get('schema_version') != 1: reject('历史资料登记版本不支持')
    entries, media = [], []
    def add(row):
        row.setdefault('institution', '')
        row.setdefault('date', '')
        row.setdefault('location', '')
        row.setdefault('rights', '未确认 / Not established')
        row.setdefault('limitation', '')
        row.setdefault('body', '')
        row.setdefault('asset_ids', [])
        row.setdefault('links', [])
        row.setdefault('local_files', [])
        row.setdefault('media_id', None)
        if row['scope'] not in SCOPES or row['kind'] not in KINDS: reject('历史资料分类无效')
        for link in row['links']: link['url'] = url(link['url'])
        row['id'] = 'ref-' + sha((row['register']+'|'+row['key']).encode())[:20]
        row['source_sha256'] = fingerprints[row['register']]
        entries.append(row)
        return row
    def archives(row, paths, base):
        for path in paths:
            path = path.strip()
            if not path: continue
            path = allowed(base+'/'+path)
            exists = safe_path(root, path).is_file()
            row['local_files'].append({'path':path, 'available':exists})
    def image(row, path, expected='', permitted=False):
        path = allowed(path)
        row['image_path'] = path
        row['image_access'] = 'rights_link_only' if not permitted else 'missing'
        if not permitted or not safe_path(root,path).is_file(): return
        raw = read(path)
        if expected and sha(raw) != expected: raise WorkbenchError('RESEARCH_IMAGE_CHANGED','历史图片与原登记哈希不符：'+path)
        from PIL import Image
        with Image.open(io.BytesIO(raw)) as im:
            mime=Image.MIME.get(im.format)
            if mime not in ('image/png','image/jpeg','image/webp') or im.width*im.height>100_000_000: reject('历史图片格式不支持')
            row['dimensions']=[im.width,im.height]
            im.verify()
        row['image_sha256']=sha(raw)
        row['image_access']='preview'
        row['media_id']=row['id']+'-image'
        media.append(dict(id=row['media_id'],path=path,sha256=sha(raw),mime=mime,audience='local_owner',kind='historical reference',label=row['title'],asset_id='',rights=row['rights']))
    for spec in config.get('registers',[]):
        path=allowed(spec['path']); kind=spec['adapter']; scope=spec['scope']
        if scope not in SCOPES: reject('历史资料适用背景无效')
        selected=spec.get('include_keys')
        if selected is not None and (not isinstance(selected,list) or not selected or any(not isinstance(k,str) or not k for k in selected) or len(set(selected))!=len(selected)):
            reject('资料保留选择器必须是不重复的精确键')
        found=set()
        for n,item in enumerate(csv_rows(path)):
            key=item.get('id') or item.get('file') or str(n)
            if selected is not None and key not in selected: continue
            found.add(key)
            if kind=='paris_sources':
                add(dict(register=path,key=key,scope=scope,kind='source',title=item['title'],institution=item['institution'],date=item['date_scope'],body=item['use'],limitation=item['limitation'],links=[{'title':'来源 / Source','url':item['url']}]))
            elif kind=='paris_images':
                add(dict(register=path,key=key,scope=scope,kind='image',title=item['subject'],date=item['event_date'],location=item['location'],rights=item['rights_status'],limitation=item['handling'],links=[{'title':'来源 / Source','url':item['url']}],image_access='rights_link_only'))
            elif kind=='sources':
                row=add(dict(register=path,key=key,scope=scope,kind='source',title=item['title'],institution=item['publisher'],date=item['date'],limitation=item['caveat'],links=[{'title':'来源 / Source','url':item['url']}]))
                archives(row,item.get('local_file','').split(';'),str(Path(path).parent.parent).replace('\\','/'))
            elif kind=='images':
                source=item['source']
                if not source.startswith('http') and not re.fullmatch(r'S\d+',source): reject('图片来源必须是HTTP(S)链接或登记来源ID')
                row=add(dict(register=path,key=key,scope=scope,kind='image',title=item['title'],date=item['date'],location=item['scope'],institution=source,rights=item['rights'],limitation=item['note'],body=item['locator'],links=[{'title':'来源 / Source','url':source}] if source.startswith('http') else []))
                rights=item['rights'].casefold()
                image(row,str(Path(path).parent.parent/ item['file']).replace('\\','/'),item['sha256'],any(term in rights for term in ('public domain','public-domain','government material','government work')))
            elif kind=='motion':
                add(dict(register=path,key=key,scope=scope,kind='motion',title=item['work']+' — '+item['source_kind'],date=item['work_year'],institution=item['source_id'],body=item['locator']+'; '+item['review_status'],limitation=item['limitation'],links=[{'title':'来源 / Source','url':item['url']}]))
            elif kind=='weather':
                add(dict(register=path,key=key,scope=scope,kind='weather',title=item['variable']+' — '+item['date'],date=item['date'],location=item['location'],institution=item['source'],body=json.dumps(item,ensure_ascii=False),limitation=item['note']))
            else: reject('历史资料适配器未知')
        if selected is not None and found!=set(selected): reject('保留资料选择器不存在：'+path)
    for spec in config.get('notes',[]):
        paths=[]
        if 'path' in spec: paths=[allowed(spec['path'])]
        else:
            directory=allowed(spec['directory']+'/README.md').rsplit('/',1)[0]
            paths=[p.relative_to(root).as_posix() for p in safe_path(root,directory).glob('*.md') if p.name!='AGENTS.md']
        for path in sorted(paths):
            body=text(path)
            title=next((line.lstrip('# ').strip() for line in body.splitlines() if line.startswith('# ')),Path(path).stem)
            if spec.get('section_heading'):
                section=re.search(r'^## '+re.escape(spec['section_heading'])+r'\r?\n(.*?)(?=^## |\Z)',body,re.M|re.S)
                if not section: reject('登记研究章节不存在：'+path)
                body=section.group(1).strip();title=spec.get('title',title)
            links=[{'title':u,'url':u} for u in dict.fromkeys(re.findall(r'https?://[^\s<>"\)]+',body))]
            add(dict(register=path,key='document',scope=spec['scope'],kind='note',title=title,body=body,links=links,date=spec.get('date',''),asset_ids=spec.get('asset_ids',[]),limitation=spec.get('limitation','原文研究记录；不等于资产采用或运行验收。 / Research notes; not asset adoption or runtime acceptance.')))
            if path=='HistoricalReference/NormandyContext/SOURCES.md':
                known={r['key'] for r in entries if r['kind']=='source' and r['scope']==spec['scope']}
                for match in re.finditer(r'^## (S\d+) [—-] ([^\r\n]+)\r?\n(.*?)(?=^## |\Z)',body,re.M|re.S):
                    key,title,section=match.groups()
                    if key in known: continue
                    urls=list(dict.fromkeys(re.findall(r'https?://[^\s<>"\)]+',section)))
                    add(dict(register=path,key=key,scope=spec['scope'],kind='source',title=title.strip(),institution=section.strip().splitlines()[0],body=section.strip(),limitation=spec.get('limitation',''),links=[{'title':'来源 / Source','url':u} for u in urls]))
    for spec in config.get('images',[]):
        if spec['register'] not in fingerprints: text(spec['register'])
        row=add(dict(register=spec['register'],key=spec['path'],scope=spec['scope'],kind='image',title=spec['title'],institution=spec['institution'],date=spec.get('date',''),rights=spec['rights'],limitation=spec['limitation'],asset_ids=spec.get('asset_ids',[]),links=[{'title':'来源 / Source','url':spec['url']}]))
        image(row,spec['path'],spec['sha256'],spec.get('display_basis') in ('CC0','US_GOVERNMENT_PUBLIC_DOMAIN'))
    if len({r['id'] for r in entries})!=len(entries): reject('历史资料身份重复')
    active_scopes=config.get('allowed_scopes',list(SCOPES))
    if not isinstance(active_scopes,list) or not active_scopes or any(s not in SCOPES for s in active_scopes) or any(r['scope'] not in active_scopes for r in entries): reject('资料不在当前平台允许背景内')
    # Resolve institutional source IDs without discarding the original locator.
    sources={r['key']:r for r in entries if r['kind']=='source'}
    for row in entries:
        source=sources.get(row['institution'])
        if source:
            row['institution']=source['institution']; row['links']=row['links'] or source['links']
        original=json.dumps(row,ensure_ascii=False).casefold()
        vocabulary={'barricad':'街垒 路障','paris':'巴黎 解放','omaha':'奥马哈 诺曼底','normandy':'诺曼底','uniform':'制服 军服','rank':'军衔','rifle':'步枪 枪械','kar98':'步枪 卡尔 毛瑟','grenade':'手雷 烟雾弹','mine':'地雷','medical':'医疗 急救包','medic':'医疗 急救包','canvas':'帆布','weather':'天气 气象','tank':'坦克 装甲','aircraft':'飞机','landing craft':'登陆艇','motion':'动作','ammunition':'弹药','weapon':'武器','liberation':'解放','insignia':'徽章 军衔','film':'电影 影视'}
        row['tags']=list(dict.fromkeys(v for k,v in vocabulary.items() if re.search(r'(?<![a-z])'+re.escape(k)+(r'[a-z]*\b' if k in ('barricad','kar98') else r'(?:s|es)?(?![a-z])'),original)))
        row['search_text']=original+' '+' '.join(row['tags'])
    if config.get('associations'):
        path = config['associations']
        if path != 'Assets/Registry/research/associations.json': reject('历史关联登记路径无效')
        raw = reader(path) if reader else read_file(root, path, 4*1024**2)
        fingerprints[path] = sha(raw)
        from .research_links import associate
        associate(entries, json.loads(raw.decode('utf-8-sig')), asset_ids, gameplay_ids)
    return entries, media, fingerprints


def collect(importer, path):
    from .catalog import identity
    config=importer.doc(path)
    def registered_read(p):
        importer.research_paths.add(p)
        return importer.read(p)
    known={a['id'] for a in importer.entities['assets']}
    entries, media, _=build(importer.root,config,registered_read,known,{g['id'] for g in importer.entities['gameplay']})
    for row in entries:
        if any(a not in known for a in row['asset_ids']): raise WorkbenchError('RESEARCH_SCHEMA_INVALID','历史资料关联资产不存在',422)
        row['source_id']=identity(row['register'])
    importer.entities['research']=entries
    importer.entities['media'].extend(media)
