import argparse
import json
import os
import socket
import webbrowser
from pathlib import Path

from .catalog import refresh
from .store import Store
from .main import ROOT, create_app
from .network import addresses, external_origin


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('command',choices=['index','serve'])
    parser.add_argument('--metadata-only',action='store_true')
    parser.add_argument('--port',type=int,default=8765)
    parser.add_argument('--host',choices=['127.0.0.1','0.0.0.0'])
    parser.add_argument('--open-browser',action='store_true')
    args=parser.parse_args()
    state=ROOT/'Assets/LocalWorking/AssetWorkbench'
    if args.command=='index':
        result=refresh(ROOT,Store(state/'cache/index.sqlite3'))
        print(json.dumps({k:v for k,v in result.items() if k!='source_fingerprints'},ensure_ascii=True));return
    config_path=state/'config.local.json'
    config=json.loads(config_path.read_text(encoding='utf-8')) if config_path.is_file() else {}
    bind_address=args.host or config.get('host','127.0.0.1')
    if bind_address not in ('127.0.0.1','0.0.0.0'):parser.error('Unsupported bind address')
    share_ips,allowed_hosts=addresses(bind_address=='0.0.0.0')
    configured_external_url=config.get('external_url') if bind_address=='0.0.0.0' else None
    try:public_origin=external_origin(configured_external_url,bind_address=='0.0.0.0')
    except ValueError as e:parser.error(str(e))
    sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    if os.name=='nt':sock.setsockopt(socket.SOL_SOCKET,socket.SO_EXCLUSIVEADDRUSE,1)
    sock.bind((bind_address,args.port));sock.listen(128)
    app=create_app(port=args.port,allowed_hosts=allowed_hosts,shared=bind_address=='0.0.0.0',external_url=public_origin)
    try:app.state.store.active()
    except Exception:refresh(ROOT,app.state.store)
    (state/'runtime').mkdir(parents=True,exist_ok=True)
    # Private local launcher handoff, never included in an HTTP response/log.
    session=state/'runtime/session.json'
    session.write_text(json.dumps({'pid':os.getpid(),'port':args.port,'host':bind_address,'allowed_hosts':allowed_hosts,'share_ips':share_ips,'external_url':configured_external_url,'external_origin':public_origin,'token':app.state.bootstrap}),encoding='utf-8')
    share_file=state/'runtime/share-link.txt'
    if bind_address=='0.0.0.0':
        share_file.write_text('\n'.join(f'http://{ip}:{args.port}/#token={app.state.bootstrap}' for ip in share_ips)+'\n',encoding='utf-8')
    else:
        share_file.unlink(missing_ok=True)
    public_share_file=state/'runtime/public-share-link.txt'
    if public_origin:
        public_share_file.write_text(f'{public_origin}/#token={app.state.bootstrap}\n',encoding='utf-8')
    else:
        public_share_file.unlink(missing_ok=True)
    if args.open_browser:webbrowser.open(f'http://127.0.0.1:{args.port}/#token={app.state.bootstrap}')
    print(f'Asset Workbench listening on {bind_address}:{args.port}',flush=True)
    if share_ips:print('Share addresses: '+', '.join(f'http://{ip}:{args.port}' for ip in share_ips),flush=True)
    if public_origin:print('Port-forward address: '+public_origin,flush=True)
    import uvicorn
    server=uvicorn.Server(uvicorn.Config(app,host=bind_address,port=args.port,proxy_headers=False,access_log=False,log_level='warning'))
    try:server.run(sockets=[sock])
    finally:
        app.state.pool.shutdown(wait=False,cancel_futures=True)
        sock.close()


if __name__=='__main__':main()
