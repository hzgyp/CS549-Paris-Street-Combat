"""Read-only authenticated verification while local recovery is prepared."""
from publish import OUT,SHARE,read,verify,sha,write,now,transport


def main():
    item=read(OUT/'before-paris-g1-packaged-playtest.json')['files'][0]
    alias='/releases/paris-g1-playtest-20261009-hud-v3/Paris-G1-HUD-20261009.zip'
    info=(SHARE/item['remote_path'].lstrip('/')).stat();other=(SHARE/alias.lstrip('/')).stat()
    assert info.st_ino==other.st_ino and info.st_nlink==2 and info.st_size==item['size_bytes']
    back=OUT/'old-sftp-retirement-readback.zip'
    assert not back.exists() and not (OUT/'old-remote-authenticated-proof.json').exists()
    print('Authenticated read-only verification of retired remote candidate',flush=True)
    transport().batch([f'get "{item["remote_path"]}" "{back.as_posix()}"'],'old-package-retirement-readback')
    verify(back,item)
    write(OUT/'old-remote-authenticated-proof.json',dict(at=now(),remote_path=item['remote_path'],alias=alias,sha256=sha(back),
        size_bytes=back.stat().st_size,shared_inode=info.st_ino,links=2,method='Pinned-host authenticated SFTP full download; local shell read denied, ACL unchanged'))
    back.unlink()
    print('Old remote package authenticated SHA256/size verified; no removal',flush=True)


if __name__=='__main__':main()
