import json
import os

tasks = []
configs = []

class Task():
    def __init__(self,label:str,args:list,isDefault:bool = False):
        self.label = label
        self.type = "shell"
        self.command = "bcake"
        self.args = args
        if isDefault:
            self.group = {
                "kind" : "build",
                "isDefault" : True
            }

class GccConfig():
    def __init__(self,name:str,program:str,args:list=[],debugger_path:str="/usr/bin/gdb"):
        self.name = name
        self.type = "cppdbg"
        self.request = "launch"
        self.program = "${workspaceRoot}/" + program
        self.args = args
        self.cwd = "${workspaceRoot}"
        self.stopAtEntry = False
        self.environment = []
        self.externalConsole = False
        self.MIMode = "gdb"
        self.miDebuggerPath = debugger_path

def add_task(label:str,args:list,isDefault:bool = False):
    tasks.append(Task(label,args,isDefault).__dict__)

def add_config(config):
    configs.append(config.__dict__)

def dump_tasks(filepath:str = ".vscode/tasks.json"):
    with open(filepath,"w") as fp:
        json.dump({"tasks":tasks},fp,indent=4)

def dump_launch(filepath:str = ".vscode/launch.json"):
    with open(filepath,"w") as fp:
        json.dump({"configurations":configs},fp,indent=4)

def vscode_init():
    if not os.path.exists(".vscode"):
        os.mkdir(".vscode")
    dump_tasks()
    dump_launch()

__all__ = ["vscode_init","GccConfig","add_task","add_config"]
