import pybcake as pbm
import os

def release():
    bcake = pbm.gcc_exe(["bcakepy.cpp"],"bcake",target_dir = "./deb_dir/usr/bin",mode="release",include_dirs = ["/usr/include/python3.9"],libs = ["python3.9"])
    bcake.make()
    bcake.clean(reserve_target=True)
    os.system("mkdir -p deb_dir/usr/lib/python3/dist-packages")
    os.system("cp -r ./pybcake deb_dir/usr/lib/python3/dist-packages")
    os.system("dpkg -b ./deb_dir .")

