# -*- coding: utf-8 -*-

import logging

from collections import defaultdict

from errno import ENOENT

from pyS3fs.net import S3Client

from pyS3fs.fs import File, Dir
from pyS3fs.fs import node_utils
from pyS3fs.fs import Cache, CacheType
from pyS3fs.fs import NodeNotFound, debug_print_tree

from fuse import FuseOSError, Operations, LoggingMixIn


class S3fs(LoggingMixIn, Operations):

    def __init__(self):
        self.S3Client = S3Client()
        self.root_node = Dir(name="")
        self.cache_registry = {}
        logging.info("Creating file tree...")
        filenames_and_sizes = self.S3Client.list_filenames_and_sizes()
        node_utils.parse_filenames_into_tree(self.root_node, filenames_and_sizes)
        logging.info("Created.")

    def release(self, path, fh):
        logging.debug("release path={}, fh={}".format(path, fh))
        if self.cache_registry[path].cache_type == CacheType.UPSTREAM:
            self.S3Client.put_file(path, self.cache_registry[path].data)
        self.cache_registry.pop(path)

    def fsync(self, path, datasync, fh):
        logging.debug("fsync path={}, datasync={}, fh={}".format(path, datasync, fh))

    def getattr(self, path, fh=None):
        logging.debug("getattr path={}, fh={}".format(path, fh))

        node = node_utils.get_node(self.root_node, path)
        if not node:
            raise FuseOSError(ENOENT)

        return node.get_attrs()

    def read(self, path, size, offset, fh):
        logging.debug("read path={} size={} offset={} fh={}".format(path, size, offset, fh))

        if path not in self.cache_registry:
            self.cache_registry[path] = Cache(
                cache_type=CacheType.DOWNSTREAM,
                data=self.S3Client.get_file(path)
            )
            logging.debug("read got file. len: {}".format(len(self.cache_registry[path].data)))

        return self.cache_registry[path].data[offset:(offset+size)]

    def create(self, path, mode):
        logging.debug("create path={} mode={}".format(path, mode))
        node_utils.add_path_to_tree(self.root_node, path)
        return 0

    def write(self, path, data, offset, fh):
        logging.debug("write path={} datalen={} offset={}".format(path, len(data), offset))
        if path not in self.cache_registry:
            self.cache_registry[path] = Cache(
                cache_type=CacheType.UPSTREAM,
            )
        self.cache_registry[path].append_data(data)
        node = node_utils.get_node(self.root_node, path)
        node.st_size = len(self.cache_registry[path].data)
        return len(data)

    def flush(self, path, fh):
        logging.debug("flush path={} fh={}".format(path, fh))

    def truncate(self, path, length, fh=None):
        logging.debug("truncate path={} length={} fh={}".format(path, length, fh))

    def unlink(self, path):
        logging.debug("unlink path={}".format(path))
        self.S3Client.delete_file(path)
        node_utils.remove_path_from_tree(self.root_node, path)

    def readdir(self, path, fh):
        logging.debug("readdir path: {}, fh: {}".format(path, fh))
        node = node_utils.get_node(self.root_node, path)
        return [n.name for n in node.children]

    def mkdir(self, path, mode):
        logging.debug("mkdir path={} mode={}".format(path, mode))
        self.S3Client.put_file(path+"/", data="")
        node_utils.add_path_to_tree(self.root_node, path+"/")

    # rmdir already recursively calls unlink for files and rmdir for subdirs!
    def rmdir(self, path):
        logging.debug("rmdir path={}".format(path))
        self.S3Client.delete_file(path+"/")
        node_utils.remove_path_from_tree(self.root_node, path+"/")

