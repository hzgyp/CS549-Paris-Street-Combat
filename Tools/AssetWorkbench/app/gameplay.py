"""Validated, read-only gameplay navigation. Documents remain the design authority."""
import copy
import re
from .security import WorkbenchError, relative_path, sha

KINDS={'mechanic','mission','route','presentation'}
DESIGN_STATES={'confirmed','review','reference'}
IMPLEMENTATION_STATES={'formal','unimplemented','diagnostic'}
VALIDATION_STATES={'scoped_verified','survey_only','pending','failed_fixed_routes'}


def validate(data, asset_ids):
    def reject(message):raise WorkbenchError('GAMEPLAY_SCHEMA_INVALID',message,422)
    def bilingual(value):
        return isinstance(value,dict) and all(isinstance(value.get(k),str) and value[k].strip() for k in ('zh','en'))
    rows=data.get('entries',[]) if isinstance(data,dict) else []
    if not isinstance(data,dict) or data.get('schema_version')!=1 or not isinstance(rows,list):reject('玩法登记格式不支持')
    ids=set()
    for row in rows:
        if not isinstance(row,dict) or not isinstance(row.get('id'),str) or not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,79}',row['id']) or row['id'] in ids:reject('玩法ID无效或重复')
        ids.add(row['id'])
        if row.get('kind') not in KINDS or row.get('design_state') not in DESIGN_STATES:reject('玩法分类或设计状态无效')
        if not isinstance(row.get('implementation'),dict) or not isinstance(row.get('validation'),dict):reject('实现或验证格式无效')
        if row['implementation'].get('state') not in IMPLEMENTATION_STATES or row['validation'].get('state') not in VALIDATION_STATES:reject('实现或验证状态无效')
        for field in ('title','summary'):
            if not bilingual(row.get(field)):reject('玩法文本需要中英文：'+field)
        if not isinstance(row.get('asset_ids'),list) or any(not isinstance(a,str) or a not in asset_ids for a in row['asset_ids']):reject('玩法引用了未知资产')
        if not isinstance(row.get('media_ids',[]),list) or any(not isinstance(a,str) for a in row.get('media_ids',[])):reject('玩法图片引用无效')
        if row['implementation'].get('build_id') is not None and not isinstance(row['implementation']['build_id'],str):reject('玩法构建引用无效')
        for field in ('rules','steps','open_items'):
            if not isinstance(row.get(field,[]),list) or not all(bilingual(x) for x in row.get(field,[])):reject('玩法条目需要中英文：'+field)
        if not isinstance(row.get('documents'),list):reject('玩法来源格式无效')
        for doc in row['documents']:
            if not isinstance(doc,dict) or not isinstance(doc.get('path'),str):reject('玩法来源路径无效')
            p=relative_path(doc.get('path',''))
            if not p.startswith(('Docs/Development/','Failures/')) or not p.endswith('.md') or not bilingual(doc.get('title')):reject('玩法来源必须是登记的开发文档')
        if not row.get('documents'):reject('玩法没有来源文档')
        if not bilingual(row['implementation'].get('note')) or not bilingual(row['validation'].get('note')):reject('玩法状态需要范围说明')
        if not isinstance(row.get('locations',[]),list) or not isinstance(row.get('related_ids',[]),list):reject('玩法地点或关联格式无效')
        for point in row.get('locations',[]):
            if not isinstance(point,dict):reject('玩法地点格式无效')
            if not isinstance(point.get('foot_xyz_m'),list) or len(point['foot_xyz_m'])!=3 or not all(isinstance(n,(int,float)) and not isinstance(n,bool) and abs(n)<10000 for n in point['foot_xyz_m']):reject('玩法地点坐标无效')
            if not bilingual(point.get('note')):reject('玩法地点需要范围说明')
    for row in rows:
        if any(not isinstance(x,str) or x not in ids for x in row.get('related_ids',[])):reject('玩法关联ID不存在')
    return rows


def collect(importer, path):
    raw=importer.doc(path)
    records=validate(raw,{a['id'] for a in importer.entities['assets']})
    builds={b['id']:b for b in importer.entities['builds']}
    media={m['id'] for m in importer.entities['media']}
    for original in records:
        row=copy.deepcopy(original)
        row['source_id']=importer.sources[path]['id']
        for doc in row['documents']:
            content=importer.read(doc['path'])
            doc.update(source_id=importer.sources[doc['path']]['id'],sha256=sha(content),source_changed=bool(doc.get('registered_sha256') and doc['registered_sha256']!=sha(content)))
        row['source_changed']=any(d['source_changed'] for d in row['documents'])
        row['media_ids']=[mid for mid in row.get('media_ids',[]) if mid in media]
        implementation=row['implementation']
        build_id=implementation.get('build_id')
        if build_id:
            if build_id not in builds:raise WorkbenchError('GAMEPLAY_SCHEMA_INVALID','玩法构建引用不存在',422)
            b=builds[build_id]
            implementation.update(build_title=b['title'],revision=b['revision'],game_sha256=b['game_sha256'],build_status=b['status'])
            if implementation['state']=='formal' and b['channel']!='formal':raise WorkbenchError('GAMEPLAY_SCHEMA_INVALID','正式玩法不能引用候选构建',422)
        elif implementation['state']=='formal':raise WorkbenchError('GAMEPLAY_SCHEMA_INVALID','正式玩法缺少构建依据',422)
        importer.entities['gameplay'].append(row)
