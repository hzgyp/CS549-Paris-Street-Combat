from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from .security import WorkbenchError


class Store:
    def __init__(self, path: Path):
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.executescript('''
                PRAGMA journal_mode=DELETE;
                CREATE TABLE IF NOT EXISTS snapshots(id TEXT PRIMARY KEY, created TEXT NOT NULL, digest TEXT NOT NULL, info TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS state(key TEXT PRIMARY KEY, value TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS entities(snapshot TEXT NOT NULL REFERENCES snapshots(id), kind TEXT NOT NULL, id TEXT NOT NULL, data TEXT NOT NULL, PRIMARY KEY(snapshot,kind,id));
                CREATE TABLE IF NOT EXISTS files(snapshot TEXT NOT NULL REFERENCES snapshots(id), bundle TEXT NOT NULL, path TEXT NOT NULL, sha TEXT NOT NULL, size INTEGER NOT NULL, data TEXT NOT NULL, PRIMARY KEY(snapshot,bundle,path));
                CREATE INDEX IF NOT EXISTS files_by_hash ON files(snapshot,sha,size);
                CREATE INDEX IF NOT EXISTS files_by_path ON files(snapshot,path);
                CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY, data TEXT NOT NULL);
            ''')
            for row in db.execute('SELECT id,data FROM jobs').fetchall():
                job = json.loads(row['data'])
                if job['status'] in ('queued', 'running'):
                    job.update(status='failed', error='上次进程中断，未完成任务不计为通过')
                    db.execute('UPDATE jobs SET data=? WHERE id=?', (json.dumps(job), row['id']))

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=5)
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA foreign_keys=ON')
        db.execute('PRAGMA busy_timeout=5000')
        try:
            with db:
                yield db
        finally:
            db.close()

    def active(self, requested=None):
        with self.connect() as db:
            if requested:
                row = db.execute('SELECT id FROM snapshots WHERE id=?', (requested,)).fetchone()
            else:
                row = db.execute("SELECT value AS id FROM state WHERE key='active'").fetchone()
        if not row:
            raise WorkbenchError('SNAPSHOT_NOT_AVAILABLE', '尚无有效索引，请刷新元数据', 503 if not requested else 409)
        return row['id']

    def publish(self, snapshot, entities, files, cancelled=lambda: False):
        if cancelled():
            raise WorkbenchError('CANCELLED', '任务已取消')
        with self.connect() as db:
            db.execute('INSERT INTO snapshots VALUES(?,?,?,?)', (snapshot['id'], snapshot['created'], snapshot['digest'], json.dumps(snapshot, ensure_ascii=False)))
            db.executemany('INSERT INTO entities VALUES(?,?,?,?)', ((snapshot['id'], kind, item['id'], json.dumps(item, ensure_ascii=False)) for kind, items in entities.items() for item in items))
            db.executemany('INSERT INTO files VALUES(?,?,?,?,?,?)', ((snapshot['id'], f['bundle'], f['path'], f['sha256'], f['size_bytes'], json.dumps(f, ensure_ascii=False)) for f in files))
            if cancelled():
                raise WorkbenchError('CANCELLED', '任务已取消')
            db.execute("INSERT OR REPLACE INTO state VALUES('active',?)", (snapshot['id'],))

    def info(self, snapshot):
        with self.connect() as db:
            return json.loads(db.execute('SELECT info FROM snapshots WHERE id=?', (snapshot,)).fetchone()[0])

    def list(self, snapshot, kind):
        with self.connect() as db:
            return [json.loads(x[0]) for x in db.execute('SELECT data FROM entities WHERE snapshot=? AND kind=? ORDER BY rowid', (snapshot, kind))]

    def get(self, snapshot, kind, identity):
        with self.connect() as db:
            row = db.execute('SELECT data FROM entities WHERE snapshot=? AND kind=? AND id=?', (snapshot, kind, identity)).fetchone()
        if not row:
            raise WorkbenchError('NOT_FOUND', '找不到登记记录', 404)
        return json.loads(row[0])

    def files(self, snapshot, bundle=None, q='', offset=0, limit=50):
        conditions, args = ['snapshot=?'], [snapshot]
        if bundle:
            conditions.append('bundle=?'); args.append(bundle)
        if q:
            conditions.append("path LIKE ? ESCAPE '\\'")
            args.append('%' + q.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_') + '%')
        where = ' AND '.join(conditions)
        with self.connect() as db:
            total = db.execute('SELECT count(*) FROM files WHERE '+where, args).fetchone()[0]
            rows = db.execute('SELECT data FROM files WHERE '+where+' ORDER BY bundle,path LIMIT ? OFFSET ?', [*args, limit, offset])
            return [json.loads(x[0]) for x in rows], total

    def job(self, value):
        with self.connect() as db:
            db.execute('INSERT OR REPLACE INTO jobs VALUES(?,?)', (value['id'], json.dumps(value, ensure_ascii=False)))

    def jobs(self):
        with self.connect() as db:
            return [json.loads(x[0]) for x in db.execute('SELECT data FROM jobs ORDER BY rowid DESC LIMIT 30')]
