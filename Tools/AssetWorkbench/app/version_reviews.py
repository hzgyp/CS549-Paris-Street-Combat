"""Merge explicit, stable-ID version annotations without promoting old results."""
from copy import deepcopy
from pathlib import PurePosixPath


def viewpoint_source(path):
    """Only registered capture recipes/review records may supply view evidence."""
    if not isinstance(path, str) or '\\' in path or ':' in path:
        return False
    parts = PurePosixPath(path).parts
    if not parts or path.startswith('/') or '..' in parts:
        return False
    return (
        path.startswith(('Tools/Modeling/', 'Tools/Integration/')) and path.endswith('.py')
        or path.startswith(('Docs/Development/', 'Failures/')) and PurePosixPath(path).suffix in ('.json', '.md')
        or path.startswith('tmp/g1-') and PurePosixPath(path).name in ('VISUAL_REVIEW.json', 'RESULT.json')
    )


def review_state(row):
    """A successful technical check is not a human decision."""
    result = row.get('result', '').lower()
    if 'reject' in result or 'fail' in result or result == 'fixture_error':
        return 'not_passed'
    if row.get('review', {}).get('basis') == 'human' and result in ('pass', 'accepted_with_limits'):
        return 'human_approved'
    return 'pending'


def merge(revisions, register):
    rows = deepcopy(revisions) + deepcopy(register.get('revisions', []))
    ids = [r['id'] for r in rows]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate version ID')
    overrides = register.get('annotations', {})
    if set(overrides) - set(ids):
        raise ValueError('Unknown version annotation ID')
    for row in rows:
        annotation = overrides.get(row['id'], {})
        if set(annotation) - {'review', 'media_ids', 'title_en'}:
            raise ValueError('Version annotation cannot change identity or result')
        row.update(annotation)
        if row.get('review'):
            review = row['review']
            if review.get('basis') not in ('human', 'technical', 'recorded', 'pending'):
                raise ValueError('Invalid version decision basis')
            for key in ('problem', 'changes', 'decision'):
                if not all(review.get(key, {}).get(lang) for lang in ('zh', 'en')):
                    raise ValueError('Missing bilingual version decision field')
        row['review_state'] = review_state(row)
    views = register.get('image_views', {})
    media_ids = {m for row in rows for m in row.get('media_ids', [])}
    if set(views) - media_ids:
        raise ValueError('Unknown viewpoint image ID')
    for view in views.values():
        if not isinstance(view, dict) or not isinstance(view.get('key'), str) or not view['key']:
            raise ValueError('Missing viewpoint identity')
        if view.get('basis') not in ('capture_recipe', 'capture_record', 'visual_review') or not view.get('source'):
            raise ValueError('Missing viewpoint provenance')
        if not viewpoint_source(view['source']):
            raise ValueError('Invalid viewpoint provenance path')
        if not all(isinstance(view.get('label', {}).get(lang), str) and view['label'][lang] for lang in ('zh', 'en')):
            raise ValueError('Missing bilingual viewpoint label')
    for row in rows:
        row_views = {m: deepcopy(views[m]) for m in row.get('media_ids', []) if m in views}
        keys = [v['key'] for v in row_views.values()]
        if len(keys) != len(set(keys)):
            raise ValueError('Ambiguous duplicate viewpoint in revision')
        if row_views:
            row['image_views'] = row_views
    by_id = {r['id']: r for r in rows}
    primary_assets, selected = set(), set()
    for selection in register.get('selections', []):
        current = by_id.get(selection.get('current_id'))
        previous = by_id.get(selection.get('previous_id'))
        if not current or current['asset_id'] != selection.get('asset_id'):
            raise ValueError('Unknown or cross-asset adopted version')
        if current['id'] in selected or current['review_state'] == 'not_passed':
            raise ValueError('Duplicate or rejected adopted version')
        if selection.get('previous_id') and (not previous or previous['asset_id'] != current['asset_id'] or previous['id'] == current['id']):
            raise ValueError('Invalid comparison predecessor')
        if not selection.get('authority') or not all(selection.get('scope', {}).get(lang) for lang in ('zh', 'en')):
            raise ValueError('Missing adoption authority or bilingual scope')
        primary = current['asset_id'] not in primary_assets
        current['adoption'] = {k: deepcopy(selection.get(k)) for k in ('previous_id', 'authority', 'scope')}
        current['adoption']['primary'] = primary
        selected.add(current['id'])
        primary_assets.add(current['asset_id'])
    return rows
