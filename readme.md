# pybcake

linux下构建工具

## 特点

1. 逐源代码查找include依赖
2. 可扩展性。上一个项目的编译脚本，可以轻松的在封装后带到下一个脚本
3. 使用stable pythonCAPI，支持更多版本python的编译（示例使用python3.9）

## 如何使用



**bcake <u>work_method</u> [options]**



`work method`:

`options`:

在项目文件下创建一个`bcake.py`脚本。

```python
# bcake.py
import pybcake as pbc
import os


def release():
    python_ver = "3.9"
    bcake = pbc.gcc_exe(["bcakepy.cpp"], "bcake", target_dir="./deb_dir/usr/bin", mode="release",
                        include_dirs=["/usr/include/python" + python_ver], libs=["python" + python_ver])
    bcake.make()
    bcake.clean(reserve_target=True)
    os.system("mkdir -p deb_dir/usr/lib/python3/dist-packages")
    os.system("cp -r ./pybcake deb_dir/usr/lib/python3/dist-packages")
    os.system("dpkg -b ./deb_dir .")

```

其中`release`函数，是我们编写的一个编译命令，可以看到，我们首先是生成了使用`release`模式的`bcake`文件。当然，我们可以直接使用 `python -i bcake.py`然后进入`python`命令行执行`release()`来编译，但是我们更推荐在编译安装了`bcake`后，使用`bcake release`。

`release`方法中的`backe`变量，实际上是`pybcake`包下的`Target`变量，我们通过`gcc_exe`生成的`Target`对象来构建我们的目标文件。

`make`方法可以传入参数`run=True`，可在编译后立即运行，默认为执行`target_dir+target_name`组成的命令，也可以修改`Target.run_command`为`str`或以`str`为返回值，参数为（`Target`类型）的函数

`clean`方法会删除目标文件、`object_dir`和其中所有的文件。可以传入参数`reserve_target=True`,来保留目标文件。



have fun！

