import os
import re
from .sourcefile import find_c_dependency


def find_file(from_dir: str, suffix=None):
    file = []
    for _, _, f in os.walk(from_dir):
        file += f
    if not suffix:
        return file
    assert isinstance(suffix, list)
    ret = []
    if not from_dir.endswith("/"):
        from_dir += "/"
    for i in file:
        for j in suffix:
            if j[0] == '.':
                j = j.split('.')[-1]
            if re.search(".*\\." + j + "$", i):
                ret.append(from_dir + i)
                continue
    return ret
