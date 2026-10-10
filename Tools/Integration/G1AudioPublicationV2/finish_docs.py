"""Summarize actual completed publication/retirement receipts."""
from publish import ROOT, OUT, PROOF, read


def main():
    result=read(OUT/'result.json')
    assert result['status']=='reviewed_audio_v2_selected_published_old_packages_retired'
    plan=read(OUT/'retirement.json')
    members=len(read(OUT/'package.json')['members'])
    net=result['actual_net_free_increase_bytes']/2**30
    physical=result['remote_removed_physical_bytes']/2**30
    compact=result['compact_recovery_bytes']/2**20
    common=f"""Game SHA256: {result['game_sha256']}.
ZIP: {result['zip']['size_bytes']:,} bytes, {members} members.
ZIP SHA256: {result['zip']['sha256']}.
"""
    english=f'''# Reviewed audio V2 adoption, private publication and package retirement

9 October2026. Yupu manually retested the exact latest executable, passes revised
audio and selects it for continued development. The current selectors now point
to exact42 G1FootContactAudio20261009/Project and its matching candidate_v2 authoring
Project. Existing models/fingers/actions/camera/gun/ammunition/HUD/save schema and
terminal saved-death implementation are preserved. No code/build/cook/Editor/game
entry or screen recording occurred during this publication. See the paired plan
for cases read, early checks and stopping conditions.

Private release `{result['release']}`. Download
`{result['download']}`, extract all and run PLAY_G1_REVISION.cmd. The exact88-file
normal trial is bundled with English/Chinese controls, source identity and the
existing Microsoft x64 prerequisite. No personal save/log/credential is included.
{common}
Every member was fully read and SHA256/size checked. The final immutable ZIP and
33 audio objects, both manifests and readable hard-link download were authenticated
SFTP downloaded and rehashed. Release guides were independently returned. Shared
account create/overwrite/rename/download/delete passed in a unique probe, root ACL
unchanged. Native city/character/weapon selections and source758/native359 remain
exact; Catalog advances only the package selection plus the independent33-cue
resource inventory through an explicit authorization proof and epoch ledger.
The package alias consumes no second remote archive allocation. Second-machine
restoration/runtime and external forwarding were not retested by the publisher.

Retired {result['local_targets_removed']} exact local outputs: nine superseded
trial/Archive directories and the old local HUD ZIP. Removed the old SFTP HUD ZIP
alias and its unreferenced package object ({physical:.2f}GiB physically). Old remote
manifest metadata remains with explicit bilingual retirement/download guidance.
Every old directory file and old ZIP member has a size/hash-matched recovery:
selected current bytes or the {compact:.1f}MiB compressed unique-file archive.
The new RECOVERY_MAP and inventory authenticate the locations without rewriting
historical raw receipts. Existing intermediate restore now resolves removed HUD
Archive references through this map; the previous V13 ZIP remains a necessary
recovery dependency. Source/log/images/raw videos/checkpoints/failure data and
the current88-file playable/42-file authoring Project remain. Two user save files
are byte-identical. Unknown SFTP objects/incoming work and asset originals were
excluded. No user process was terminated and no ACL was weakened.

Logical local removed bytes: {result['logical_local_removed_bytes']:,}; shared
hard links mean this is not reclaimed capacity. Net D-drive free increase from
the frozen pre-publication state, after storing the new local/remote package and
compact recovery archive: **{net:.2f}GiB**. Exact before/after counts are in
G1AudioPublicationV2/RESULT_20261009.json; filesystem activity outside this task
can also affect a drive-level free-space measurement.

Pre-publication readme inspection corrected an erroneous C crouch label to Left
Ctrl, matching the unchanged DefaultInput binding. Both rejected readme bytes and
the original unpublished package identity are retained privately. An ad hoc
verification used system cp936 for UTF8 JSON and failed a Unicode member lookup;
the archive was intact. Explicit UTF8 verification passes all92 final members.
These are metadata/preflight corrections, not a new gameplay/audio experiment.

Recovery preparation also hits a local-shell PermissionError on the old protected
SFTP object after compact-member checks. No deletion occurs in that attempt.
Preserve its receipt/archive and reverify all unique members. The old remote bytes
are then fully authenticated SFTP downloaded and hashed, without ACL changes.
New hashes come from publication readbacks; final checks add authenticated
presence/size and exact manifest identity, not a second rejected-shell byte hash.

Git carries matching exact source/configuration/provenance, repair/failure and
recovery/publication metadata, with binary/credential guards. Matching commit/push
is the final publication step; its actual remote HEAD is verified and recorded
outside its own Git tree in the private receipt and user handoff. No private
vendor/native/audio/archive/video bytes are added to Git. The current team guide
is TEAM_CURRENT_BUILD_20261009.md. Cached original Editor binaries do not represent
this newer Game; a selected-source Editor build/recook is still separate.

Manual listening passes by user report; the original quantitative scope remains
20 stable contacts checked and9 blend contacts UNASSESSED. Exact reusable German
live-fire audio, physical contact, natural-turn recording correction, FPS/stress,
teammate/video/report/mentor/course gates remain separate. Audio approval releases
its listening hold but this task records no video. Earlier raw video and stopped
failure routes are retained.
'''
    chinese=f'''# 人工复验音效V2采用、私有发布与旧包清理结果

2026年10月9日。Yupu复验最新精确程序通过，明确选为开发基础。当前选择器已指向
G1FootContactAudio20261009/Project精确42文件及一致的candidate_v2制作工程。
保留模型/手指/动作/镜头/枪械/弹药/HUD/存档格式与直接恢复死亡终态。本次发布
没有修改游戏代码、构建、烹饪、编辑器/游戏启动或录屏。失败案例、早期检查与
停止条件见对应英文计划及同步中文。

SFTP版本`{result['release']}`，下载`{result['download']}`，完整解压后启动
PLAY_G1_REVISION.cmd。原88文件试玩另附双语操作、源码身份和微软x64运行库，
没有个人存档/日志/凭据。{common}
逐成员完整回读SHA256/大小通过；不可变ZIP、33音效对象、两份清单和易读硬链接
入口均认证SFTP下载并核对，下载说明另行回读。仅独立探针验证共享账户增/改/改名/
下载/删，根ACL不变。城市/人物/枪械原生选择及source758/native359一致，Catalog
只通过明确授权证明与epoch账本更新试玩包选择、增加独立33音效清单。易读ZIP
硬链接不再占一份包空间；组员电脑与公网转发未由发布者重新验证。

本机清理{result['local_targets_removed']}项：9个过时试玩/Archive目录及旧HUD ZIP。
SFTP删除旧HUD ZIP别名与不再被当前清单引用的包对象，实际远端字节{physical:.2f}GiB；
旧清单文本保留，并附双语退休/新版下载说明。每个旧目录文件和旧ZIP成员均有
大小/哈希一致的恢复来源：当前版本字节或{compact:.1f}MiB唯一文件压缩档。
新RECOVERY_MAP/清单记录位置，不改写原始历史记录；旧中间包恢复脚本已接入
被删HUD Archive路径映射。原V13 ZIP仍是必要恢复依赖，保留。源码/日志/图像/
原始视频/存档/失败资料、当前88文件试玩及42文件制作工程均保留；2个用户存档
逐字节一致。未知SFTP对象/incoming工作及原件排除，没有终止用户进程或放宽ACL。

逻辑本机删除大小{result['logical_local_removed_bytes']:,}字节，硬链接使其不能等同
实际回收。计入新本机/远端包及差异恢复档后，D盘相对发布前冻结状态净增
**{net:.2f}GiB**空闲。精确数据见G1AudioPublicationV2/RESULT_20261009.json；其他
工作造成的磁盘变化也可能影响整盘空闲测量。

发布前发现分发说明把蹲下误写为C，已按未改动的DefaultInput修正为左Ctrl，原
说明及未发布包身份私有保留。临时验证默认用cp936读UTF8 JSON，导致Unicode
成员查找失败，ZIP本身未坏；显式UTF8后92最终成员全部通过。仅元数据/预检
纠正，没有新增玩法或音效实验。

恢复准备在差异成员检查后直读受保护旧SFTP对象出现本机PermissionError，没有
删除。保留记录/ZIP并复核唯一成员，再完整认证SFTP下载并校验旧字节，不改ACL。
新对象哈希来自发布回读，最后增加认证存在性/大小与精确清单检查，不冒充二次
本机字节哈希。

Git包含匹配的精确源码/配置/来源、修复/失败/恢复/发布元数据，使用资产及凭据
检查。匹配提交/推送为最后一步，实际远端HEAD在本Git树外的私有记录和最终交接
中核对，避免提交自引用。Git不加入私有商业/原生/音频/压缩包/视频字节。组员按
TEAM_CURRENT_BUILD_20261009_ZH.md；旧编辑器缓存不代表较新的Game，编辑器
构建/重新烹饪仍需单独执行。

人工音效复验通过；原数值范围仍为20稳定落脚检查、9过渡未评估。精确可用德军
实录来源、物理接触、自然转身录制修正、性能/压力、组员电脑/视频/报告/导师/
课程验收仍独立。音效通过结束听感暂停，但本次没有录屏，旧视频和停止路线保留。
'''
    (ROOT/'Docs/Development/G1_AUDIO_BASELINE_PUBLICATION_RESULT_20261009.md').write_text(english,'utf-8')
    (ROOT/'Docs/Development/G1_AUDIO_BASELINE_PUBLICATION_RESULT_20261009_ZH.md').write_text(chinese,'utf-8')
    print('Bilingual actual publication/retirement result written')


if __name__=='__main__':main()
