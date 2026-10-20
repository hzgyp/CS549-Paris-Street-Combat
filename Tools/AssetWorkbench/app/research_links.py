"""Explicit research associations. No keyword or asset-family inference."""
import json
from .security import WorkbenchError

RELATIONS = {'context', 'visual', 'identity_check', 'adaptation', 'comparison'}


def associate(entries, data, asset_ids=None, gameplay_ids=None):
    def reject(message):
        raise WorkbenchError('RESEARCH_ASSOCIATION_INVALID', message, 422)
    if not isinstance(data, dict) or data.get('schema_version') != 1 or not isinstance(data.get('groups'), list):
        reject('历史关联登记格式无效')
    by_key = {(r['register'], r['key']): r for r in entries}
    groups, edges = set(), set()
    for row in entries:
        row['asset_links'] = []
        row['gameplay_links'] = []
        row['gameplay_ids'] = []
    for group in data['groups']:
        if not isinstance(group, dict) or not isinstance(group.get('id'), str) or not group['id'] or group['id'] in groups:
            reject('历史关联组ID无效或重复')
        groups.add(group['id'])
        note = group.get('note')
        if group.get('relation') not in RELATIONS or not isinstance(note, dict) or any(not isinstance(note.get(k), str) or not note[k].strip() for k in ('zh', 'en')):
            reject('历史关联用途需要类型及中英文说明')
        refs = group.get('references')
        if not isinstance(refs, list) or not refs:
            reject('历史关联缺少精确资料选择器')
        for kind, known in [('asset', asset_ids), ('gameplay', gameplay_ids)]:
            targets = group.get(kind+'_ids', [])
            if not isinstance(targets, list) or any(not isinstance(x, str) or (known is not None and x not in known) for x in targets):
                reject('历史关联目标不存在：'+kind)
        if not group.get('asset_ids') and not group.get('gameplay_ids'):
            reject('历史关联没有目标')
        for selector in refs:
            if not isinstance(selector, dict) or not isinstance(selector.get('register'), str) or not isinstance(selector.get('key'), str):
                reject('历史关联选择器无效')
            row = by_key.get((selector['register'], selector['key']))
            if row is None:
                reject('历史关联资料不存在：'+selector['register']+' | '+selector['key'])
            for kind in ('asset', 'gameplay'):
                for target in group.get(kind+'_ids', []):
                    edge = (row['id'], kind, target)
                    if edge in edges:
                        reject('历史关联边重复：'+target)
                    edges.add(edge)
                    row[kind+'_links'].append(dict(id=target, relation=group['relation'], note=note))
                    if target not in row[kind+'_ids']:
                        row[kind+'_ids'].append(target)
    # Legacy per-note registrations still navigate; explicit groups add purpose.
    for row in entries:
        row['search_text'] += ' '+json.dumps([row['asset_links'], row['gameplay_links']], ensure_ascii=False).casefold()


def references_for(entries, kind, target):
    result = []
    for row in entries:
        if target not in row.get(kind+'_ids', []):
            continue
        item = {k: row.get(k) for k in ('id', 'title', 'scope', 'kind', 'institution', 'date', 'rights', 'limitation', 'links', 'media_id', 'image_access', 'source_id', 'register')}
        text = row.get('body', '')
        item.update(excerpt=text[:1200], has_more=len(text)>1200,
                    association=next((l for l in row.get(kind+'_links', []) if l['id']==target), None))
        result.append(item)
    return result
