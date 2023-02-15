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
