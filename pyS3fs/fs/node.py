# -*- coding: utf-8 -*-
from stat import S_IFDIR, S_IFLNK, S_IFREG

def debug_print_tree(root, level=0):
    print ("\t"*level)+"root: {}, has {} children".format(root.name, len(root.children))
    for child in root.children:
        debug_print_tree(child, level+1)


class NodeNotFound(Exception):
    pass


class _Node(object):
    def __init__(self, name):
        self.name = name
        self.children = []

    def get_attrs(self):
        raise NotImplemented("This method should only be called on a subclass")

    def get_child(self, name):
        try:
            return filter(lambda c: c.name == name, self.children)[0]
        except IndexError:
            raise NodeNotFound

    def append_child(self, node):
        if node.name not in [child.name for child in self.children]:
            self.children.append(node)
        else:
            node = filter(lambda c: c.name == node.name, self.children)[0]
        return node

    def delete_child(self, name):
        if name in [c.name for c in self.children]:
            self.children = filter(lambda n: n.name != name, self.children)
        else:
            raise NodeNotFound

class File(_Node):
    def get_attrs(self):
        return dict(st_mode=(S_IFREG | 0644), st_size=4096,
                    st_ctime=0, st_mtime=0, st_atime=0)


class Dir(_Node):
    def get_attrs(self):
        return dict(st_mode=(S_IFDIR | 0755), st_nlink=2,
                    st_ctime=0, st_mtime=0, st_atime=0)

