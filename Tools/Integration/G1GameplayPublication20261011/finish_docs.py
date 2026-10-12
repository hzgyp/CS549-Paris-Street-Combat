"""Document verified private publication without changing reviewed Game bytes."""
from publish import ROOT,OUT,PROOF,RELEASE,ZIP,GAME,MANIFEST,AID,RID,CID,TEACHER_DOWNLOAD,TEACHER_SHA,read,write,row,now
def prepend(p,text):
    old=p.read_bytes();prefix=text.encode('utf-8')
    assert text.splitlines()[0] not in old.decode('utf-8-sig')
    p.write_bytes(b'\xef\xbb\xbf'+prefix+old[3:] if old.startswith(b'\xef\xbb\xbf') else prefix+old)
pub=read(OUT/'publication.json');retention=read(PROOF/'REMOTE_RETENTION_20261011.json')
assert retention['status'].startswith('pass')
text=f'''# 最新正式试玩与源码同步

2026-10-11，最新正式版为人工通过逻辑的76文件G1GrenadeEquip，衣袖遮挡仍待修。

## 直接玩最新版本

先正常git pull --ff-only，同步后以CURRENT_DEVELOPMENT_BASELINE.json为准。
通过已有团队SFTP账号／私下提供的密钥／固定可信主机指纹下载：

`{pub['download']}`

ZIP {pub['zip']['size_bytes']:,}字节，SHA256 `{pub['zip']['sha256']}`；完整解压，运行PLAY_GRENADE_EQUIP.cmd。
无需安装UE／Python即可试玩，微软x64运行库按需安装。中文操作与正式采用状态见包内FORMAL_README_ZH.md。
SOURCE_VARIANT.json标记源码／Game；Game `{GAME}`。不要只取exe，不复制他人存档。

本版包括手雷／烟雾的可用库存滚轮切换、左键长按准备／松开投出、地雷拆除／爆炸、有限补给、战地手册／小队UI、第三视角死亡倒地与原全灭敌军圈内E持久保存。原模型、枪械手指常量及原枪械／资源／存档保护；15项同一Game既有检查及用户逻辑验证通过，衣袖、细致全程接触、匹配Editor、新外机和大量NPC压测仍分开处理。

## 要继续源码开发

精确源在Unreal/Variants/G1GrenadeEquip20261011/Project，76文件，manifest `{MANIFEST}`。
城市／原生359仍按TEAM_PLAYTEST_ZH.md恢复；其原Editor DLL不代表新的76源码。
新运行资源清单 `{RID}.json` 位于Assets/Sync/manifests，包含私有Audio／Equipment／UI，Catalog固定字节。
可直接用已核验的完整解压包准备新的tmp制作工程：

```powershell
python Tools/Integration/G1GameplayPublication20261011/prepare_source_project.py --packaged-root 'C:/Games/Paris-G1-Gameplay-20261011'
```

它逐项验证包内文件，复制精确76源及资源，并联接已恢复的本机Content；不覆盖原工作，不复制旧DLL、不自动启动或保存UE。
随后使用本机UE5.8.2构建匹配Editor／Game。包和源码同步成功不表示新电脑已经验证，仍由组员实际试玩。

## 老师评阅包保留

老师旧下载仍为 `{TEACHER_DOWNLOAD}`，SHA `{TEACHER_SHA}`。原课程访问目录／私密附件ZIP／两页PDF／密钥保持原字节。
独立保留清单 `{CID}.json` 将它与最新组员试玩区分；老师视频及此前外机证明属于原audioV2身份。
目前SFTP的旧HUD ZIP此前已删，剩下唯一较早试玩ZIP正是老师包，本次没有其它可安全删除的旧试玩字节。
未删除原生资产、原始包、workspaces／incoming、哈希对象历史或恢复依赖。
'''
for name in ['TEAM_CURRENT_BUILD_20261011_ZH.md','TEAM_CURRENT_BUILD_20261011.md']:
    (ROOT/'Docs/Development'/name).write_text(text,'utf-8')
note=f'## 2026-10-11：最新正式76版已同步SFTP\n\n最新组员包 `{pub["download"]}`；精确76源／运行资源／SHA及恢复步骤见[最新同步指南](TEAM_CURRENT_BUILD_20261011_ZH.md)。原老师audioV2下载及课程附件保留，以下旧日期文字为历史。衣袖遮挡待修；新的76版外机验证由组员进行。\n\n'
for name in ['TEAM_CURRENT_BUILD_20261009.md','TEAM_CURRENT_BUILD_20261009_ZH.md','CURRENT_DEVELOPMENT_BASELINE.md','CURRENT_DEVELOPMENT_BASELINE_ZH.md']:
    prepend(ROOT/'Docs/Development'/name,note)
for name in ['CURRENT_UI_REVIEW','CURRENT_EQUIPMENT_INPUT_REVIEW']:
    p=ROOT/'Docs/Development'/(name+'.json');d=read(p)
    d.update(publication='Latest three-member SFTP package/runtime bytes verified; teacher audioV2 protected; matching Git publication requested',sftp_release=RELEASE,sftp_download=pub['download'])
    write(p,d)
prepend(ROOT/'Assets/TEAM_SYNC_WORKFLOW.md','**Latest formal gameplay release,11October2026:** [current source/playable guide](../Docs/Development/TEAM_CURRENT_BUILD_20261011_ZH.md) selects exact76 and its private runtime resources. The latest ZIP is '+pub['download']+'. The previously supplied audioV2 course-review ZIP and credentials/report attachment remain unchanged and active under a separate course role. Earlier dated handoffs below are historical native/recovery anchors.\n\n')
prepend(ROOT/'Assets/Sync/RIGHTS.md','## Reviewed complete gameplay private release,11October2026\n\nThe owner manually accepts source76 gameplay logic with minor sleeve occlusion and explicitly requests matching Git/source and private SFTP playable publication. Existing commercial-source team entitlement remains limited to Yupu Guo, Yuqi Pu and Jingdi Wu. New team-authored mine/smoke and permitted adapted MkII, recorded CC0 audio and licensed Cinzel/OFL/Roboto/Apache2 runtime bytes accompany this private build. No public asset bytes or new teacher distribution of this76 revision are inferred. The exact old compiled audioV2 instructor/TA delivery is explicitly retained, with its existing permission and unchanged access attachment.\n\n')
prepend(ROOT/'README.md','**Latest formal source and private playable,11October2026:** exact76 manually accepted gameplay now has a verified private SFTP download; read [latest team guide](Docs/Development/TEAM_CURRENT_BUILD_20261011_ZH.md). Minor sleeve occlusion remains. Existing teacher assessment ZIP/video/access attachment remain the prior audioV2 and are preserved. No public model/texture/audio/archive/credential bytes enter Git.\n\n')
prepend(ROOT/'HANDOFF.md','## 2026-10-11：正式76私有发布与老师包保留\n\n最新SFTP：'+pub['download']+'。精确76和RuntimeResources清单见TEAM_CURRENT_BUILD_20261011_ZH及G1_GAMEPLAY_PUBLICATION实施／结果。老师旧audioV2 ZIP／哈希对象／原manifest／访问附件未变，独立course-review角色保持。旧HUD已先前删除；没有其它旧试玩ZIP可安全清理。原生／模型／枪械／存档／用户文件保持，UE继续开启。Git提交推送为本轮授权步骤，实际远端HEAD单独记录，不能按本文提前推断成功。\n\n')
ag=ROOT/'AGENTS.md';old=ag.read_bytes();idx=old.index(b'\n')+1
para='\n- Latest authorized gameplay publication,11October2026: user requests Git commit/push, latest formal76 private SFTP and obsolete packaged cleanup, explicitly preserving teacher delivery. Read G1_GAMEPLAY_PUBLICATION implementation/result and TEAM_CURRENT_BUILD_20261011_ZH. New release '+RELEASE+', Game '+GAME+'; package/runtime objects and named alias authenticated SHA/size read back. Catalog selects current gameplay/runtime plus independent retained audioV2 course-review role; native selections unchanged. Teacher old ZIP/object/manifest/access attachment retained exactly. Old HUD already retired; no other unused playable ZIP eligible, no object/native/workspace sweep. Minor sleeve issue remains; no new Editor/game/second-machine/large-NPC/course acceptance. Existing UE stays open. Git actual remote HEAD recorded separately; no public commercial bytes/credentials.\n'
ag.write_bytes(old[:idx]+para.encode('utf-8')+old[idx:])
result=dict(status='verified_private76_published_course_package_retained_git_pending',finished=now(),release=RELEASE,download=pub['download'],zip=pub['zip'],source_files=76,source_manifest_sha256=MANIFEST,game_sha256=GAME,archive_members=len(read(OUT/'package.json')['members']),runtime_resource_files=pub['resource_files'],teacher_download=TEACHER_DOWNLOAD,teacher_zip_sha256=TEACHER_SHA,teacher_access_unchanged=True,remote_obsolete_bytes_removed=0,remote_retention=retention,root_acl_unchanged=True,native_selections_unchanged=True)
write(PROOF/'RESULT_20261011.json',result)
(ROOT/'Docs/Development/G1_GAMEPLAY_PUBLICATION_RESULT_20261011_ZH.md').write_text(f'''# 正式76版私有发布及老师包保护结果

2026-10-11。最新正式包 `{pub['download']}` 已认证SFTP上传／最终对象与命名下载读回SHA核对，{result['archive_members']}成员，{pub['zip']['size_bytes']:,}字节，ZIP SHA `{pub['zip']['sha256']}`。
精确76源manifest `{MANIFEST}`；Game `{GAME}`。原100文件／程序不改，发布附来源、双语指南和原微软运行库。{pub['resource_files']}个私有运行资源逐对象认证回读；Catalog及epoch ledger只推进当前包／资源／保留课程角色，原生版本／模型／手指／枪械／存档保持。当前逻辑人工通过，衣袖待修。

老师原8,476,572,643字节audioV2 ZIP `{TEACHER_DOWNLOAD}` 完整认证读回匹配SHA `{TEACHER_SHA}`，原对象与别名同inode，原manifest／指南及课程访问六文件和私密附件ZIP保留。独立course-review manifest保证新正式选择不会取消老师下载依赖。
远端实际G1试玩ZIP仅最新与老师两份；旧HUD已此前清理，本次旧包删除量0，不能删除老师包来制造清理量。未扫原始资产／对象库／workspaces／incoming。根ACL不变，UE／独立预览继续保留。

[最新同步指南](TEAM_CURRENT_BUILD_20261011_ZH.md)、[实施](G1_GAMEPLAY_PUBLICATION_20261011_ZH.md)、[Catalog](../../Assets/Sync/CATALOG.json)、[远端保留记录](G1GameplayPublication20261011/REMOTE_RETENTION_20261011.json)。Git包含匹配源码／配置／公安全文档图示／哈希与失败记录；实际提交／推送／远端HEAD写入独立发布收据。资产二进制和课程连接密钥均不进Git。未新增游戏／Editor／第二机／压力／课程验收或录像。
''','utf-8')
print('Verified publication/current guides/rights/teacher retention documented')
