from .target import Target


def gcc_exe(source: list, target_name, **kwargs) -> Target:
    target = Target(source, target_name, "exe")
    target.compiler = "gcc"
    target.compilers = {
        ".cpp": "g++",
        ".c": "gcc",
        ".f90": "gfortran"
    }

    for k, v in kwargs.items():
        if hasattr(target, k):
            target.__setattr__(k, v)
        if k == "mode":
            if v == "Debug" or v == "debug":
                target.object_dir = "./Debug"
                target.definitions.append("_DEBUG")
                target.options.append("-O0")
                target.options.append("-g")
            elif v == "Release" or v == "release":
                target.object_dir = "./Release"
                target.definitions.append("NDEBUG")
                target.options.append("-O3")
    return target


def gcc_lib(source: list, target_name, **kwargs) -> Target:
    target = Target(source, target_name, "lib")
    target.compiler = "gcc"
    target.compilers = {
        ".cpp": "g++",
        ".c": "gcc",
        ".f90": "gfortran"
    }
    for k, v in kwargs.items():
        if hasattr(target, k):
            target.__setattr__(k, v)
        if k == "mode":
            if v == "Debug" or v == "debug":
                target.object_dir = "./Debug"
                target.definitions.append("_DEBUG")
                target.options.append("-O0")
                target.options.append("-g")
            elif v == "Release" or v == "release":
                target.object_dir = "./Release"
                target.definitions.append("NDEBUG")
                target.options.append("-O3")
            else:
                target.object_dir = "./Debug"
                target.definitions.append("_DEBUG")
                target.options.append("-O0")
                target.options.append("-g")
    return target
