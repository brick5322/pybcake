import re
from ..target import Target
from ..group import Group
from .generator import *
from ..fortran.methods import *
from copy import copy


def lib(target_name: str, sources: list, output_dir=None, obj_dir=None, include_dirs=None, definitions=None,
        additional_options=None, mod_dir=None, configuration=None,
        lib_gen=LibGen,
        c_compile_gen=CompileGen(),
        cpp_compile_gen=CompileGen(),
        c_precompile_gen=HeaderCompilePreGen(),
        fortran_compile_gen=CompileGen()
        ):
    c_compile_gen = copy(c_compile_gen)
    cpp_compile_gen = copy(cpp_compile_gen)
    c_precompile_gen = copy(c_precompile_gen)
    fortran_compile_gen = copy(fortran_compile_gen)

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
        output_dir = "."
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
               c_compile_gen=CompileGen(),
               cpp_compile_gen=CompileGen(),
               c_precompile_gen=HeaderCompilePreGen(),
               fortran_compile_gen=CompileGen(),
               executable_gen=BinGen()
               ):
    c_compile_gen = copy(c_compile_gen)
    cpp_compile_gen = copy(cpp_compile_gen)
    c_precompile_gen = copy(c_precompile_gen)
    fortran_compile_gen = copy(fortran_compile_gen)
    executable_gen = copy(executable_gen)

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
        output_dir = "."
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
        ret_bin.generate += {
            "libs": ["gfortran"]
        }

    return ret_bin


def share(target_name: str, sources: list,
          output_dir=None,
          obj_dir=None,
          include_dirs=None,
          definitions=None,
          additional_options=None,
          mod_dir=None,
          lib_dirs=None,
          libs=None,
          configuration=None,
          c_compile_gen=CompileGen(),
          cpp_compile_gen=CompileGen(),
          c_precompile_gen=HeaderCompilePreGen(),
          fortran_compile_gen=CompileGen(),
          shared_gen=SharedGen()
          ):
    c_compile_gen = copy(c_compile_gen)
    cpp_compile_gen = copy(cpp_compile_gen)
    c_precompile_gen = copy(c_precompile_gen)
    fortran_compile_gen = copy(fortran_compile_gen)
    shared_gen = copy(shared_gen)

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
        output_dir = "."
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

    shared_gen += {
        "lib_dirs": lib_dirs,
        "libs": libs
    }
    if not re.findall(r"lib.*\.so", target_name):
        target_name = "lib" + target_name + ".so"
    target_name = output_dir + target_name

    ret_shared = Target(target_name)
    ret_shared.command = "gcc "
    ret_shared.generate = shared_gen

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
        ret_shared.sources.append(group)
    if cpp_targets:
        group = Group("CPPFiles")
        group.targets = cpp_targets
        group.pre_generate.append(c_precompile_gen)
        ret_shared.sources.append(group)
        ret_shared.generate += {
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
        ret_shared.sources += fortran_file_sort(fortran_files, fortran_initializer)
        ret_shared.generate.libs.append("gfortran")
        ret_shared.generate += {
            "libs": ["gfortran"]
        }

    return ret_shared
