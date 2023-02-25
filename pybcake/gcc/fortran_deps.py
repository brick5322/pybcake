from ..target import *
from ..group import *


class fortran_module:
    def __init__(self, module: str, filename: str, dependency: list):
        self.module = module
        self.filename = filename
        self.dependency = dependency
        self.entry_degree = 0


def find_mod(filename: str):
    modules = []
    with open(filename) as fp:
        file_using = []
        has_line_break = False
        line = fp.readline()
        status_in_module = False
        while line:
            line = line.split("!")[0]
            if line.strip() == "":
                line = fp.readline()
                continue
            if has_line_break:
                line += fp.readline().strip().lower()[1:]
            else:
                line = line.strip().lower()
                has_line_break = False
            if line[-1] == '&':
                line = line[:-1]
                has_line_break = True
                continue

            words = line.split()
            if words[0] == 'use':
                if status_in_module:
                    modules[-1].dependency.append(words[1].split(',')[0])
                else:
                    file_using.append(words[1].split(',')[0])
            elif words[0] == 'module':
                status_in_module = True
                modules.append(fortran_module(words[1], filename, []))
            elif words[0] == 'end' and words[1] == 'module':
                status_in_module = False
            line = fp.readline()
        if file_using:
            modules.append(fortran_module("File_" + filename, filename, file_using))
    for mod in modules:
        mod.dependency = list(set(mod.dependency))
    return modules


def fortran_file_sort(files: list, target_initializer):
    modules = {}
    for f in files:
        for mod in find_mod(f):
            modules[mod.module] = mod

    for mod in modules.values():
        mod.dependency = [item for item in mod.dependency if item in modules]

    for mod in modules.values():
        mod.entry_degree = len(mod.dependency)
    ret_groups = []
    added_files = set()

    time_left = len(modules)
    while time_left:
        file_in_same_depth = set()
        mod_in_same_depth = []

        for mod in modules.values():
            if mod.entry_degree == 0:
                mod_in_same_depth.append(mod)
                if mod.filename in added_files:
                    raise ValueError("exist ring")
                added_files.add(mod.filename)
                mod.entry_degree -= 1
                time_left -= 1

        for mod in modules.values():
            for prev_mod in mod_in_same_depth:
                try:
                    mod.dependency.remove(prev_mod.module)
                    mod.entry_degree -= 1
                except ValueError:
                    pass

        for mod in mod_in_same_depth:
            file_in_same_depth.add(mod.filename)

        group = Group("FortranFiles")
        file_in_same_depth = list(file_in_same_depth)
        for file in file_in_same_depth:
            group.targets.append(target_initializer(file))

        ret_groups.append(group)
    return ret_groups
