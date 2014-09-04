# -*- coding: utf-8 -*-

import logging

from errno import ENOENT

from pyS3fs.net import S3Client
from pyS3fs.fs import File, Dir
from pyS3fs.fs import NodeNotFound, debug_print_tree

from fuse import FuseOSError, Operations, LoggingMixIn

class S3fs(LoggingMixIn, Operations):

    def __init__(self):
        self.S3Client = S3Client()
        self.root_node = Dir(name="")
        logging.info("Creating file tree...")
        filenames = self.S3Client.list_files()
        self._parse_filenames_into_tree(filenames)
        logging.info("Created.")

    def _get_nodes_names(self, full_path):
        tokens = full_path.split("/")
        return filter(lambda t: t != "", tokens)

    def _get_dir_and_file_names(self, full_path):
        file_name = None
        dir_names = []
        tokens = full_path.split("/")
        if tokens[-1] != "":
            file_name = tokens.pop()
        dir_names = filter(lambda t: t != "", tokens)
        return dir_names, file_name

    def _parse_filenames_into_tree(self, filenames):
        for f in filenames:
            self._add_path_to_tree(f)

    def _add_path_to_tree(self, full_path):
        dir_names, file_name = self._get_dir_and_file_names(full_path)

        ancestor = self.root_node
        for dir_name in dir_names:
            ancestor = ancestor.append_child(Dir(name=dir_name))
        if file_name:
            ancestor.append_child(File(name=file_name))

    def _remove_path_from_tree(self, full_path):
        node_names = self._get_nodes_names(full_path)

        node = self.root_node
        try:
            for node_name in node_names[:-1]:
                node = node.get_child(node_name)
            node.delete_child(node_names[-1])
        except NodeNotFound:
            raise ValueError

    def _get_node(self, full_path):
        dir_names, file_name = self._get_dir_and_file_names(full_path)

        node = self.root_node
        try:
            for dir_name in dir_names:
                node = node.get_child(dir_name)
            if file_name:
                return node.get_child(file_name)
            else:
                return node
        except NodeNotFound:
            return None

    def getattr(self, path, fh=None):
        logging.debug("getattr path={}, fh={}".format(path, fh))

        node = self._get_node(path)
        if not node:
            raise FuseOSError(ENOENT)

        return node.get_attrs()

    def read(self, path, size, offset, fh):
        logging.debug("read path={} size={} offset={} fh={}".format(path, size, offset, fh))
        return self.S3Client.get_file(path)

    def create(self, path, mode):
        logging.debug("create path={} mode={}".format(path, mode))
        self._add_path_to_tree(path)
        return 0

    def write(self, path, data, offset, fh):
        logging.debug("write path={} datalen={}".format(path, len(data)))
        self.S3Client.put_file(path, data)
        return len(data)

    def truncate(self, path, length, fh=None):
        logging.debug("truncate path={} length={} fh={}".format(path, length, fh))
        pass

    def unlink(self, path):
        logging.debug("unlink path={}".format(path))
        self.S3Client.delete_file(path)
        self._remove_path_from_tree(path)

    def readdir(self, path, fh):
        logging.debug("readdir path: {}, fh: {}".format(path, fh))
        node = self._get_node(path)
        return [n.name for n in node.children]

    def mkdir(self, path, mode):
        logging.debug("mkdir path={} mode={}".format(path, mode))
        self.S3Client.put_file(path+"/", data="")
        self._add_path_to_tree(path+"/")

    # rmdir already recursively calls unlink for files and rmdir for subdirs!
    def rmdir(self, path):
        logging.debug("rmdir path={}".format(path))
        self.S3Client.delete_file(path+"/")
        self._remove_path_from_tree(path+"/")

