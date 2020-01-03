# -*- coding: utf-8 -*-
# Author: Ivan "PandaHugMonster" Ponomarev <panda@taggerd.org>
import struct

from tgdar.ArInfo import ArInfo
from tgdar.ArEndOfFile import ArEndOfFile
from tgdar.ArWrongFormatException import ArWrongFormatException
from tgdar.ArWrongOpenModeException import ArWrongOpenModeException
"""
    Code is undone. It's suitable only to unpack AR file format that used in DEB packages.
    Later version (starting from 1.0) should include other "ar" formats (GNU, BSD, BSD44 and Solaris x64)
"""


class ArFile:
    """
    Code example how to use:
        with ArFile.open('tgd-helpers_0.1-1_all.deb', 'r') as f:
            members = f.getmembers()
            print(members)

            member: ArInfo = f.getmember('debian-binary')
            if member:
                print(member.content)

            member: ArInfo = f.getmember('control.tar.gz')
            if member:
                tar = tarfile.open(fileobj=member.content_as_bytes_io)
                for member in tar.getmembers():
                    if member.isfile():
                        q: BufferedReader = tar.extractfile(member)
                        for line in q.readlines():
                            print(line)

    """

    VERSION: str = '0.5'

    AR_BITS_32 = 32
    AR_BITS_64 = 64

    AR_TYPE_UNKNOWN = None
    AR_TYPE_GNU = 'gnu'
    AR_TYPE_BSD = 'bsd'
    AR_TYPE_BSD44 = 'bsd44'

    OPEN_MODE_READ = 'r'
    OPEN_MODE_WRITE = 'w'

    fd = None
    type: str = AR_TYPE_UNKNOWN
    bits: int = AR_BITS_32
    file_path: str = None
    open_mode: str = OPEN_MODE_READ
    file_obj = None
    buffer_size: int = 10240

    _files_section_position = None

    _cached_members: dict = None

    def __init__(self, name=None, mode='r', fileobj=None, bufsize=10240, is_rt: bool = False):
        self.file_path = name
        self.open_mode = mode
        self.file_obj = fileobj
        self.buffer_size = bufsize

    @property
    def is_bsd_extended_file_name(self):
        return self.type == self.AR_TYPE_BSD44

    @classmethod
    def open(cls, name=None, mode='r', fileobj=None, bufsize=10240) -> 'ArFile':
        return cls(name, mode, fileobj, bufsize)

    def __enter__(self):
        if self.open_mode not in [self.OPEN_MODE_READ, self.OPEN_MODE_WRITE]:
            raise ArWrongOpenModeException('Wrong open mode. Please use %s or %s',
                self.OPEN_MODE_READ, self.OPEN_MODE_WRITE)
        self.fd = open(self.file_path, self.open_mode + 'b')
        self._check_header()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.fd.close()

    def _check_header(self):
        f = self.fd
        f.seek(0)
        signature, = struct.unpack('8s', f.read(8))
        if signature.decode('utf-8') != '!<arch>\n':
            raise ArWrongFormatException('File has a wrong signature. Probably not an AR archive.')

    def _data_chunk(self, length) -> bytes:
        chunk = bytes(self.fd.read(length))
        if len(chunk) < length:
            raise ArEndOfFile('Unexpected end of file')
        return chunk

    def getmembers(self, recache: bool = False):
        if not self._cached_members or recache:
            self._cached_members = dict()
            while True:
                try:
                    ar_info = ArInfo(self._data_chunk(60))
                    ar_info.set_content(self._data_chunk(ar_info.size))
                    self._cached_members[ar_info.name] = ar_info
                except ArEndOfFile:
                    break
        return self._cached_members

    def getmember(self, name: str, recache: bool = False) -> ArInfo or None:
        res = self.getmembers(recache)
        if name in res:
            return res[name]
        return None

    def getnames(self, recache: bool = False):
        res = self.getmembers(recache)
        return res.keys()
