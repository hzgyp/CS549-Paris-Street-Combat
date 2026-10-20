"""Owned local UI QA server; current active metadata only, never refreshes live index."""
import json
import os
from pathlib import Path
import secrets
import socket
import sqlite3
import sys
import uvicorn

ROOT=Path(__file__).resolve().parents[3]
EVIDENCE=ROOT/'tmp/npc-ai-live-20261017/work_v1'
STATE=EVIDENCE/'server-state-active'
sys.path.insert(0,str(ROOT/'Tools/AssetWorkbench'))
from app.main import create_app
from app.store import Store

def main():
    target=Store(STATE/'cache/index.sqlite3')
    uri='file:'+str(ROOT/'Assets/LocalWorking/AssetWorkbench/cache/index.sqlite3').replace('\\','/')+'?mode=ro'
    with sqlite3.connect(uri,uri=True) as source, target.connect() as dest:
        source.execute('BEGIN')
        active=source.execute("SELECT value FROM state WHERE key='active'").fetchone()[0]
        snap=source.execute('SELECT * FROM snapshots WHERE id=?',(active,)).fetchone()
        dest.execute('INSERT OR IGNORE INTO snapshots VALUES(?,?,?,?)',snap)
        rows=source.execute('SELECT * FROM entities WHERE snapshot=?',(active,)).fetchall()
        dest.executemany('INSERT OR IGNORE INTO entities VALUES(?,?,?,?)',rows)
        dest.execute("INSERT OR REPLACE INTO state VALUES('active',?)",(active,))
        source.rollback()
    sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
    token=secrets.token_urlsafe(32)
    (EVIDENCE/'qa-server.private.json').write_text(json.dumps({'pid':os.getpid(),'port':port,'token':token}),encoding='utf-8')
    (EVIDENCE/'QA_INDEX_COPY.json').write_text(json.dumps({'snapshot':active,'entity_count':len(rows),'scope':'active metadata only; files table omitted; no live publication','port':port,'pid':os.getpid()},indent=2),encoding='utf-8')
    app=create_app(root=ROOT,state_dir=STATE,token=token,port=port)
    uvicorn.Server(uvicorn.Config(app,host='127.0.0.1',port=port,log_level='warning')).run(sockets=[sock])

if __name__=='__main__':main()
