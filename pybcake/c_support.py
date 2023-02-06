import re
import os
from .sourcefile import SourceFile

__all__ = ["find_c_dependency"]


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

SourceFile.find_deps_funcs[".c"] = find_c_dependency
SourceFile.find_deps_funcs[".cpp"] = find_c_dependency
SourceFile.find_deps_funcs[".h"] = find_c_dependency
SourceFile.find_deps_funcs[".hpp"] = find_c_dependency
