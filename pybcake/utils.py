import os
import re
import json

__all__ = ["find_file","find_pkg","get_jsonset","environment"]

def find_file(from_dir: str, suffix=None, recursive: bool = False):
    file = []
    if not suffix:
        return file
    if recursive:
        for root, _, files in os.walk(from_dir):
            for f in files:
                file.append(root + "/" + f)
    else:
        if not from_dir.endswith("/"):
            from_dir += "/"
        for f in os.listdir(from_dir):
            if os.path.isfile(os.path.abspath(from_dir + f)):
                file.append(from_dir + f)
    assert isinstance(suffix, list)
    ret = []
    for i in file:
        for j in suffix:
            if j[0] == '.':
                j = j.split('.')[-1]
            if re.search(".*\\." + j + "$", i):
                ret.append(i)
                continue
    return ret

def find_pkg(pkg_name: str, cflags=True, lib_dirs=True, libs=True):
    ret = {
        "cflags": [],
        "libs": [],
        "lib_dirs": []
    }
    tmp_strs = os.popen("pkg-config --cflags --libs " + pkg_name).read().split(' ')
    if not tmp_strs:
        return ret
    tmp_strs[-1] = tmp_strs[-1][:-1]
    for i in tmp_strs:
        if len(i) < 2:
            continue
        elif i[1] == 'I':
            ret["cflags"].append(i[2:])
        elif i[1] == 'L':
            ret["lib_dirs"].append(i[2:])
        elif i[1] == 'l':
            ret["libs"].append(i[2:])
    return ret

def exec_subdir(directory:str,command:str,argvs=[]):
    cmd = "cd " + directory + "; bcake " + command
    for argv in argvs:
        cmd += " " + argv
    print(cmd)
    return os.system(cmd)

def get_jsonset(filename:str = "./settings.json",key = None):
    if hasattr(get_jsonset,"settings"):
        if key:
            try:
                return settings[key]
            except KeyError:
                pass
    else:
        get_jsonset.settings = {}

    with open(filename) as fp:
        settings = json.load(fp)
        if key == None:
            return settings
        else:
            return settings[key]

class environment:
    def __init__(self,cmd:str,**kwargs):
        self.command = cmd
        self.env = {}
        for k,v in kwargs.items():
            if isinstance(v,(list,tuple)) and v:
                value = ":"
                for s in v:
                    if v[0] == ":":
                        value += s
                    else:
                        value += ":" + s
                self.env[k] = value
            elif isinstance(v,str):
                if v[0] == ":":
                    self.env[k] = v
                else:
                    self.env[k] = ":" + v
                
    def run(self):
        for k,v in self.env.items():
            try:
                os.environ[k] += v
            except KeyError:
                os.environ[k] = v[1:] 
        return os.system(self.command)

    def dump(self,shname:str):
        with open(shname,"w") as fp:
            for k,v in self.env.items():
                fp.write("export " + k + "=$" + k + v + "\n") 
            fp.write(self.command + "\n")
