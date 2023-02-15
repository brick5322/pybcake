from ..target import *
from ..generator import *


class GccCompileGenerator(Generator):
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
            cmd += "-I" + inc + " "

        for define in self.definitions:
            cmd += "-D" + define + " "

        for src in target.sources:
            cmd += src + " "

        for opt in self.options:
            cmd += opt + " "

        return cmd


class GccBinGenerator(Generator):
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
            cmd += src + " "

        for dirs in self.lib_dirs:
            cmd += "-L" + dirs + " "

        for lib in self.libs:
            cmd += "-l" + lib + " "

        for opt in self.options:
            cmd += opt + " "

        return cmd


def GccLibGenerator(target: Target, cmd: str = ""):
    cmd = ""
    if target.command is None:
        cmd += "ar rcs "
    else:
        cmd += target.command + " "

    cmd += target.name + " "

    for src in target.sources:
        cmd += src + " "

    return cmd


class GccSharedGenerator(Generator):
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
        self.options += "-fPIC"
        self.options += "-shared"

    def __call__(self, target, cmd: str = ""):
        cmd = target.command + " "
        cmd += "-o " + target.name + " "

        for src in target.sources:
            cmd += src + " "

        for dirs in self.lib_dirs:
            cmd += "-L" + dirs + " "

        for opt in self.options:
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


class GfortranPostGenerator(Generator):
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
            cmd += opt + " "
        return cmd


__all__ = ["Release", "Debug", "GccLibGenerator", "GccSharedGenerator",
           "GccCompileGenerator", "GccBinGenerator", "GfortranPostGenerator"]