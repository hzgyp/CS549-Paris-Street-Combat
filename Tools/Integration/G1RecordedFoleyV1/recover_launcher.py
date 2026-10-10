"""Recover the identified mutable-launcher link drift; preserve the failed delivery."""
import json,shutil
from intake import ROOT,OUT,digest,save_json,row

def main():
    case=OUT/'delivery_launcher_failure';assert not case.exists();case.mkdir()
    prepared=json.loads((OUT/'candidate_v1/prepare.json').read_text('utf-8'))
    expected=next(r for r in prepared['archive_files'] if r['path']=='PLAY_G1_REVISION.cmd')
    original=ROOT/'tmp/g1-playtest-revision-20261008/hud_v3/Archive/PLAY_G1_REVISION.cmd'
    assert digest(original)==expected['sha256'] and original.stat().st_size==expected['size_bytes']
    targets=[ROOT/'tmp/g1-av-revision-20261009/candidate_v3/Archive/PLAY_G1_REVISION.cmd',
             OUT/'candidate_v1/Archive/PLAY_G1_REVISION.cmd',ROOT/'tmp/Playtest-G1-Foley-20261009/PLAY_G1_REVISION.cmd']
    before=[]
    for i,p in enumerate(targets):
        assert p.resolve().is_relative_to(ROOT.resolve()) and p.name=='PLAY_G1_REVISION.cmd'
        q=case/(str(i)+'_failed_launcher.cmd');shutil.copyfile(p,q);before.append(row(p,ROOT))
    shutil.copyfile(original,case/'original_verified_launcher.cmd')
    shutil.copyfile(ROOT/'Tools/Integration/G1RecordedFoleyV1/deliver.py',case/'deliver_v1_failed.py')
    shutil.copyfile(ROOT/'Tools/Integration/G1RecordedFoleyV1/build.ps1',case/'build_link_policy_v1_failed.ps1')
    # Only identified .cmd links are detached. No recursive delete or engine/asset manipulation.
    new_text=targets[2].read_bytes()
    targets[2].unlink();targets[2].write_bytes(new_text)
    targets[0].write_bytes(original.read_bytes()) # restore the old private archive to its exact frozen identity
    assert digest(targets[0])==expected['sha256'] and digest(targets[1])==expected['sha256']
    archive_text=targets[1].read_bytes();targets[1].unlink();targets[1].write_bytes(archive_text)
    assert digest(targets[2])!=expected['sha256'] and b'G1PlaytestFoley20261009' in targets[2].read_bytes()
    save_json(case/'recovery.json',dict(status='restored_exact_parent_launcher_and_detached_mutable_candidate_links',
        expected_parent=expected,verified_recovery_source=row(original,ROOT),temporary_changed=before,
        after=[row(p,ROOT) for p in targets],scope='Only three explicitly identified generated .cmd files; no game/native/source/save drift',
        cause='Delivery linked the Archive root launcher then wrote candidate UserDir through it; final count wrongly assumed an extra launcher instead of replacement',
        actual_trial_files=91,recording_hold=True))
    print('Original parent launcher restored exactly; candidate scripts now independent; failed bytes retained')

if __name__=='__main__':main()
