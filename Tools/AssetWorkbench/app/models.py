"""Strict self-contained GLB boundary for registered private browser previews."""
import json
import struct
from .security import WorkbenchError

MAX_MODEL_BYTES=128*1024**2

def validate_glb(raw):
    try:
        if len(raw)<28 or len(raw)>MAX_MODEL_BYTES:raise ValueError('size')
        magic,version,total=struct.unpack_from('<III',raw)
        if magic!=0x46546c67 or version!=2 or total!=len(raw):raise ValueError('header')
        size,kind=struct.unpack_from('<II',raw,12)
        if kind!=0x4e4f534a or size>8*1024**2 or size%4 or 20+size>len(raw):raise ValueError('json')
        doc=json.loads(raw[20:20+size]);offset=20+size;binary=0
        if offset<len(raw):
            binary,kind=struct.unpack_from('<II',raw,offset)
            if kind!=0x004e4942 or binary%4 or offset+8+binary!=len(raw):raise ValueError('bin')
        if doc.get('asset',{}).get('version')!='2.0':raise ValueError('version')
        def inspect(value):
            if isinstance(value,dict):
                for k,v in value.items():
                    if k=='uri':raise ValueError('external dependency')
                    inspect(v)
            elif isinstance(value,list):
                for v in value:inspect(v)
        inspect(doc)
        buffers=doc.get('buffers',[])
        if len(buffers)>1 or any(not 0<=b['byteLength']<=binary for b in buffers):raise ValueError('buffer size')
        for view in doc.get('bufferViews',[]):
            if view.get('buffer',0)!=0 or view.get('byteOffset',0)<0 or view['byteLength']<0 or view.get('byteOffset',0)+view['byteLength']>binary:raise ValueError('buffer range')
        for key,limit in [('nodes',8192),('meshes',2048),('images',512),('animations',128),('accessors',32768)]:
            if len(doc.get(key,[]))>limit:raise ValueError('resource limit')
        for accessor in doc.get('accessors',[]):
            if not 0<=accessor['count']<=10_000_000:raise ValueError('accessor limit')
        return doc
    except (ValueError,KeyError,TypeError,AttributeError,RecursionError,struct.error,UnicodeError) as e:
        raise WorkbenchError('MODEL_FORMAT_REJECTED','模型格式、内嵌资源或容量校验失败',422) from e
