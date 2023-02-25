# pybcake

linux下构建工具

## 特点

1. 支持gcc、gfortran，并保持编译器可扩展
2. 支持多线程编译
3. 一项工程只需要一份bcake.py
4. 使用stable pythonCAPI，支持更多版本python的编译（示例使用python3.9）

## 如何使用

**bcake <u>work_method</u> [options]**

例如：`bcake install`

`work method`:bcake.py中的方法

`options`:传入bcake.py的参数，可以调用`argprase`，实现更多功能

在项目文件下创建一个`bcake.py`脚本。

```python
# bcake.py
import pybcake as pbc
import os

python_ver = "3.9"

bcake = pbc.gcc.executable("bcake", ["./core/bcakepy.cpp"],
                           output_dir="./core",
                           include_dirs=["/usr/include/python" + python_ver],
                           configuration=pbc.gcc.Release,
                           libs=["python" + python_ver]
                           )


def release():
    bcake.make()
    os.system("mkdir -p deb_dir/usr/lib/python3/dist-packages")
    os.system("cp -r ./pybcake deb_dir/usr/lib/python3/dist-packages")
    os.system("chmod 0755 ./deb_dir/DEBIAN")
    os.system("dpkg -b ./deb_dir .")


def install():
    bcake.make()
    os.system("sudo rm -r /usr/lib/python3/dist-packages/pybcake/*")
    os.system("sudo cp -r ./pybcake /usr/lib/python3/dist-packages")

# before you make and install ,uncommit this to make
# after that, you can commit this to test
# install()


```

其中`release`函数，是我们编写的一个编译命令，可以看到，我们首先是生成了使用`release`模式的`bcake`文件。当然，我们可以直接使用 `python -i bcake.py`然后进入`python`命令行执行`release()`来编译。

have fun！

