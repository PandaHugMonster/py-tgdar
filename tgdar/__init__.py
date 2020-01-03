# -*- coding: utf-8 -*-
from tgdar.ArFile import ArFile


def open(name=None, mode='r', fileobj=None, bufsize=10240):
    return ArFile.open(name, mode, fileobj, bufsize)
