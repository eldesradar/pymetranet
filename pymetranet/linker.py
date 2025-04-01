#!/bin/env python3

import sys
import os
import inspect

class Linker:
    """
    A utility class for creating hard links based on a configuration file.

    This class provides static methods to determine the appropriate paths and create
    hard links from a given file to a target location defined in a link node file.
    """

    @staticmethod
    def create_links(file_name: str, link_node_file: str, exe_dir: str=None, use_thr: bool=False) -> None:
        """
        Creates hard links for a given file based on the configuration specified in a link node file.

        This method determines the target node file path based on the provided parameters.
        If the 'link_node_file' is an absolute path, it is used directly; otherwise, a default path
        is constructed based on the executable directory. Then, it calls an internal method to
        create the link files.

        Args:
            file_name (str): The path to the file for which hard links will be created.
            link_node_file (str): The name or absolute path of the link node configuration file.
            exe_dir (str, optional): The directory of the executable. If None, it is automatically
                                     determined from sys.argv[0]. Defaults to None.
            use_thr (bool, optional): A flag to indicate whether to use a threshold-based mechanism.
                                      Defaults to False.

        Returns:
            None

        Raises:
            FileNotFoundError: If the determined node file does not exist.
        """
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
        """
        Creates hard links for the file at 'file_path_name' based on entries in the node file.

        The method reads the node file line by line, ignoring commented lines (starting with '#').
        For each valid line, it splits the line into a target path and a threshold value (thr).
        If the target path is relative, it is resolved relative to the file's base directory.
        Then, a hard link is created in a subdirectory (named after the parent directory of the file)
        inside the target path.

        Args:
            node_file (str): The absolute path to the node configuration file.
            file_path_name (str): The absolute path to the file for which links are to be created.
            use_thr (bool): Flag indicating whether to use threshold-based processing (currently unused).

        Returns:
            None

        Raises:
            FileNotFoundError: If the node configuration file does not exist.
        """
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

