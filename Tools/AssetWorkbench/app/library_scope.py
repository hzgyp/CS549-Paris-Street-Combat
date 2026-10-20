"""Current library membership without rewriting immutable storage manifests."""
from .security import WorkbenchError, relative_path


def validate(data):
    def reject():raise WorkbenchError('LIBRARY_SCOPE_INVALID','资产库撤下登记无效',422)
    if not isinstance(data,dict) or data.get('schema_version')!=1 or not isinstance(data.get('retired_files'),list):reject()
    seen=set()
    for row in data['retired_files']:
        if not isinstance(row,dict) or any(not isinstance(row.get(k),str) or not row[k] for k in ('bundle','path','sha256','reason')):reject()
        key=(row['bundle'],row['path'])
        relative_path(row['path'])
        if key in seen or len(row['sha256'])!=64 or any(c not in '0123456789abcdef' for c in row['sha256']):reject()
        seen.add(key)
    return data


def collect(importer,path):
    data=validate(importer.doc(path))
    actual={(f['bundle'],f['path']):f for f in importer.files}
    retired=set()
    for row in data['retired_files']:
        key=(row['bundle'],row['path'])
        if key not in actual or actual[key]['sha256']!=row['sha256']:
            raise WorkbenchError('LIBRARY_SCOPE_CHANGED','撤下文件与原清单身份不符；保留上次索引',409)
        retired.add(key)
    # An asset or registered research input cannot be retired by a stale scope file.
    protected=set(importer.research_paths) | set(importer.code_paths)
    for kind in ('models','media'):
        protected.update(r['path'] for r in importer.entities.get(kind,[]) if r.get('path'))
    active_bundles={b for a in importer.entities['assets'] for b in a.get('bundles',[])}
    protected.update(f['path'] for f in importer.files if f['bundle'] in active_bundles)
    for r in importer.entities.get('research',[]):
        protected.update(f['path'] for f in r.get('local_files',[]))
    if any(p in protected for _,p in retired):
        raise WorkbenchError('LIBRARY_SCOPE_IN_USE','撤下文件仍被当前资料引用',409)
    for bundle in importer.entities['bundles']:
        old=[f for f in importer.files if f['bundle']==bundle['id']]
        removed=[f for f in old if (f['bundle'],f['path']) in retired]
        if removed:
            bundle.update(catalog_file_count=bundle['file_count'],catalog_size_bytes=bundle['size_bytes'],retired_file_count=len(removed),
                          file_count=len(old)-len(removed),size_bytes=sum(f['size_bytes'] for f in old if f not in removed),
                          scope='当前项目文件；原始清单与归档保留 / Current-project files; original manifest and archives retained')
    importer.files=[f for f in importer.files if (f['bundle'],f['path']) not in retired]
    importer.entities['bundles']=[b for b in importer.entities['bundles'] if b['file_count']]
