import os
import re


def find_file(from_dir: str, suffix=None, recursive: bool = False):
    file = []
    if not suffix:
        return file
    if recursive:
        for root, _, files in os.walk(from_dir):
            for f in files:
                file.append(root + "/" + f)
    else:
        if not from_dir.endswith("/"):
            from_dir += "/"
        for f in os.listdir(from_dir):
            if os.path.isfile(os.path.abspath(from_dir + f)):
                file.append(from_dir + f)
    assert isinstance(suffix, list)
    ret = []
    for i in file:
        for j in suffix:
            if j[0] == '.':
                j = j.split('.')[-1]
            if re.search(".*\\." + j + "$", i):
                ret.append(i)
                continue
    return ret


def find_c_dependency(filename: str, include_dirs: list, ):
    src_dir, src_name = os.path.split(filename)
    finc_dependency = []
    with open(filename) as fp:
        line = fp.readline()
        while line:
            finc_dependency += re.findall('#include *"(.*)"\n', line)
            line = fp.readline()

    dep_dirs: list[str] = []
    dependency = []
    for dep_dir in include_dirs + [src_dir]:
        if len(dep_dir) == 0:
            continue
        elif dep_dir.endswith("/"):
            dep_dirs.append(dep_dir)
        else:
            dep_dirs.append(dep_dir + "/")
        dep_dirs = list(set(dep_dirs))

    for depend in finc_dependency:
        for dep_dir in dep_dirs:
            dep_file = dep_dir + depend
            if os.path.exists(dep_file):
                dependency += [dep_file]
                if src_name.endswith(".c") or src_name.endswith(".cpp") \
                        or src_name.endswith(".h") or src_name.endswith(".hpp"):
                    dependency += find_c_dependency(dep_file, include_dirs)
                dependency = list(set(dependency))
                break
    return dependency


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


def fortran_file_sort(files: list):
    modules = {}
    for f in files:
        for mod in find_mod(f):
            modules[mod.module] = mod

    for mod in modules.values():
        mod.dependency = [item for item in mod.dependency if item in modules]

    for mod in modules.values():
        mod.entry_degree = len(mod.dependency)
    ret_files = []
    time_left = len(modules)
    while time_left:
        file_in_same_depth = []
        for mod in modules.values():
            if mod.entry_degree != 0:
                continue
            if mod.filename in ret_files:
                raise ValueError("exist ring")
            time_left -= 1
            file_in_same_depth.append(mod.filename)
            for mod2 in modules.values():
                try:
                    mod2.dependency.remove(mod.module)
                    mod2.entry_degree -= 1
                except ValueError:
                    continue
            mod.entry_degree = -1
        file_in_same_depth = list({}.fromkeys(file_in_same_depth).keys())
        ret_files += file_in_same_depth
    return ret_files


def find_pkg(pkg_name: str, cflags=True, lib_dirs=True, libs=True):
    ret = {
        "cflags": [],
        "libs": [],
        "lib_dirs": []
    }
    tmp_strs = os.popen("pkg-config --cflags --libs " + pkg_name).read().split(' ')
    if not tmp_strs:
        return ret
    tmp_strs[-1] = tmp_strs[-1][:-1]
    for i in tmp_strs:
        if len(i) < 2:
            continue
        elif i[1] == 'I':
            ret["cflags"].append(i[2:])
        elif i[1] == 'L':
            ret["lib_dirs"].append(i[2:])
        elif i[1] == 'l':
            ret["libs"].append(i[2:])
    return ret
