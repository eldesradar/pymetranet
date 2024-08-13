#!/bin/env python3

import sys
import os
import inspect

class Linker:
    @staticmethod
    def create_links(file_name: str, link_node_file: str, exe_dir: str=None, use_thr: bool=False) -> None:
        if link_node_file and os.path.isabs(link_node_file):
            node_file: str = link_node_file
        else:
            #build appdir
            if exe_dir is None:
                #automatically detects directory of main using sys.argv[0]
                exe_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
            file_name_prefix = os.path.basename(file_name)[0:3]
            node_dir = os.path.realpath(os.path.join(exe_dir, "..", "etc", "pgs", "link_node", file_name_prefix))
            node_file = os.path.join(node_dir, "default" if not link_node_file else link_node_file)

        return Linker.__create_link_files(node_file, os.path.abspath(file_name), use_thr)

    @staticmethod
    def __create_link_files(node_file: str, file_path_name: str, use_thr: bool) -> None:
        file_base_name = os.path.basename(file_path_name)
        file_dir_name_no_path = os.path.basename(os.path.dirname(file_path_name))
        file_base_dir_full_path = os.path.realpath(os.path.join(file_path_name, "..", ".."))
        if not os.path.exists(node_file):
            raise FileNotFoundError("can't create link files: input link file '%s' does not exist" % node_file)
        
        f = open(node_file, "rt")
        try:
            while True:
                line = f.readline()
                if not line:
                    break

                line = line.rstrip()
                if line[0] == '#':
                    continue

                #split to separate path form thr
                values = line.split()
                if len(values) < 2:
                    continue

                path = values[0]
                thr = int(values[1])
                if os.path.isabs(path):
                    line = path
                else:
                    line = os.path.realpath(os.path.join(file_base_dir_full_path, path))
                link_file: str = os.path.join(line, file_dir_name_no_path, file_base_name)

                #check if the directory exist, otherwise create it
                create_link = True
                if not os.path.exists(os.path.dirname(link_file)):
                    try:
                        os.mkdir(os.path.dirname(link_file))
                    except Exception as ex:
                        create_link = False

                #create the hard link (only if the file does not exist)
                if create_link:
                    if not os.path.exists(link_file):
                        print("%s => %s" % (file_path_name, link_file))
                        os.link(file_path_name, link_file)
        finally:
            f.close()

