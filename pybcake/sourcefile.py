import os

class SourceFile:
    find_deps_funcs = {}
    def __init__(self, filename: str, include_dirs: list):
        self.dependency = []
        self.filename = filename
        self.include_dirs = include_dirs

    def __setattr__(self, key, value):
        dependency = []
        if key == "include_dirs":
            src_dir, src_name = os.path.split(self.filename)
            try :
                dependency += SourceFile.find_deps_funcs["."+src_name.split(".")[-1]](self.filename,value)
                object.__setattr__(self, "dependency", dependency)
            except KeyError:
                pass
        return object.__setattr__(self, key, value)
