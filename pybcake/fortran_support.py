
__all__ = ["fortran_file_sort"]

class fortran_module:
    def __init__(self, module: str, filename: str, dependency: list):
        self.module = module
        self.filename = filename
        self.dependency = dependency
        self.entry_degree = 0


def find_mod(filename: str):
    modules = []
    with open(filename) as fp:
        file_using = []
        has_line_break = False
        line = fp.readline()
        status_in_module = False
        while line:
            line = line.split("!")[0]
            if line.strip() == "":
                line = fp.readline()
                continue
            if has_line_break:
                line += fp.readline().strip().lower()[1:]
            else:
                line = line.strip().lower()
                has_line_break = False
            if line[-1] == '&':
                line = line[:-1]
                has_line_break = True
                continue

            words = line.split()
            if words[0] == 'module':
                status_in_module = True
                modules.append(fortran_module(words[1], filename, []))            
            elif words[0] == 'use':
                if status_in_module:
                    modules[-1].dependency.append(words[1].split(',')[0])
                else:
                    file_using.append(words[1].split(',')[0])
            elif words[0] == 'end' and words[1] == 'module':
                status_in_module = False
            line = fp.readline()
        if file_using:
            modules.append(fortran_module("File_" + filename, filename, file_using))
    for mod in modules:
        mod.dependency = list(set(mod.dependency))
    return modules


def fortran_file_sort(files: list):
    modules = {}
    for f in files:
        for mod in find_mod(f):
            modules[mod.module] = mod

    for mod in modules.values():
        mod.dependency = [item for item in mod.dependency if item in modules]

    for mod in modules.values():
        mod.entry_degree = len(mod.dependency)
    ret_files = []
    time_left = len(modules)
    while time_left:
        file_in_same_depth = []
        for mod in modules.values():
            if mod.entry_degree != 0:
                continue
            if mod.filename in ret_files:
                raise ValueError("exist ring")
            time_left -= 1
            file_in_same_depth.append(mod.filename)
            for mod2 in modules.values():
                try:
                    mod2.dependency.remove(mod.module)
                    mod2.entry_degree -= 1
                except ValueError:
                    continue
            mod.entry_degree = -1
        file_in_same_depth = list({}.fromkeys(file_in_same_depth).keys())
        ret_files += file_in_same_depth
    return ret_files
