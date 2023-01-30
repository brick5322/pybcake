import os

def exec_subdir(directory:str,command:str,argvs=[]):
    cmd = "cd " + directory + "; bcake " + command
    for argv in argvs:
        cmd += " " + argv
    print(cmd)
    return os.system(cmd)
