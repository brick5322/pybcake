from ..c_cpp.methods import * 
from ..target import *
from ..generator import *

class CompileGen(Generator):
    def __init__(self,
                 include_dirs=None,
                 definitions=None,
                 additional_options=None
                 ):
        super().__init__()
        if additional_options is None:
            additional_options = []
        if definitions is None:
            definitions = []
        if include_dirs is None:
            include_dirs = []
        self.definitions = definitions
        self.include_dirs = include_dirs
        self.options = additional_options

    def __call__(self, target: Target, cmd: str = ""):
        cmd = target.command
        cmd += " -c -o " + target.name + " "

        for inc in self.include_dirs:
            if isinstance(inc,str):
                cmd += "-I" + inc + " "

        for define in self.definitions:
            if isinstance(define,str):
                cmd += "-D" + define + " "

        for src in target.sources:
            if isinstance(src,str):
                cmd += src + " "

        for opt in self.options:
            if isinstance(opt,str):
                cmd += opt + " "

        return cmd


class BinGen(Generator):
    def __init__(self,
                 lib_dirs=None,
                 libs=None,
                 ):
        super().__init__()
        if lib_dirs is None:
            lib_dirs = []
        if libs is None:
            libs = []

        self.libs = libs
        self.lib_dirs = lib_dirs

    def __call__(self, target, cmd: str = ""):
        cmd = target.command + " "
        cmd += "-o " + target.name + " "

        for src in target.sources:
            if isinstance(src,str):
                cmd += src + " "

        for lib_dir in self.lib_dirs:
            if isinstance(lib_dir,str):
                cmd += "-L" + lib_dir + " "

        for lib in self.libs:
            if isinstance(lib,str):
                cmd += "-l" + lib + " "

        for opt in self.options:
            if isinstance(opt,str):
                cmd += opt + " "

        return cmd


def LibGen(target: Target, cmd: str = ""):
    cmd = ""
    if target.command is None:
        cmd += "ar rcs "
    else:
        cmd += target.command + " "

    cmd += target.name + " "

    for src in target.sources:
        if isinstance(src,str):
            cmd += src + " "

    return cmd


class SharedGen(Generator):
    def __init__(self,
                 lib_dirs=None,
                 libs=None,
                 ):
        super().__init__()
        if lib_dirs is None:
            lib_dirs = []
        if libs is None:
            libs = []
        self.libs = libs
        self.lib_dirs = lib_dirs
        self.options.append("-fPIC")
        self.options.append("-shared")

    def __call__(self, target, cmd: str = ""):
        cmd = target.command + " "
        cmd += "-o " + target.name + " "

        for src in target.sources:
            if isinstance(src,str):
                cmd += src + " "

        for dirs in self.lib_dirs:
            if isinstance(dirs,str):
                cmd += "-L" + dirs + " "

        for lib in self.libs:
            if isinstance(lib,str):
                cmd += "-l" + lib + " "

        for opt in self.options:
            if isinstance(opt,str):
                cmd += opt + " "

        return cmd


Debug = {
    "definitions": ["_DEBUG"],
    "options": ["-O0", "-g"]
}

Release = {
    "definitions": ["NDEBUG"],
    "options": ["-O3"]
}


class FortPostGen(Generator):
    def __init__(self, mod_dir: str):
        super().__init__()
        self.mod_dir = mod_dir

    def __call__(self, target, cmd: str = ""):
        try:
            os.makedirs(self.mod_dir)
        except OSError:
            pass

        cmd += "-J" + self.mod_dir + " "
        for opt in self.options:
            if isinstance(opt,str):
                cmd += opt + " "
        return cmd

class HeaderCompilePreGen(Generator):
    def __init__(self, inc_dirs = None):
        if inc_dirs is None:
            inc_dirs = []
        self.include_dirs = inc_dirs
        super().__init__()
    
    def __call__(self, target, cmd: str = ""):
        for filename in target.sources:
            if isinstance(filename,str):
                target.dep_files += find_c_dependency(filename,self.include_dirs)

__all__ = ["Release", "Debug", "LibGen", "SharedGen",
           "CompileGen", "BinGen", "FortPostGen",
           "HeaderCompilePreGen"]
