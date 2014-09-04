# -*- coding: utf-8 -*-

from pyS3fs.fs import File, Dir
from pyS3fs.fs import NodeNotFound

def get_nodes_names(full_path):
    tokens = full_path.split("/")
    return filter(lambda t: t != "", tokens)

def get_dir_and_file_names(full_path):
    file_name = None
    dir_names = []
    tokens = full_path.split("/")
    if tokens[-1] != "":
        file_name = tokens.pop()
    dir_names = filter(lambda t: t != "", tokens)
    return dir_names, file_name

def parse_filenames_into_tree(root_node, filenames_and_sizes):
    for filename, size in filenames_and_sizes:
        add_path_to_tree(root_node, filename, size)

def add_path_to_tree(root_node, full_path, size=0):
    print "Adding: {}".format((full_path, size))
    dir_names, file_name = get_dir_and_file_names(full_path)

    ancestor = root_node
    for dir_name in dir_names:
        ancestor = ancestor.append_child(Dir(name=dir_name))
    if file_name:
        ancestor.append_child(File(name=file_name, size=size))

def remove_path_from_tree(root_node, full_path):
    node_names = get_nodes_names(full_path)

    node = root_node
    try:
        for node_name in node_names[:-1]:
            node = node.get_child(node_name)
        node.delete_child(node_names[-1])
    except NodeNotFound:
        raise ValueError

def get_node(root_node, full_path):
    dir_names, file_name = get_dir_and_file_names(full_path)

    node = root_node
    try:
        for dir_name in dir_names:
            node = node.get_child(dir_name)
        if file_name:
            return node.get_child(file_name)
        else:
            return node
    except NodeNotFound:
        return None
