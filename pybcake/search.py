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
            if os.path.isfile(f):
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
