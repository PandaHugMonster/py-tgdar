# -*- coding: utf-8 -*-
from datetime import datetime
from io import BytesIO
from struct import unpack


class ArInfo:

    HEADER_UNPACK_TEMPLATE = '16s12s6s6s8s10s2s'

    __slots__ = dict(
        name=None,
        mode=0o777,
        uid=0,
        gid=0,
        size=None,
        mtime=None,
        ar=None,
        _content=None
    )

    def __init__(self, header_data: bytes, ar: 'ArFile' = None):
        self.ar = ar
        raw_h_d = unpack(self.HEADER_UNPACK_TEMPLATE, header_data)
        file_name, file_modification_ts, uid, gid, file_mode, file_size, end_char = raw_h_d

        self._content = None
        self.mtime = datetime.fromtimestamp(int(file_modification_ts))
        self.name = str(file_name.decode('utf-8')).replace(' ', '').replace('\n', '')
        self.size = int(file_size)
        self.uid = int(uid)
        self.gid = int(gid)
        self.mode = int(file_mode)

    @property
    def content(self):
        return self._content

    def set_content(self, content):
        """
            Reason is to motivate people to write content with one step and not using ArInfo.content as a variable
        :param content:
        :return:
        """
        self._content = content

    @property
    def content_as_bytes_io(self):
        """
            It's for using with other compressing/archiving tools like tarfile or gz/bz2
        :return:
        """
        return BytesIO(self.content)
