import pybcake as pbc
import os
import shutil

python_ver = "3.9"

config = [pbc.gcc.Release,"Release"]

try:
    if pbc.gcc.config == "Debug":
        config = [pbc.gcc.Debug,"Debug"]
except:
    pass

bcake = pbc.gcc.executable("bcake", ["./core/bcakepy.cpp"],
                           output_dir="core/x64/" + config[1] + "/core",
                           include_dirs=["/usr/include/python" + python_ver],
                           configuration=config[0],
                           libs=["python" + python_ver]
                           )

def release():
    bcake.make()
    os.system("mkdir -p deb_dir/usr/lib/python3/dist-packages")
    os.system("cp -r ./pybcake deb_dir/usr/lib/python3/dist-packages")
    os.system("cp ./core/bcake deb_dir/usr/bin")
    os.system("chmod 0755 ./deb_dir/DEBIAN")
    os.system("dpkg -b ./deb_dir .")


def install():
    bcake.make()
    os.system("sudo cp " + bcake.name + " /usr/bin")
    os.system("sudo rm -r /usr/lib/python3/dist-packages/pybcake/*")
    os.system("sudo cp -r ./pybcake /usr/lib/python3/dist-packages")

def clean():
    shutil.rmtree("x64/" + config[1])

# before you make and install ,uncommit this to make
# after that, you can commit this to test
# install()
