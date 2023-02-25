import re
from ..target import Target
from ..group import Group
from .gcc_generator import *
from .fortran_deps import *


def lib(target_name: str, sources: list, output_dir=None, obj_dir=None, include_dirs=None, definitions=None,
        additional_options=None, mod_dir=None, configuration=None,
        lib_gen=GccLibGenerator,
        c_compile_gen=None,
        cpp_compile_gen=None,
        c_precompile_gen=None,
        fortran_compile_gen=None):

    if c_compile_gen is None:
        c_compile_gen = GccCompileGenerator()
    if cpp_compile_gen is None:
        cpp_compile_gen = GccCompileGenerator()
    if c_precompile_gen is None:
        c_precompile_gen = HeaderCompilePreGenerator()
    if fortran_compile_gen is None:
        fortran_compile_gen = GccCompileGenerator()
        
    if additional_options is None:
        additional_options = []
    assert isinstance(additional_options, list)

    if definitions is None:
        definitions = []
    assert isinstance(definitions, list)

    if include_dirs is None:
        include_dirs = []
    assert isinstance(include_dirs, list)

    if configuration is None:
        configuration = {}
    assert isinstance(configuration, dict)

    if output_dir is None:
        output_dir = ""
    else:
        try:
            os.makedirs(output_dir)
        except OSError:
            pass

    if not output_dir.endswith("/"):
        output_dir = output_dir + "/"

    if obj_dir is None:
        obj_dir = ""
    elif not obj_dir.endswith("/"):
        obj_dir = obj_dir + "/"

    if not re.findall(r"lib.*\.a", target_name):
        target_name = "lib" + target_name + ".a"
    target_name = output_dir + target_name

    ret_lib = Target(target_name)
    ret_lib.command = "ar rcs"
    ret_lib.generate = lib_gen
    c_targets = []
    cpp_targets = []
    fortran_files = []

    options = {
        "include_dirs": include_dirs,
        "definitions": definitions,
        "additional_options": additional_options
    }
    cpp_compile_gen += options
    cpp_compile_gen += configuration
    c_compile_gen += options
    c_compile_gen += configuration

    c_precompile_gen += options

    for file in sources:
        assert isinstance(file, str)
        if file.endswith(".cpp"):
            target = Target(obj_dir + file[:-4] + '.o')
            target.sources.append(file)
            target.command = "g++"
            target.generate = cpp_compile_gen
            cpp_targets.append(target)
        elif file.endswith(".c"):
            target = Target(obj_dir + file[:-2] + '.o')
            target.sources.append(file)
            target.command = "gcc"
            target.generate = c_compile_gen
            c_targets.append(target)
        elif file.endswith(".f90"):
            fortran_files.append(file)
        else:
            raise TypeError("undefined filetype suffix")

    if c_targets:
        group = Group("CFiles")
        group.targets = c_targets
        group.pre_generate.append(c_precompile_gen)
        ret_lib.sources.append(group)

    if cpp_targets:
        group = Group("CPPFiles")
        group.targets = cpp_targets
        group.pre_generate.append(c_precompile_gen)
        ret_lib.sources.append(group)

    fortran_compile_gen += {
        "include_dirs": [mod_dir],
        "definitions": definitions,
        "additional_options": additional_options
    }
    fortran_compile_gen += configuration

    def fortran_initializer(filename: str):
        f_target = Target(obj_dir + filename[:-4] + '.o')
        f_target.sources.append(filename)
        f_target.command = "gfortran"
        f_target.generate = fortran_compile_gen
        return f_target

    if fortran_files:
        ret_lib.sources += fortran_file_sort(fortran_files, fortran_initializer)



    return ret_lib


def executable(target_name: str, sources: list,
               output_dir=None,
               obj_dir=None,
               include_dirs=None,
               definitions=None,
               additional_options=None,
               mod_dir=None,
               lib_dirs=None,
               libs=None,
               configuration=None,
               c_compile_gen=None,
               cpp_compile_gen=None,
               c_precompile_gen=None,
               fortran_compile_gen=None,
               executable_gen=None
               ):

    if c_compile_gen is None:
        c_compile_gen = GccCompileGenerator()
    if cpp_compile_gen is None:
        cpp_compile_gen = GccCompileGenerator()
    if c_precompile_gen is None:
        c_precompile_gen = HeaderCompilePreGenerator()
    if fortran_compile_gen is None:
        fortran_compile_gen = GccCompileGenerator()
    if executable_gen is None:
        executable_gen = GccBinGenerator()

    if configuration is None:
        configuration = {}
    assert isinstance(configuration, dict)

    if additional_options is None:
        additional_options = []
    assert isinstance(additional_options, list)

    if definitions is None:
        definitions = []
    assert isinstance(definitions, list)

    if include_dirs is None:
        include_dirs = []
    assert isinstance(include_dirs, list)

    if lib_dirs is None:
        lib_dirs = []
    assert isinstance(lib_dirs, list)

    if libs is None:
        libs = []
    assert isinstance(libs, list)

    if output_dir is None:
        output_dir = ""
    else:
        try:
            os.makedirs(output_dir)
        except OSError:
            pass
    if not output_dir.endswith("/"):
        output_dir = output_dir + "/"

    if obj_dir is None:
        obj_dir = ""
    elif not obj_dir.endswith("/"):
        obj_dir = obj_dir + "/"

    executable_gen += {
        "lib_dirs": lib_dirs,
        "libs": libs
    }

    target_name = output_dir + target_name

    ret_bin = Target(target_name)
    ret_bin.command = "gcc "
    ret_bin.generate = executable_gen

    c_targets = []
    cpp_targets = []
    fortran_files = []

    options = {
        "include_dirs": include_dirs,
        "definitions": definitions,
        "additional_options": additional_options
    }
    cpp_compile_gen += options
    cpp_compile_gen += configuration
    c_compile_gen += options
    c_compile_gen += configuration

    c_precompile_gen += options

    for file in sources:
        assert isinstance(file, str)
        if file.endswith(".cpp"):
            target = Target(obj_dir + file[:-4] + '.o')
            target.sources.append(file)
            target.command = "g++"
            target.generate = cpp_compile_gen
            cpp_targets.append(target)
        elif file.endswith(".c"):
            target = Target(obj_dir + file[:-2] + '.o')
            target.sources.append(file)
            target.command = "gcc"
            target.generate = c_compile_gen
            c_targets.append(target)
        elif file.endswith(".f90"):
            fortran_files.append(file)
        else:
            raise TypeError("undefined filetype suffix")

    if c_targets:
        group = Group("CFiles")
        group.targets = c_targets
        group.pre_generate.append(c_precompile_gen)
        ret_bin.sources.append(group)
    if cpp_targets:
        group = Group("CPPFiles")
        group.targets = cpp_targets
        group.pre_generate.append(c_precompile_gen)
        ret_bin.sources.append(group)
        ret_bin.generate += {
            "libs": ["stdc++"]
        }

    fortran_compile_gen += {
        "include_dirs": [mod_dir],
        "definitions": definitions,
        "additional_options": additional_options
    }
    fortran_compile_gen += configuration

    def fortran_initializer(filename: str):
        f_target = Target(obj_dir + filename[:-4] + '.o')
        f_target.sources.append(filename)
        f_target.command = "gfortran"
        f_target.generate = fortran_compile_gen
        return f_target

    if fortran_files:
        ret_bin.sources += fortran_file_sort(fortran_files, fortran_initializer)
        ret_bin.generate.libs.append("gfortran")

    return ret_bin
