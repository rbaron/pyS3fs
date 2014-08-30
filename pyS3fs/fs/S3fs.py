# -*- coding: utf-8 -*-

import logging
import syslog
import os
import sys

from pyS3fs.net import S3Client

from collections import defaultdict
from errno import ENOENT
from stat import S_IFDIR, S_IFLNK, S_IFREG
from sys import argv, exit
from time import time

from fuse import FUSE, FuseOSError, Operations, LoggingMixIn

if not hasattr(__builtins__, 'bytes'):
    bytes = str


class S3fs(LoggingMixIn, Operations):

    def __init__(self):
        self.S3Client = S3Client()

    def getattr(self, path, fh=None):

        def _is_dir(path):
            return True if path == "/" else False 

        print "getattr path={}, fh={}".format(path, fh)

        #if path not in self.files:
        #    raise FuseOSError(ENOENT)

        if _is_dir(path): 
            st = dict(st_mode=(S_IFDIR | 0755), st_nlink=2)
        else:
            st = dict(st_mode=(S_IFREG | 0444), st_size=4096)

        st['st_ctime'] = st['st_mtime'] = st['st_atime'] = time()
        return st

    def read(self, path, size, offset, fh):
        print "read"
        return self.S3Client.get_file(path)

    def write(self, path, data, offset, fh):
        print "write"
        self.S3Client.put_file(path, data)
        return len(data)

    def readdir(self, path, fh):
        print "readdir"
        files = self.S3Client.list_files()
        return files


class Memory(LoggingMixIn, Operations):
    'Example memory filesystem. Supports only one level of files.'

    def __init__(self):
        self.files = {}
        self.data = defaultdict(bytes)
        self.fd = 0
        now = time()
        self.files['/'] = dict(st_mode=(S_IFDIR | 0755), st_ctime=now,
                               st_mtime=now, st_atime=now, st_nlink=2)


    def chmod(self, path, mode):
        print "chmod"
        self.files[path]['st_mode'] &= 0770000
        self.files[path]['st_mode'] |= mode
        return 0

    def chown(self, path, uid, gid):
        print "chown"
        self.files[path]['st_uid'] = uid
        self.files[path]['st_gid'] = gid

    def create(self, path, mode):
        print "create"
        self.files[path] = dict(st_mode=(S_IFREG | mode), st_nlink=1,
                                st_size=0, st_ctime=time(), st_mtime=time(),
                                st_atime=time())

        self.fd += 1
        return self.fd

    def getattr(self, path, fh=None):
        print "getattr"
        if path not in self.files:
            raise FuseOSError(ENOENT)

        return self.files[path]

    def getxattr(self, path, name, position=0):
        print "getattrx"
        attrs = self.files[path].get('attrs', {})

        try:
            return attrs[name]
        except KeyError:
            return ''       # Should return ENOATTR

    def listxattr(self, path):
        print "listxattr"
        attrs = self.files[path].get('attrs', {})
        return attrs.keys()

    def mkdir(self, path, mode):
        print "mkdir"
        self.files[path] = dict(st_mode=(S_IFDIR | mode), st_nlink=2,
                                st_size=0, st_ctime=time(), st_mtime=time(),
                                st_atime=time())

        self.files['/']['st_nlink'] += 1

    def open(self, path, flags):
        print "open"
        self.fd += 1
        return self.fd

    def read(self, path, size, offset, fh):
        print "read"
        return self.data[path][offset:offset + size]

    def readdir(self, path, fh):
        print "readdir"
        return ['.', '..'] + [x[1:] for x in self.files if x != '/']

    def readlink(self, path):
        print "readlink"
        return self.data[path]

    def removexattr(self, path, name):
        print "removexattr"
        attrs = self.files[path].get('attrs', {})

        try:
            del attrs[name]
        except KeyError:
            pass        # Should return ENOATTR

    def rename(self, old, new):
        print "rename"
        self.files[new] = self.files.pop(old)

    def rmdir(self, path):
        print "rmdir"
        self.files.pop(path)
        self.files['/']['st_nlink'] -= 1

    def setxattr(self, path, name, value, options, position=0):
        print "setxattr"
        # Ignore options
        attrs = self.files[path].setdefault('attrs', {})
        attrs[name] = value

    def statfs(self, path):
        print "statfs"
        return dict(f_bsize=512, f_blocks=4096, f_bavail=2048)

    def symlink(self, target, source):
        print "symlink"
        self.files[target] = dict(st_mode=(S_IFLNK | 0777), st_nlink=1,
                                  st_size=len(source))

        self.data[target] = source

    def truncate(self, path, length, fh=None):
        print "truncate"
        self.data[path] = self.data[path][:length]
        self.files[path]['st_size'] = length

    def unlink(self, path):
        print "unlink"
        self.files.pop(path)

    def utimens(self, path, times=None):
        print "utimens"
        now = time()
        atime, mtime = times if times else (now, now)
        self.files[path]['st_atime'] = atime
        self.files[path]['st_mtime'] = mtime

    def write(self, path, data, offset, fh):
        print "write"
        self.data[path] = self.data[path][:offset] + data
        self.files[path]['st_size'] = len(self.data[path])
        return len(data)
