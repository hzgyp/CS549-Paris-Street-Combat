"""Scoped formatting only: preserve the exact already-verified SFTP CRLF manifest.

Repository .gitattributes marks manifests -text, so Git preserves these bytes.
apply_patch edited metadata semantically but left mixed endings. This formatter
changes only newline encoding and requires the exact published hash before write.
"""
from formal_common import *
DEST=ROOT/'Assets/Sync/manifests/paris-gameplay-native-playtest.json'
status=read(BASE/'publication_v1/publication.json')
candidate=BASE/'publication_v1/paris-gameplay-native-playtest.json'
assert read(DEST)==read(candidate) and sha(candidate)==status['manifest_sha256']
original=DEST.read_bytes()
formatted=original.replace(b'\r\n',b'\n').replace(b'\n',b'\r\n')
assert hashlib.sha256(formatted).hexdigest()==status['manifest_sha256'],'Non-newline difference; stop formatting'
DEST.write_bytes(formatted)
assert sha(DEST)==status['manifest_sha256']
write(BASE/'publication_v1/newline_format_verification.json',{'status':'exact_verified_manifest_bytes_restored_by_newline_format_only',
    'before_sha256':hashlib.sha256(original).hexdigest(),'after_sha256':sha(DEST),
    'semantic_changes':False,'gitattributes':'Assets/Sync/manifests/*.json -text','remote_manifest_overwritten':False})
print(json.dumps({'status':'exact_verified_manifest_bytes','sha256':sha(DEST)}))
