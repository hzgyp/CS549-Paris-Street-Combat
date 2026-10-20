"""Curated homepage modules resolved against one immutable catalog snapshot."""
from copy import deepcopy
from urllib.parse import urlencode

from .security import WorkbenchError


MODULES = {'actions': {'武器', '人物', '动画'}, 'characters': {'人物'},
           'scenes': {'地图'}, 'props': {'道具', '武器'}}


def assemble(config, entities):
    def reject(message):raise WorkbenchError('HOMEPAGE_SCHEMA_INVALID', message, 422)
    def bilingual(value):return isinstance(value,dict) and all(isinstance(value.get(k),str) and value[k] for k in ('zh','en'))
    if config.get('schema_version')!=1 or not isinstance(config.get('modules'),list):reject('首页模块格式不支持')
    assets={a['id']:a for a in entities['assets']};revisions={r['id']:r for r in entities['revisions']}
    builds={b['id']:b for b in entities['builds']};media={m['id']:m for m in entities['media']}
    gameplay={g['id']:g for g in entities.get('gameplay',[])}
    release=config.get('release',{});formal=builds.get(release.get('build_id'))
    if not formal or formal['id']!='formal' or formal['channel']!='formal':reject('首页正式版必须引用当前正式选择器')
    if release.get('gameplay_id') not in gameplay:reject('首页玩法引用不存在')
    cover=media.get(release.get('cover_id'))
    if not cover or not cover.get('actual_capture') or not cover.get('game_sha256'):reject('正式版封面缺少真实截图身份')
    if cover.get('asset_id') not in formal['assets']:reject('正式版封面不属于当前版本资产')
    # A later formal selection can refresh safely without presenting an old capture as current.
    matching=cover['game_sha256']==formal['game_sha256']
    if not bilingual(release.get('title')):reject('正式版标题需要中英文')
    output=dict(id='current',release=dict(title=deepcopy(release['title']) if matching else dict(zh=formal['title'],en=formal['title']),version=formal['revision'],
        game_sha256=formal['game_sha256'],build_id=formal['id'],href='/builds/formal',
        gameplay_href='/gameplay/'+release['gameplay_id'],cover_id=cover['id'] if matching else None,
        cover_state='matching_game' if matching else 'not_registered',cover_sha256=cover['sha256'] if matching else None,
        summary=deepcopy(release.get('summary',{})) if matching else dict(zh='当前正式版截图尚未登记。',en='The current release preview is not registered.')),modules=[])
    if not bilingual(output['release']['summary']):reject('正式版简介需要中英文')
    seen=set()
    for module in config['modules']:
        mid=module.get('id')
        if mid not in MODULES or mid in seen or not bilingual(module.get('title')) or not bilingual(module.get('description')):reject('首页模块重复或分类无效')
        seen.add(mid);cards=[];card_ids=set()
        if not isinstance(module.get('cards'),list):reject('首页卡片格式无效')
        for raw in module['cards']:
            if not raw.get('id') or raw['id'] in card_ids:reject('首页卡片ID重复')
            card_ids.add(raw['id']);asset=assets.get(raw.get('asset_id'));picture=media.get(raw.get('cover_id'))
            if not asset or asset['category'] not in MODULES[mid]:reject('首页卡片跨越资产模块')
            if not picture or picture.get('asset_id')!=asset['id']:reject('首页配图未登记或属于其他资产')
            if raw.get('image_fit','contain') not in ('contain','cover'):reject('首页图片显示方式无效')
            if not all(bilingual(raw.get(k)) for k in ('title','description','image_label')):reject('首页卡片需要中英文')
            revision=revisions.get(raw.get('revision_id')) if raw.get('revision_id') else None
            if raw.get('revision_id') and (not revision or revision['asset_id']!=asset['id'] or not revision.get('adoption')):reject('首页采用版本引用无效')
            if mid=='actions' and not revision:reject('动作模块需要明确采用记录')
            # Classification does not convert a usage edge or an action acceptance into model approval.
            adopted=bool(revision)
            used=asset['id'] in formal['assets']
            status='adopted' if adopted else 'current_use' if used else 'registered'
            href='/assets/'+asset['id']
            if mid=='actions':
                previous=revision['adoption'].get('previous_id')
                href='/compare?'+urlencode(dict(asset=asset['id'],left=previous,right=revision['id'])) if previous else href+'?tab=versions'
            cards.append(dict(id=raw['id'],asset_id=asset['id'],revision_id=revision['id'] if revision else None,
                title=deepcopy(raw['title']),description=deepcopy(raw['description']),image_label=deepcopy(raw['image_label']),
                cover_id=picture['id'],cover_sha256=picture['sha256'],image_fit=raw.get('image_fit','contain'),
                href=href,status=status,has_model=bool(asset.get('models')),source_id=revision.get('source_id') if revision else None))
        category=module.get('category')
        if category not in MODULES[mid]:reject('首页分类入口无效')
        output['modules'].append(dict(id=mid,title=deepcopy(module['title']),description=deepcopy(module['description']),
            href='/assets?'+urlencode({'category':category}),cards=cards,
            library_count=sum(a['category']==category for a in assets.values())))
    return output


def collect(importer, path):
    config=importer.doc(path)
    homepage=assemble(config,importer.entities)
    cover=next(m for m in importer.entities['media'] if m['id']==config['release']['cover_id'])
    if not cover.get('source_record'):
        raise WorkbenchError('HOMEPAGE_SCHEMA_INVALID','正式版截图缺少原始记录',422)
    if cover.get('source_record'):
        from .version_reviews import viewpoint_source
        source=cover['source_record']
        if not viewpoint_source(source):raise WorkbenchError('HOMEPAGE_SCHEMA_INVALID','首页截图来源越过登记范围',422)
        importer.view_paths.add(source)
        record=importer.doc(source)
        if record.get('game_sha256')!=cover['game_sha256'] or not any(f.get('sha256')==cover['sha256'] and f.get('size_bytes')==cover['size_bytes'] for f in record.get('frames',[])):
            raise WorkbenchError('HOMEPAGE_SCHEMA_INVALID','首页正式版截图与原始记录不符',422)
        homepage['release']['source_id']=importer.sources[source]['id']
    importer.entities['homepage']=[homepage]
