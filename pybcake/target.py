import os
import re
from threading import Thread
from threading import Semaphore
from .sourcefile import SourceFile


class Target:
    default_compilers = {
        ".cpp": "g++",
        ".c": "gcc",
        ".f90": "gfortran"
    }

    def __init__(self, source_files: list, target_name: str, target_type="exe"):
        if target_type != "exe" and target_type != "lib" and target_type != "so":
            raise ValueError("type should be \"exe\" or \"lib\" or \"so\"")
        self.obj_files = set([])
        self.run_command = None
        self.target_type = target_type
        self.compiler = None
        self.target_dir = "./"
        self.object_dir = "./obj"
        self.source_files = source_files
        self.include_dirs = []
        self.target_name = target_name
        self.definitions = []
        self.lib_dirs = []
        self.libs = []
        self.proj_dependencies = []
        self.options = []
        self.compilers = Target.default_compilers
        if target_type == "lib":
            if not re.findall("lib.*\\.a", target_name):
                self.target_name = "lib" + target_name + ".a"
        elif target_type == "so":
            if not re.findall("lib.*\\.so", target_name):
                self.target_name = "lib" + target_name + ".so"
        if target_type == "exe":
            self.run_command = self.target_dir + self.target_name

    def __setattr__(self, key, value):
        if key == "target_name":
            invalid = {'\\', '/', ':', '*', '?', '"', '<', '>', '|', ' '}
            value_set = set(value)
            if not value_set & invalid:
                return object.__setattr__(self, key, value)
            else:
                raise ValueError("target_name cannot contain special characters " + str(value_set & invalid))
        if key == "target_dir":
            target_dir = value
            if not target_dir.endswith("/"):
                target_dir += "/"
            if hasattr(self, "target_name") and hasattr(self, "target_dir"):
                if self.target_type == "exe":
                    if not callable(self.run_command) or self.run_command != self.target_dir + self.target_name:
                        object.__setattr__(self, "run_command", target_dir + self.target_name)
            return object.__setattr__(self, key, target_dir)
        elif key == "target_name":
            if hasattr(self, "target_name") and hasattr(self, "target_dir"):
                if self.target_type == "exe":
                    if not callable(self.run_command) or self.run_command != self.target_dir + self.target_name:
                        object.__setattr__(self, "run_command", self.target_dir + self.target_name)
        elif key == "object_dir":
            obj_dir = value
            if not obj_dir.endswith("/"):
                obj_dir += "/"
            return object.__setattr__(self, key, obj_dir)
        elif key == "source_files":
            src_files = []
            for i in value:
                if isinstance(i, str):
                    if not hasattr(self, "include_dirs"):
                        self.include_dirs = []
                    src_file = SourceFile(i, self.include_dirs)
                    src_files.append(src_file)
                if isinstance(i, SourceFile):
                    src_files.append(i)
            return object.__setattr__(self, key, src_files)
        elif key == "include_dirs":
            if not hasattr(self, "source_files"):
                return object.__setattr__(self, key, value)
            for i in self.source_files:
                assert isinstance(i, SourceFile)
                if i.include_dirs == self.include_dirs:
                    i.include_dirs = value
        return object.__setattr__(self, key, value)

    def make(self, nb_threads: int = 1):
        if nb_threads > 1:
            return multi_make(nb_threads, [self])

        if not self.compiler:
            raise ValueError("self.compiler is None and cannot be set automatically")
        for i in self.proj_dependencies:
            i.make()
        return self.make_self()

    def clean(self, reserve_target: bool = False):
        if os.path.exists(self.target_dir + self.target_name):
            if not reserve_target:
                try:
                    os.remove(self.target_dir + self.target_name)
                except FileNotFoundError:
                    pass
                try:
                    os.removedirs(self.target_dir)
                except OSError:
                    pass
        obj_names = set([])
        obj_dirs = set([])
        for (k, v) in self.compilers.items():
            for src_name in self.source_files:
                if src_name.filename.endswith(k):
                    if self.object_dir.endswith("/"):
                        obj_names.add(self.object_dir + src_name.filename[:-len(k)] + ".o")
                    else:
                        obj_names.add(self.object_dir + "/" + src_name.filename[:-len(k)] + ".o")
        for i in obj_names:
            obj_dirs.add(os.path.split(i)[0])
            try:
                os.remove(i)
                print("remove " + i)
            except FileNotFoundError:
                pass

        for i in obj_dirs:
            try:
                os.removedirs(i)
                print("remove directories" + i)
            except OSError:
                pass

    def run(self, run_command=None):
        try:
            print("\nrunning \"" +
                  run_command +
                  "\":\n" + os.popen(run_command + " 2>&1").read() +
                  "\n\n", end='')
        except TypeError:
            if callable(self.run_command):
                print("\nrunning \"" +
                      self.run_command(self) +
                      "\":\n" + os.popen(self.run_command(self) + " 2>&1").read() +
                      "\n\n", end='')
            elif self.run_command is not None:
                print("\nrunning \"" +
                      self.run_command +
                      "\":\n" + os.popen(self.run_command + " 2>&1").read() +
                      "\n\n", end='')
            else:
                raise ValueError("self.run_command is None and cannot be set automatically")

    def make_self(self):
        verify_dir(self.object_dir)
        obj_files = []
        for source in self.source_files:
            obj_files.append(self.update_obj(source))
        dependency_files = []
        for dependency in self.proj_dependencies:
            assert isinstance(dependency, Target)
            if dependency.target_type != "exe":
                dependency_files.append(dependency.target_dir + dependency.target_name)
        if target_is_latest(self.target_dir + self.target_name, obj_files + dependency_files):
            return self

        verify_dir(self.target_dir)
        if self.target_type == "exe":
            self.make_exe(obj_files)
        if self.target_type == "lib":
            self.make_lib(obj_files)
        if self.target_type == "so":
            self.make_so(obj_files)

        return self

    def update_obj(self, src_name: SourceFile):
        obj_name = None
        compiler = None
        for (k, v) in self.compilers.items():
            if src_name.filename.endswith(k):
                obj_name = src_name.filename[:-len(k)] + ".o"
                compiler = v
        if compiler is None:
            raise ValueError(src_name.filename + "cannot find matched compiler")
        if compiler == "g++":
            if not self.libs.count("stdc++"):
                self.libs.append("stdc++")
        self.obj_files.add(self.object_dir + obj_name)
        if target_is_latest(self.object_dir + obj_name, src_name.dependency + [src_name.filename]):
            return self.object_dir + obj_name

        verify_dir(os.path.split(self.object_dir + obj_name)[0])
        command = compiler + " -c -o " + self.object_dir + obj_name
        command += " "
        command += src_name.filename
        for inc_dir in self.include_dirs:
            command += " -I" + inc_dir
        for define in self.definitions:
            command += " -D" + define
        for opt in self.options:
            command += " " + opt
        print(command)
        print(os.popen(command + " 2>&1").read(), end='')
        return self.object_dir + obj_name

    def make_exe(self, obj_files):
        command = self.compiler + " -o " + self.target_dir + self.target_name
        for obj in obj_files:
            command += " "
            command += obj
        for lib_dir in self.lib_dirs:
            command += " -L" + lib_dir
        for lib in self.libs:
            command += " -l" + lib
        for opt in self.options:
            command += " " + opt
        print(command)
        print(os.popen(command + " 2>&1").read(), end='')

    def make_lib(self, obj_files: list):
        command = "ar rcs " + self.target_dir + self.target_name
        for file in obj_files:
            command += " "
            command += file
        print(command)
        print(os.popen(command + " 2>&1").read(), end='')

    def make_so(self, obj_files: list):
        command = self.compiler + "-fPIC -shared -o " + self.target_dir + self.target_name
        for obj in obj_files:
            command += " "
            command += obj
        for lib_dir in self.lib_dirs:
            command += " -L" + lib_dir
        for lib in self.libs:
            command += " -l" + lib
        for opt in self.options:
            command += " " + opt
        print(command)
        print(os.popen(command + " 2>&1").read(), end='')

    def add_dependency(self, dependency: object):
        if not self.proj_dependencies.count(dependency):
            self.proj_dependencies.append(dependency)


class MultiMake(Thread):
    def __init__(self, make_obj: Target, thr_sem: Semaphore):
        super().__init__()
        self.target = make_obj
        self.tar_name = make_obj.target_name
        self.tar_sem = Semaphore(len(self.target.source_files))

        def run_closure():
            for i in range(len(self.target.source_files)):
                self.tar_sem.acquire()
            thr_sem.acquire()
            self.target.make_self()

        self.run = run_closure


'''
    def run(self):
        self.target.make_self()
'''


class MultiUpdObj(Thread):
    def __init__(self, make_obj: Target, src_file: SourceFile, thr_sem: Semaphore, tar_sem: Semaphore):
        super().__init__()
        self.tar_name = src_file.filename
        tar_sem.acquire()

        def run_closure():
            thr_sem.acquire()
            make_obj.update_obj(src_file)
            tar_sem.release()
            thr_sem.release()

        self.run = run_closure


def multi_make(nb_thread: int, objs: list):
    make_works = []
    thr_sem = Semaphore(nb_thread)

    for tar in objs:
        tar_work = MultiMake(tar, thr_sem)
        make_works.append(tar_work)
        assert isinstance(tar, Target)
        for src in tar.source_files:
            make_works.append(MultiUpdObj(tar, src, thr_sem, tar_work.tar_sem))

    for i in make_works:
        if isinstance(i, MultiMake):
            for tar in i.target.proj_dependencies:
                tar_work = MultiMake(tar, thr_sem)
                make_works.append(MultiMake(tar, thr_sem))
                assert isinstance(tar, Target)
                for src in tar.source_files:
                    make_works.append(MultiUpdObj(tar, src, thr_sem, tar_work.tar_sem))

    make_works = make_works[::-1]
    for i in make_works:
        i.start()
    for i in make_works:
        i.join()


'''
    alive_thread_count = len(make_works) if nb_thread > len(make_works) else nb_thread

    for i in range(alive_thread_count):
        make_works[i].start()
    while alive_thread_count:
        j = 0
        while j < alive_thread_count:
            if not make_works[j].is_alive():
                make_works.pop(j)
                if len(make_works) >= alive_thread_count:
                    make_works[alive_thread_count - 1].start()
                else:
                    alive_thread_count -= 1
            j += 1
'''


def target_is_latest(target_file: str, dependency: list) -> bool:
    if not os.path.exists(target_file):
        return False
    target_mtime = os.path.getmtime(target_file)
    for dependency_file in dependency:
        if not os.path.exists(dependency_file):
            return False
        if os.path.getmtime(dependency_file) > target_mtime:
            return False
    return True


def verify_dir(directory: str):
    try:
        os.makedirs(directory)
    except FileExistsError:
        pass
