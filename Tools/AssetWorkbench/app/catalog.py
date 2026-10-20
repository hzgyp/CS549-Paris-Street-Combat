from __future__ import annotations

import json
import subprocess
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from .security import WorkbenchError, read_file, relative_path, sha


def now():
    return datetime.now(timezone.utc).isoformat()


def identity(*parts):
    return sha(json.dumps(parts, ensure_ascii=False).encode())[:24]


def result_state(data, expected_mode=None):
    status = str(data.get('status', '')).lower()
    reason = str(data.get('reason', ''))
    if 'unknown_check_mode' in reason or 'unknown_check_mode' in status:
        return 'fixture_error'
    if status.startswith('fail'):
        return 'fail'
    if expected_mode and data.get('mode') and data['mode'] != expected_mode:
        return 'fixture_error'
    if status == 'pass' or status.startswith('pass_'):
        return 'pass' if (data.get('reason') or data.get('scope')) else 'incomplete'
    return 'incomplete' if not status else 'unassessed'


class Importer:
    def __init__(self, root: Path, store, cancelled=lambda: False):
        self.root, self.store, self.cancelled = root.resolve(), store, cancelled
        self.sources, self.entities, self.files = {}, {k: [] for k in ['assets','revisions','builds','bundles','evidence','sources','media','templates','issues','usage','recovery','models','gameplay']}, []
        self.code_paths = {}
        self.file_identities = {}
        self.research_paths = set()
        self.view_paths = set()
        self.issue_identities = {}

    def issue(self, code, message, subject='', severity='warning'):
        key = identity(code,subject,message)
        if key in self.issue_identities:
            if severity == 'error':
                self.issue_identities[key]['severity'] = 'error'
            return
        item = dict(id=key, code=code, message=message, subject_id=subject, severity=severity)
        self.issue_identities[key] = item
        self.entities['issues'].append(item)

    def read(self, path, expected=None, optional=False):
        if self.cancelled():
            raise WorkbenchError('CANCELLED', '任务已取消')
        relative_path(path)
        permitted = (
            path in self.code_paths or path in self.research_paths or path in self.view_paths
            or
            (path.startswith(('Assets/Registry/', 'Assets/Sync/', 'Docs/Development/', 'Failures/')) and Path(path).suffix in ('.json', '.md'))
            or path in ('Assets/ASSET_REGISTER.csv','Assets/XIAN_YU_ASSET_CATALOG_20261003_ZH.md','Assets/TEAM_SYNC_WORKFLOW.md',
                        'Assets/LocalWorking/AssetWorkbench/private-records/media.json',
                        'Assets/LocalWorking/AssetWorkbench/private-records/models.json',
                        'Assets/LocalWorking/Experiments/PressureMine/20261011-v1/ASSET_REVIEW.json')
            or (path.startswith('Unreal/Variants/') and path.endswith('/SOURCE_MANIFEST.json'))
            or (path.startswith('tmp/g1-') and '/checks/' in path and Path(path).name in ('RESULT.json','VISUAL_REVIEW.json'))
        )
        if not permitted:
            raise WorkbenchError('PATH_NOT_REGISTERED', '元数据引用越过登记来源范围', 403)
        if path in self.sources:
            raw = self.sources[path]['raw']
        else:
            try:
                raw = read_file(self.root, path)
            except (OSError, WorkbenchError) as e:
                if not optional:
                    raise WorkbenchError('SOURCE_UNAVAILABLE', f'必需来源不可读：{path}') from e
                self.issue('SOURCE_UNAVAILABLE', f'来源缺失或未获准访问：{path}', path)
                return None
            self.sources[path] = dict(raw=raw, sha256=sha(raw), id=identity(path))
        if expected and sha(raw) != expected:
            raise WorkbenchError('MANIFEST_HASH_MISMATCH', f'固定来源哈希不匹配：{path}')
        if path in self.code_paths and sha(raw) != self.code_paths[path]:
            raise WorkbenchError('MANIFEST_HASH_MISMATCH', f'固定源码哈希不匹配：{path}')
        return raw

    def doc(self, path, expected=None, optional=False):
        raw = self.read(path, expected, optional)
        if raw is None:
            return None
        try:
            return json.loads(raw.decode('utf-8-sig'))
        except (ValueError, UnicodeError) as e:
            raise WorkbenchError('SOURCE_SCHEMA_UNSUPPORTED', f'无法解析JSON：{path}') from e

    def file_rows(self, bundle, rows, prefix=''):
        seen = set()
        for x in rows:
            p = relative_path(prefix + x['path'])
            if p in seen or not isinstance(x.get('size_bytes'), int) or x['size_bytes'] < 0 or len(x.get('sha256', '')) != 64 or any(c not in '0123456789abcdef' for c in x['sha256']):
                raise WorkbenchError('SOURCE_SCHEMA_UNSUPPORTED', f'重复路径或无效文件身份：{p}')
            seen.add(p)
            row=dict(bundle=bundle, path=p, sha256=x['sha256'], size_bytes=x['size_bytes'], storage=x.get('storage','local'), availability='declared_remote' if x.get('storage')=='sftp' else 'not_checked')
            key=(bundle,p)
            if key in self.file_identities:
                if self.file_identities[key]!=row:
                    raise WorkbenchError('SOURCE_SCHEMA_UNSUPPORTED',f'同一文件组路径身份冲突：{p}')
                continue
            self.file_identities[key]=row
            self.files.append(row)

    def build(self, item):
        d = self.doc(item['path'], optional=item.get('optional',False))
        if d is None:
            return
        if d.get('schema_version',1) not in (1,2,3) or not d.get('source_manifest') or not d.get('game_sha256'):
            raise WorkbenchError('SOURCE_SCHEMA_UNSUPPORTED', '不支持的构建选择器')
        source = self.doc(d['source_manifest'], d.get('source_manifest_sha256'))
        source_id = identity(d['source_manifest'], self.sources[d['source_manifest']]['sha256'])
        snapshot=d.get('source_snapshot') or d.get('source_project')
        if not isinstance(snapshot,str) or not snapshot:
            raise WorkbenchError('SOURCE_SCHEMA_UNSUPPORTED','构建选择器缺少源码目录')
        relative_path(snapshot)
        self.file_rows(source_id, source['files'], snapshot.rstrip('/')+'/')
        for f in source['files']:
            if Path(f['path']).suffix in ('.cpp','.h','.inl','.json','.ini'):
                self.code_paths[snapshot.rstrip('/')+'/'+f['path']]=f['sha256']
        build = dict(id=item['id'], channel=item['channel'], title=item['title'], revision=d.get('revision', d.get('baseline_id',d.get('selected_build'))), game_sha256=d['game_sha256'], source_manifest_sha256=d.get('source_manifest_sha256'), source_files=len(source['files']), source_id=identity(item['path']), manifest_source_id=identity(d['source_manifest']), source_bundle=source_id, status=d['status'], entry=d.get('playable_entry'), native_anchor=d.get('native_asset_anchor'), human_review=d.get('human_manual_review',d.get('human_review','待人工选定')), assets=item['assets'], scope='选择器记录；不代表本次重新运行游戏', source_snapshot=snapshot)
        self.entities['builds'].append(build)
        for asset in item['assets']:
            self.entities['usage'].append(dict(id=identity(build['id'],asset), build_id=build['id'], asset_id=asset, basis='documented_binding', source_id=identity(item['path']), completeness='curated_family_mapping', label='文档／选择器关联，未执行新运行扫描'))
        checks=d.get('checks',[])
        if isinstance(checks,str):
            build['checks_record']=relative_path(checks)
            checks=[]  # A record path is not a list of individually verified results.
        if not isinstance(checks,list):
            raise WorkbenchError('SOURCE_SCHEMA_UNSUPPORTED','构建检查格式不支持')
        for check in checks:
            p = check.get('result')
            if not p:
                continue
            ev_id=identity(item['id'],p)
            raw = self.read(p, optional=True)
            state, reason = 'unassessed', '原始结果不可访问'
            if raw is not None:
                if check.get('result_sha256') and sha(raw)!=check['result_sha256']:
                    state, reason='fail','结果字节不匹配登记哈希'
                    self.issue('EVIDENCE_HASH_MISMATCH',reason,ev_id)
                else:
                    try:
                        result=json.loads(raw.decode('utf-8-sig'))
                        state=result_state(result,check.get('mode')); reason=result.get('reason','未记录原因')
                        if result.get('game_sha256',d['game_sha256'])!=d['game_sha256'] or check.get('game_sha256',d['game_sha256'])!=d['game_sha256']:
                            state,reason='unassessed','结果与选择器Game身份不同，不能当作当前通过'
                        elif state=='pass' and check.get('inherited_unchanged_scope'):
                            state='inherited'
                    except (ValueError,TypeError):
                        state,reason='incomplete','结果格式不支持'
            self.entities['evidence'].append(dict(id=ev_id,title=check.get('mode','检查'),result=state,summary=reason,scope=check.get('scope','原结果限定范围；不是本次实跑'),build_id=item['id'],asset_ids=item['assets'],source_id=identity(p) if raw else None,source_sha256=sha(raw) if raw else None,game_sha256=d['game_sha256'],identity_strength='selector_pinned_result' if check.get('result_sha256') else 'partial',media_ids=[]))
        if d.get('retirement_map'):
            recovery=self.doc(d['retirement_map'],optional=True)
            if recovery:
                self.entities['recovery'].append(dict(id=identity(d['retirement_map']),source_id=identity(d['retirement_map']),count=len(recovery.get('files',[])),scope=recovery.get('scope'),availability='recoverable_not_verified',files=recovery.get('files',[])))

    def collect(self):
        started=time.perf_counter()
        registry=self.doc('Assets/Registry/registry.json')
        if registry.get('schema_version') != 1:
            raise WorkbenchError('SOURCE_SCHEMA_UNSUPPORTED','registry schema版本不支持')
        catalog=self.doc(registry['catalog'])
        if catalog.get('schema_version') != 1:
            raise WorkbenchError('SOURCE_SCHEMA_UNSUPPORTED','Catalog schema版本不支持')
        manifests={}
        restore={}
        for active in catalog['active_manifests']:
            d=self.doc(active['path'],active['sha256'])
            if d.get('schema_version')!=1 or d.get('asset_id')!=active['asset_id'] or d.get('asset_version')!=active['asset_version']:
                raise WorkbenchError('SOURCE_SCHEMA_UNSUPPORTED','manifest与Catalog身份不符')
            bid=d['asset_id']; manifests[bid]=d
            self.file_rows(bid,d['files'])
            self.entities['bundles'].append(dict(id=bid,name=bid,version=d['asset_version'],manifest_sha256=active['sha256'],source_id=identity(active['path']),file_count=len(d['files']),size_bytes=sum(x['size_bytes'] for x in d['files']),rights=d.get('sharing_status','unknown'),rights_source=d.get('license_record'),owner=d.get('owner','未登记'),dependencies=d.get('dependencies',[]),verification=d.get('verification',{}),availability='recorded_published',scope=d.get('scope','以原清单为准')))
            for f in d['files']:
                p=f['path'].replace('\\','/').casefold()
                if p in restore and restore[p]!=f['sha256']:
                    raise WorkbenchError('RESTORE_PATH_CONFLICT',f'选定清单恢复路径冲突：{f["path"]}')
                restore[p]=f['sha256']
        for b in self.entities['bundles']:
            for dep in b['dependencies']:
                did=dep if isinstance(dep,str) else dep.get('asset_id')
                if did not in manifests:
                    self.issue('DEPENDENCY_UNRESOLVED','依赖未被本次Catalog解析：'+str(did),b['id'],'error')
        for source in registry.get('documents',[]):
            self.read(source,optional=True)
        for item in registry['selectors']:
            self.build(item)
        published=manifests.get('paris-g1-packaged-playtest')
        if published:
            self.entities['builds'].append(dict(id='published',channel='published',title='团队已发布包',revision=published['asset_version'],game_sha256=published.get('game_sha256'),source_manifest_sha256=published.get('source_manifest_sha256'),source_files=None,source_id=next(b['source_id'] for b in self.entities['bundles'] if b['id']=='paris-g1-packaged-playtest'),status='recorded_published',human_review='历史发布记录',assets=['german-soldier','allied-soldier','first-person','recorded-audio','german-rifle','paris-city'],scope='读取发布记录；未重新下载核验',source_bundle='paris-g1-packaged-playtest'))
            for aid in self.entities['builds'][-1]['assets']:
                self.entities['usage'].append(dict(id=identity('published',aid),build_id='published',asset_id=aid,basis='documented_binding',source_id=self.entities['builds'][-1]['source_id'],completeness='curated_family_mapping',label='已发布包的文档关联'))
        assets=self.doc(registry['assets'])
        extension=self.doc(registry['inventory']) if registry.get('inventory') else {}
        assets['assets'].extend(extension.get('assets',[]))
        ids=[a['id'] for a in assets['assets']]
        if len(ids)!=len(set(ids)):
            raise WorkbenchError('SOURCE_SCHEMA_UNSUPPORTED','重复逻辑资产身份')
        for build in self.entities['builds']:
            if not build.get('source_snapshot'):continue
            for rule in extension.get('usage_rules',[]):
                for path in self.code_paths:
                    if not path.startswith(build['source_snapshot']+'/') or Path(path).name!=rule['filename']:continue
                    raw=self.read(path)
                    lines=raw.decode('utf-8-sig').splitlines()
                    matches=[dict(line=i+1,text=line[:1600]) for i,line in enumerate(lines) if rule['needle'] in line]
                    if matches:
                        self.entities['usage'].append(dict(id=identity(build['id'],rule['asset_id'],path),build_id=build['id'],asset_id=rule['asset_id'],basis='pinned_source_reference',label=rule['label'],source_id=identity(path),source_sha256=sha(raw),matches=matches,completeness='source_reference_only'))
                        if rule['asset_id'] not in build['assets']:build['assets'].append(rule['asset_id'])
        for a in assets['assets']:
            if a.get('inherit_usage_from'):
                for u in list(self.entities['usage']):
                    if u['asset_id']==a['inherit_usage_from']:
                        self.entities['usage'].append(dict(u,id=identity(u['id'],a['id']),asset_id=a['id'],basis='bundle_member',label='运行音频交付成员；具体事件见音频版本说明。'))
                        build=next(b for b in self.entities['builds'] if b['id']==u['build_id'])
                        build['assets'].append(a['id'])
        private=self.doc('Assets/LocalWorking/AssetWorkbench/private-records/media.json',optional=True) or {'files':[]}
        model_path='Assets/LocalWorking/AssetWorkbench/private-records/models.json'
        models=self.doc(model_path,optional=True) if (self.root/model_path).is_file() else {'models':[]}
        for m in (models or {}).get('models',[]):
            relative_path(m['path'])
            if m.get('audience')!='local_owner' or len(m.get('sha256',''))!=64:
                raise WorkbenchError('SOURCE_SCHEMA_UNSUPPORTED','3D预览缺少身份或受众')
            self.entities['models'].append(m)
        media_map={}
        for m in private.get('files',[]):
            if m.get('kind')=='supplier thumbnail':continue
            if m.get('audience')!='local_owner' or not m.get('sha256'):
                self.issue('RIGHTS_NOT_ESTABLISHED','预览没有明确的本机受众许可',m.get('id',''))
                continue
            relative_path(m['path'])
            media_map[m['id']]=m
            self.entities['media'].append(m)
        for entry in assets['assets']:
            a=dict(entry)
            for p in a.get('documents',[]):
                self.read(p,optional=True)
            a.update(extension.get('patches',{}).get(a['id'],{}))
            a['source_id']=identity(registry.get('inventory') if a['id'] in {x['id'] for x in extension.get('assets',[])} else registry['assets'])
            a['members']=extension.get('members',{}).get(a['id'],[])
            a['member_count']=len(a['members'])
            a['sources']=[identity(p) for p in a.pop('documents',[]) if p in self.sources]
            a['build_ids']=[e['build_id'] for e in self.entities['usage'] if e['asset_id']==a['id']]
            a['usage_status']='formal' if 'formal' in a['build_ids'] else 'candidate' if any(b in a['build_ids'] for b in ('ui-review','equipment-review')) else 'source_only' if a.get('usage_hint')=='source_only' else 'unregistered'
            a['media_ids']=[m['id'] for m in private.get('files',[]) if m.get('asset_id')==a['id'] and m['id'] in media_map]
            a['models']=[{k:v for k,v in m.items() if k not in ('path','audience','source_files')} for m in self.entities['models'] if a['id'] in m['asset_ids']]
            a['preview_id']=a['media_ids'][0] if a['media_ids'] else None
            a['preview_label']=media_map[a['preview_id']]['label'] if a['preview_id'] else None
            a['availability']='local_preview' if a['preview_id'] else 'metadata_only'
            a['rights']='private_local' if a['media_ids'] else 'see_source'
            a['revisions']=[]
            for bundle in a.get('bundles',[]):
                if bundle not in manifests: continue
                d=manifests[bundle]
                rid=identity(a['id'],d['asset_version'],next(b['manifest_sha256'] for b in self.entities['bundles'] if b['id']==bundle))
                rev=dict(id=rid,asset_id=a['id'],title=d['asset_version'],kind='bundle_revision',parent_ids=[],file_bundle=bundle,source_id=next(b['source_id'] for b in self.entities['bundles'] if b['id']==bundle),summary=d.get('scope',d.get('source','')),result='recorded',identity_strength='exact_manifest',media_ids=a['media_ids'][:1],metrics=d.get('metrics',{}))
                self.entities['revisions'].append(rev); a['revisions'].append(rid)
            self.entities['assets'].append(a)
        # Curated historical integration records retain their documented scope.
        histories=self.doc(registry['history'])
        if registry.get('inventory_history'):histories['revisions'].extend(self.doc(registry['inventory_history'])['revisions'])
        if registry.get('version_reviews'):
            from .version_reviews import merge
            try:
                histories['revisions']=merge(histories['revisions'],self.doc(registry['version_reviews']))
                self.view_paths = {view['source'] for row in histories['revisions'] for view in row.get('image_views', {}).values()}
            except ValueError as exc:
                raise WorkbenchError('SOURCE_SCHEMA_UNSUPPORTED',str(exc)) from exc
        for h in histories['revisions']:
            if h.get('review') and any(m not in media_map for m in h.get('media_ids',[])):
                raise WorkbenchError('SOURCE_SCHEMA_UNSUPPORTED','版本证据引用了未登记图片')
            h=dict(h); p=h.pop('document'); document=self.read(p,optional=True)
            for view in h.get('image_views', {}).values():
                self.read(view['source'])
                view['source_id']=identity(view['source'])
            if h.get('adoption'):
                authority=h['adoption']['authority']
                self.read(authority)
                h['adoption']['source_id']=identity(authority)
            h['recorded_result']=h['result']
            if document is None:
                h['result']='unassessed'
            h.update(source_id=identity(p),media_ids=[m for m in h.get('media_ids',[]) if m in media_map],identity_strength=h.get('identity_strength','documented'),parent_ids=h.get('parent_ids',[]))
            h['screenshots']=[{k:media_map[m][k] for k in ('id','path','label','sha256','size_bytes') if k in media_map[m]} for m in h['media_ids']]
            if h.get('model_review'):
                model=self.doc(h['model_review'],optional=True)
                if model:
                    model_files=[f for f in model.get('files',[]) if '/finish_v2/' in f['path'] and (Path(f['path']).name.startswith('mine_') or f['path'].endswith(('.blend','.glb')))]
                    h['model_identity']=sha(json.dumps(model_files,sort_keys=True).encode())
                    h['metrics']={'triangles':model.get('triangles'),'textures':model.get('texture')}
            if h.get('result_path'):
                d=self.doc(h['result_path'],optional=True)
                h['raw_result']=result_state(d) if d else 'unassessed'
            self.entities['revisions'].append(h)
            a=next((a for a in self.entities['assets'] if a['id']==h['asset_id']),None)
            if a:a['revisions'].append(h['id'])
            self.entities['evidence'].append(dict(id=identity(h['id'],'evidence'),title=h['title'],result=h['result'],summary=h['summary'],scope=h['scope'],asset_ids=[h['asset_id']],source_id=h['source_id'],identity_strength=h['identity_strength'],media_ids=h['media_ids']))
        templates=self.doc(registry['templates'])
        self.entities['templates']=templates['templates']
        self.issue('HISTORICAL_REGISTER','早期ASSET_REGISTER仍包含待选定人物条目；当前展示以独立选择器和整合记录为准。','asset-register','info')
        self.issue('SEMANTIC_COVERAGE','采购包、武器集合及项目资产按库存登记；源码引用不是运行时扫描，未关联条目不等于已证实未使用。','coverage','info')
        self.issue('LOCAL_ONLY','本机只读模式；远端可用性来自带日期记录，未发起SFTP连接。','publication','info')
        for a in self.entities['assets']:
            if not a['media_ids']:self.issue('PREVIEW_UNAVAILABLE','尚无登记且允许展示的本机预览',a['id'])
        if registry.get('gameplay'):
            from .gameplay import collect
            collect(self,registry['gameplay'])
        if registry.get('research'):
            from .research import collect
            collect(self,registry['research'])
        if registry.get('library_scope'):
            from .library_scope import collect
            collect(self,registry['library_scope'])
        if registry.get('homepage'):
            from .homepage import collect
            collect(self,registry['homepage'])
        for path, source in self.sources.items():
            if sha(read_file(self.root,path))!=source['sha256']:
                raise WorkbenchError('SOURCE_CHANGED_DURING_SCAN','刷新期间来源变化，保留上次有效索引')
            excerpt=source['raw'].decode('utf-8-sig',errors='replace')[:80000] if Path(path).suffix.lower() not in ('.png','.jpg','.jpeg','.webp') else '图片原件；请使用登记预览。 / Image original; use the registered preview.'
            # No private metadata/config source is offered as a general browser.
            self.entities['sources'].append(dict(id=source['id'],path=path,sha256=source['sha256'],size_bytes=len(source['raw']),excerpt=excerpt if not path.startswith('Assets/LocalWorking/AssetWorkbench/') else '本机私有媒体登记，原内容不通过接口公开。'))
        digest=sha(json.dumps(sorted((p,x['sha256']) for p,x in self.sources.items())).encode())
        try: git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=self.root,stderr=subprocess.DEVNULL,text=True).strip()
        except (OSError,subprocess.CalledProcessError):git_head=None
        stats=dict(asset_count=len(self.entities['assets']),bundle_count=len(self.entities['bundles']),file_count=len(self.files),unique_blobs=len({(f['sha256'],f['size_bytes']) for f in self.files}),expected_unique_bytes=sum(size for _,size in {(f['sha256'],f['size_bytes']) for f in self.files}),evidence_count=len(self.entities['evidence']),source_count=len(self.sources),issue_count=len(self.entities['issues']))
        stats['gameplay_count']=len(self.entities['gameplay'])
        stats['research_count']=len(self.entities.get('research',[]))
        snapshot=dict(id=uuid.uuid4().hex,created=now(),digest=digest,git_head=git_head,adapter_version='1.1.0',stats=stats,elapsed_ms=round((time.perf_counter()-started)*1000),source_fingerprints={p:x['sha256'] for p,x in self.sources.items()})
        from asset_index import build, publish
        try:
            navigation=build(self.root)
            for source in navigation['source_fingerprints']:
                if source['path'] in self.sources and source['sha256']!=self.sources[source['path']]['sha256']:
                    raise WorkbenchError('SOURCE_CHANGED_DURING_SCAN','刷新期间来源变化，保留上次有效索引')
            if {a['id'] for a in navigation['assets']}!={a['id'] for a in self.entities['assets']}:
                raise WorkbenchError('SOURCE_CHANGED_DURING_SCAN','刷新期间资产登记变化，保留上次有效索引')
            def research_identity(rows):
                return {(r['id'],r['source_sha256'],r.get('image_sha256'),json.dumps([r.get('asset_links',[]),r.get('gameplay_links',[])],sort_keys=True)) for r in rows}
            if research_identity(navigation.get('research',[]))!=research_identity(self.entities.get('research',[])):
                raise WorkbenchError('SOURCE_CHANGED_DURING_SCAN','刷新期间历史资料变化，保留上次有效索引')
            with publish(self.root,navigation,self.cancelled) as report:
                snapshot['navigation_index']=report
                self.store.publish(snapshot,self.entities,self.files,self.cancelled)
        except WorkbenchError:
            raise
        except Exception as e:
            raise WorkbenchError('NAVIGATION_INDEX_FAILED',f'资产资料索引同步失败：{e}') from e
        return snapshot


def refresh(root,store,cancelled=lambda:False):
    for attempt in range(2):
        try:return Importer(root,store,cancelled).collect()
        except WorkbenchError as e:
            if e.code!='SOURCE_CHANGED_DURING_SCAN' or attempt:raise
