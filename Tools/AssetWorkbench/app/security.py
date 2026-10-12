from __future__ import annotations

import ctypes
import hashlib
import os
import stat
from pathlib import Path, PurePosixPath


class WorkbenchError(Exception):
    def __init__(self, code: str, message: str, status: int = 409):
        self.code, self.message, self.status = code, message, status
        super().__init__(message)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def relative_path(value: str) -> str:
    value = value.replace('\\', '/')
    p = PurePosixPath(value)
    if not value or p.is_absolute() or ':' in value or any(x in ('..', '') for x in value.split('/')):
        raise WorkbenchError('PATH_NOT_REGISTERED', '路径不在允许范围内', 403)
    return p.as_posix()


def safe_path(root: Path, value: str) -> Path:
    value = relative_path(value)
    candidate = root / value
    resolved = candidate.resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise WorkbenchError('PATH_NOT_REGISTERED', '解析路径越过工作区边界', 403)
    # Existing project aliases are not implicitly trusted by this service.
    part = root
    for name in PurePosixPath(value).parts:
        part = part / name
        try:
            st = part.lstat()
            if stat.S_ISLNK(st.st_mode) or getattr(st, 'st_file_attributes', 0) & 0x400:
                raise WorkbenchError('PATH_NOT_REGISTERED', '存储别名未登记，保留为不可访问', 403)
        except FileNotFoundError:
            break
    return resolved


def read_file(root: Path, value: str, max_bytes: int = 32 * 1024 * 1024) -> bytes:
    p = safe_path(root, value)
    with p.open('rb') as f:
        # Validate the actual open handle, not just the previously resolved name.
        if os.name == 'nt':
            import msvcrt
            handle = msvcrt.get_osfhandle(f.fileno())
            buf = ctypes.create_unicode_buffer(32768)
            fn = ctypes.windll.kernel32.GetFinalPathNameByHandleW
            fn.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_uint32, ctypes.c_uint32]
            count = fn(handle, buf, len(buf), 0)
            if not count or count >= len(buf):
                raise WorkbenchError('PATH_NOT_REGISTERED', '无法验证打开的文件', 403)
            final = buf.value.removeprefix('\\\\?\\')
            if Path(final).resolve() != p or not Path(final).is_relative_to(root.resolve()):
                raise WorkbenchError('PATH_NOT_REGISTERED', '打开后的文件路径发生变化', 403)
        if os.fstat(f.fileno()).st_size > max_bytes:
            raise WorkbenchError('INPUT_TOO_LARGE', '文件超出本次读取限额', 422)
        data = f.read(max_bytes + 1)
        if len(data) > max_bytes:
            raise WorkbenchError('INPUT_TOO_LARGE', '文件超出本次读取限额', 422)
        return data
