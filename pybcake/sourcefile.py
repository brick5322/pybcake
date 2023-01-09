import os
from .search import *


class SourceFile:
    def __init__(self, filename: str, include_dirs: list):
        self.dependency = []
        self.filename = filename
        self.include_dirs = include_dirs

    def __setattr__(self, key, value):
        dependency = []
        if key == "include_dirs":
            src_dir, src_name = os.path.split(self.filename)
            if src_name.endswith(".c") or src_name.endswith(".cpp") \
                    or src_name.endswith(".h") or src_name.endswith(".hpp"):
                dependency += find_c_dependency(self.filename, value)
                object.__setattr__(self, "dependency", dependency)
        return object.__setattr__(self, key, value)
