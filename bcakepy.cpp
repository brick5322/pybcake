#define PY_SSIZE_T_CLEAN
#define Py_LIMITED_API 3
#include <Python.h>
#include "BLogger.hpp"
#include <vector>

BLogger logger;
void add_current_path(PyObject* module_sys)
{
	PyObject* path = PyObject_GetAttrString(module_sys,"path");
	PyObject* append = PyObject_GetAttrString(path,"append");
	PyObject* result = PyObject_CallFunction(append,"s","./");
 	logger << result;	
	Py_XDECREF(path);
	Py_XDECREF(append);
	Py_XDECREF(result);
}

int main(int argc, char* argv[])
{
	if (argc < 2)
	{
		logger(LogLevel::Error) << "need work Method";
		return -1;
	}
	Py_Initialize();

	PyObject* module_sys = PyImport_ImportModule("sys");
	add_current_path(module_sys);
	PyObject* arg = PyList_New(argc - 2);
	std::vector<PyObject*> argi(argc - 2);
	PyObject_SetAttrString(module_sys, "argv", arg);
	for (int i = 2; i < argc; i++)
	{
		argi[i - 2] = PyUnicode_FromString(argv[i]);
		PyList_SetItem(arg, i - 2, argi[i - 2]);
	}

	PyObject* cur = PyImport_ImportModule("bcake");

	if (!cur)
	{
		logger(LogLevel::Error) << "bcake.py does not exist in the current directory";
		return -1;
	}
	PyObject* method = PyObject_GetAttrString(cur, argv[1]);
	if (!method)
	{
		logger(LogLevel::Error) << "work Method:" << argv[1] << " does not exist in bcake.py";
		return -1;
	}


	PyObject* args = PyTuple_New(0);
	PyObject* result = PyObject_Call(method, args, nullptr);

	for (auto i : argi)
		Py_XDECREF(i);
	Py_XDECREF(cur);
	Py_XDECREF(result);
	Py_XDECREF(arg);
	Py_XDECREF(args);
	Py_XDECREF(module_sys);
	Py_XDECREF(method);
	return 0;

}

