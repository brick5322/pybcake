from .target import Target

gcc_compilers = {
    ".cpp": "g++",
    ".c": "gcc",
    ".f90": "gfortran"
}

gcc_opt_templates = {
    "Debug": {
        "definitions": ["_DEBUG"],
        "options": ["-g", "-O0"]},
    "Release": {
        "definitions": ["NDEBUG"],
        "options": ["-O3"]},
}


def gcc_exe(source: list, target_name, **kwargs) -> Target:
    target = Target(source, target_name, "exe")
    target.compiler = "gcc"
    target.target_dir = "bin"
    target.compilers = gcc_compilers
    for k, v in kwargs.items():
        if hasattr(target, k):
            target.__setattr__(k, v)
        elif k == "mode":
            if isinstance(v, dict):
                target += v
            elif v == "Debug" or v == "Release":
                target.object_dir = "obj/" + v
                target += gcc_opt_templates[v]
    return target


def gcc_lib(source: list, target_name, **kwargs) -> Target:
    target = Target(source, target_name, "lib")
    target.compiler = "gcc"
    target.target_dir = "lib"
    target.compilers = gcc_compilers
    for k, v in kwargs.items():
        if hasattr(target, k):
            target.__setattr__(k, v)
        elif k == "mode":
            if isinstance(v, dict):
                target += v
            elif v == "Debug" or v == "Release":
                target.object_dir = v
                target += gcc_opt_templates[v]
    return target
