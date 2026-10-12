"""Build/check the metadata index, or search registered assets without running the server."""
import argparse
import hashlib
import json
import os
import sys
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[2]
INDEX = ROOT / 'Assets/Registry/asset-index.json'
TABLE = ROOT / 'Assets/Registry/ASSET_DIRECTORY.md'


def read(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8-sig'))


def build(root=ROOT):
    root = Path(root).resolve()
    captured = {}
    def load(path):
        raw = (root / path).read_bytes()
        captured[path] = hashlib.sha256(raw).hexdigest()
        return json.loads(raw.decode('utf-8-sig'))
    paths = ['Assets/Registry/registry.json']
    reg = load(paths[0])
    paths += [reg[k] for k in ('assets', 'inventory', 'history', 'inventory_history', 'catalog') if reg.get(k)]
    selectors = sorted(p.relative_to(root).as_posix() for p in (root / 'Docs/Development').glob('CURRENT_*.json'))
    paths += selectors
    paths += [s['path'] for s in reg.get('selectors', []) if (root / s['path']).is_file()]
    inventory = load(reg['inventory']) if reg.get('inventory') else {}
    records = [(reg['assets'], a) for a in load(reg['assets'])['assets']]
    records += [(reg.get('inventory'), a) for a in inventory.get('assets', [])]
    revisions = load(reg['history'])['revisions']
    if reg.get('inventory_history'):
        revisions += load(reg['inventory_history'])['revisions']
    manifests = {m['asset_id']: m for m in load(reg['catalog'])['active_manifests']}
    assets = []
    for source, original in records:
        a = {**original, **inventory.get('patches', {}).get(original['id'], {})}
        row = {k: a[k] for k in ('id', 'name', 'name_en', 'category', 'origin', 'description', 'aliases', 'parent_id', 'related_ids', 'documents', 'limitations') if k in a}
        row['registry_source'] = source
        row['member_count'] = len(inventory.get('members', {}).get(a['id'], []))
        row['preview_route'] = '/assets/' + a['id']
        row['revisions'] = [{k: r[k] for k in ('id', 'title', 'result', 'document', 'parent_ids', 'model_identity', 'metrics') if k in r} for r in revisions if r['asset_id'] == a['id']]
        row['manifests'] = [{k: manifests[b][k] for k in ('asset_id', 'asset_version', 'path', 'sha256')} for b in a.get('bundles', []) if b in manifests]
        row['usage_references'] = [{'path': s['path'], 'channel': s['channel'], 'basis': 'registry_family_mapping'} for s in reg.get('selectors', []) if a['id'] in s['assets']]
        row['usage_rules'] = [r for r in inventory.get('usage_rules', []) if r['asset_id'] == a['id']]
        assets.append(row)
    ids = {a['id'] for a in assets}
    if len(ids) != len(assets):
        raise ValueError('Duplicate asset IDs')
    missing = []
    for a in assets:
        for related in ([a['parent_id']] if a.get('parent_id') else []) + a.get('related_ids', []):
            if related not in ids:
                raise ValueError(f'Unknown related asset: {related}')
        for p in a.get('documents', []) + [r['document'] for r in a['revisions'] if r.get('document')] + [m['path'] for m in a['manifests']]:
            if not (root / p).is_file():
                missing.append({'asset_id': a['id'], 'path': p})
        for revision in a['revisions']:
            if revision.get('document') and not (root / revision['document']).is_file():
                revision['recorded_result'] = revision.get('result')
                revision['result'] = 'unassessed'
    for path in dict.fromkeys(paths):
        if path not in captured:
            load(path)
    return {'schema_version': 1, 'scope': 'Metadata navigation; follow current selectors and exact manifests before use.',
            'source_fingerprints': [{'path': p, 'sha256': captured[p]} for p in dict.fromkeys(paths)],
            'current_selectors': selectors, 'missing_references': missing, 'asset_count': len(assets),
            'member_count': sum(a['member_count'] for a in assets), 'assets': assets}


def table(data):
    def cell(x):
        return str(x).replace('|', '\\|').replace('\n', ' ')
    lines = ['# 完整资产目录 / Asset directory', '', '平台刷新时自动生成；不要手工维护。',
             '[统一入口](../ASSET_INDEX.md) · [结构化索引](asset-index.json)', '',
             f"共 {data['asset_count']} 条资产/包，{data['member_count']:,} 条已登记成员。版本、关联、manifest和来源指纹见JSON；当前使用需读最新选择器。", '']
    for category in sorted({a['category'] for a in data['assets']}):
        lines += ['## ' + category, '', '| ID | 名称 / Name | 来源 | 成员 | 资料 |', '| --- | --- | --- | ---: | --- |']
        for a in data['assets']:
            if a['category'] != category:
                continue
            documents = list(dict.fromkeys(a.get('documents', []) + [r['document'] for r in a['revisions'] if r.get('document')]))
            links = ' · '.join(f'[{i+1}](../../{quote(p, safe="/")})' for i, p in enumerate(documents)) or '—'
            name = a['name'] if a.get('name_en') == a['name'] else a['name'] + ' / ' + a.get('name_en', '')
            lines.append(f"| `{a['id']}` | {cell(name)} | {a['origin']} | {a['member_count']} | {links} |")
        lines.append('')
    return '\n'.join(lines) + '\n'


def validate_sources(root, data):
    from app.security import WorkbenchError
    for source in data['source_fingerprints']:
        path = root / source['path']
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != source['sha256']:
            raise WorkbenchError('SOURCE_CHANGED_DURING_SCAN', '刷新期间来源变化，保留上次有效索引')
    selectors = sorted(p.relative_to(root).as_posix() for p in (root / 'Docs/Development').glob('CURRENT_*.json'))
    if selectors != data['current_selectors']:
        raise WorkbenchError('SOURCE_CHANGED_DURING_SCAN', '刷新期间选择器变化，保留上次有效索引')


def atomic_write(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.asset-index-', suffix='.tmp', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


@contextmanager
def publish(root, data, cancelled=lambda: False):
    """Keep old documents until the caller's database publication succeeds."""
    from app.security import WorkbenchError, safe_path
    root = Path(root).resolve()
    lock_path = safe_path(root, 'Assets/LocalWorking/AssetWorkbench/runtime/navigation-index.lock')
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock = lock_path.open('a+b')
    backups = {}
    changed = []
    locked = False
    def check_cancel():
        if cancelled():
            raise WorkbenchError('CANCELLED', '任务已取消')
    try:
        started = time.monotonic()
        if os.name == 'nt':
            import msvcrt
            lock.seek(0); lock.write(b'0'); lock.flush()
        else:
            import fcntl
        while not locked:
            check_cancel()
            try:
                if os.name == 'nt':
                    lock.seek(0); msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                locked = True
            except OSError:
                if time.monotonic() - started > 30:
                    raise WorkbenchError('INDEX_BUSY', '已有索引任务，请等待或取消')
                time.sleep(.05)
        validate_sources(root, data)
        outputs = {'Assets/Registry/asset-index.json': (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode('utf-8'),
                   'Assets/Registry/ASSET_DIRECTORY.md': table(data).encode('utf-8')}
        for relative, raw in outputs.items():
            check_cancel()
            path = safe_path(root, relative)
            backups[path] = path.read_bytes() if path.is_file() else None
            if backups[path] != raw:
                atomic_write(path, raw)
                changed.append(path)
        validate_sources(root, data)
        check_cancel()
        yield {'status': 'synced', 'asset_count': data['asset_count'], 'member_count': data['member_count'],
               'files': [{'path': p, 'sha256': hashlib.sha256(raw).hexdigest()} for p, raw in outputs.items()]}
    except BaseException:
        for path in reversed(changed):
            if backups[path] is None:
                path.unlink(missing_ok=True)
            else:
                atomic_write(path, backups[path])
        raise
    finally:
        if locked and os.name == 'nt':
            lock.seek(0); msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)
        elif locked:
            fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
        lock.close()


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('query', nargs='?', default='')
    parser.add_argument('--build', action='store_true')
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--asset', help='Exact asset ID filter')
    parser.add_argument('--members', action='store_true')
    parser.add_argument('--animations', action='store_true')
    parser.add_argument('--limit', type=int, default=20)
    args = parser.parse_args()
    expected = build()
    if args.build:
        with publish(ROOT, expected):
            pass
        print(f"Built {expected['asset_count']} assets / {expected['member_count']} members")
        return
    if not INDEX.is_file() or read(INDEX) != expected or not TABLE.is_file() or TABLE.read_text(encoding='utf-8') != table(expected):
        raise SystemExit('Index is stale or missing. Use Refresh index in the platform.')
    if args.check:
        print(f"Index current; {expected['asset_count']} unique assets; missing references: {len(expected['missing_references'])}")
        return
    if args.asset and args.asset not in {a['id'] for a in expected['assets']}:
        raise SystemExit('Unknown asset ID: ' + args.asset)
    rows = expected['assets']
    if args.animations:
        path = ROOT / 'Assets/LocalWorking/AssetWorkbench/private-records/animation-packs.json'
        if not path.is_file():
            raise SystemExit('Local animation directory unavailable; see Assets/ASSET_INDEX.md')
        rows = [{'asset_id': p['id'], **c} for p in read(path)['packs'].values() for c in p['clips']]
    elif args.members:
        rows = [{'asset_id': aid, **m} for aid, members in read('Assets/Registry/assets/inventory.json')['members'].items() for m in members]
    matches = [r for r in rows if (not args.asset or r.get('asset_id', r.get('id')) == args.asset) and args.query.casefold() in json.dumps(r, ensure_ascii=False).casefold()]
    print(json.dumps({'total': len(matches), 'shown': min(len(matches), max(0, args.limit)), 'results': matches[:max(0, args.limit)]}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
