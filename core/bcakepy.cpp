#include <Python.h>
#include <iostream>
#include <utility>
#include <string>
#include <cstring>
#include <vector>

#include "BLogger.hpp"

using namespace std;

void add_current_path()
{
    PyObject* module_sys = PyImport_ImportModule("sys");
    PyObject* path = PyObject_GetAttrString(module_sys,"path");
    PyObject* append = PyObject_GetAttrString(path,"append");
    PyObject* result = PyObject_CallFunction(append,"s",".");
    Py_XDECREF(path);
    Py_XDECREF(append);
    Py_XDECREF(result);
    Py_XDECREF(module_sys);
}

using kwpair = pair<string,string>;

vector<kwpair> arg_split(int argc,char** argv)
{
    vector<kwpair> ret;

    for(int i = 0;i < argc;i++)
    {
        char* arg = argv[i];
        int len = strlen(arg);

        if((arg[0] == '-' && arg[1] == '-') || arg[0] != '-')
        {
            int start_pos = arg[0] == '-' ? 2 : 0;
            kwpair kwarg;
            kwarg.first = string(arg + start_pos);
            for(int i = start_pos;i < len;i++)
            {
                if(arg[i] != '=')
                    continue;
                kwarg.first = string(arg + start_pos,i - start_pos);

                int value_len = len - i - 1 > 0 ? len - i - 1 : 0;
                if(value_len)
                    kwarg.second = string(arg + i + 1,value_len);

                break;
            }
            ret.push_back(kwarg);
        }
        else if(arg[0] == '-')
        {
            if(arg[2] >= '0' && arg[2] <= '9')
                ret.push_back(kwpair(string(arg + 1,1),string(arg + 2)));
            else
                for(int i = 1;i < len;i++)
                    ret.push_back(kwpair(string(arg + i,1),string()));
        }
    }
    return ret;
}

int main(int argc,char** argv)
{
    vector<kwpair> args = (argc == 2 ? vector<kwpair>():arg_split(argc - 2,argv + 2));
    PyObject* pyargs = NULL;
    PyObject* bcake = NULL;
    PyObject* arg_list = NULL;
    PyObject* cmd_method = NULL;
    PyObject* cmd = NULL;

    Py_Initialize();
    add_current_path();

    pyargs = PyImport_ImportModule("pybcake.args");
    if(!pyargs)
        goto pyargs_err;

    if(argc > 1)
        PyObject_SetAttrString(pyargs,"command",PyUnicode_InternFromString(argv[1]));

    arg_list = PySet_New(0);
    if(!arg_list)
        goto arg_list_err;
    
    for(auto&arg : args)
    {
        if(arg.second.empty())
            PySet_Add(arg_list,PyUnicode_InternFromString(arg.first.data()));
        else
        {
            PyObject* obj = PyLong_FromString(arg.second.data(),NULL,0);
            if(!obj)
            {
                PyErr_Clear();
                obj = PyUnicode_InternFromString(arg.second.data());
                if(!obj)
                    goto arg_str_convert_err;
                PyObject* pyfloat = PyFloat_FromString(obj);
                if(!pyfloat)
                    PyErr_Clear();
                else
                {
                    Py_DECREF(obj);
                    obj = pyfloat;
                }
            }
            PyObject_SetAttrString(pyargs,arg.first.data(),obj);
        }
    }
    PyObject_SetAttrString(pyargs,"arg_list",arg_list);

    bcake = PyImport_ImportModule("bcake");
    if(!bcake)
        goto bcake_err;

    cmd = PyObject_GetAttrString(pyargs,"command");
    if(!cmd)
        goto cmd_err;
    logger(LogLevel::Info) << "Doing Task \'\033[33m" << PyUnicode_AsUTF8(cmd) << "\033[0m\'";
    cmd_method = PyObject_GetAttr(bcake,cmd);
    if(!cmd_method)
        goto command_err;

    Py_XDECREF(PyObject_CallNoArgs(cmd_method));
    if(PyErr_Occurred())
        goto call_err;
    logger(LogLevel::Info) << "Task Finish";

    
    Py_DECREF(cmd_method);
    Py_DECREF(cmd);
    Py_DECREF(bcake);
    Py_DECREF(arg_list);
    Py_DECREF(pyargs);
    Py_Finalize();
    return 0;

call_err:
    Py_DECREF(cmd_method);
command_err:
    Py_DECREF(cmd);
cmd_err:
    Py_DECREF(bcake);
bcake_err:
    Py_DECREF(arg_list);
arg_str_convert_err:
arg_list_err:
    Py_DECREF(pyargs);
pyargs_err:
    logger(LogLevel::Critical) << "Error Occured:";
    PyErr_Print();
    Py_Finalize();
    return -1;
}

