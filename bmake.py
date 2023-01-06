import pybmake as pbm
import os

def release():
    bmake = pbm.gcc_exe(["bmakepy.cpp"],"bmake",target_dir = "./deb_dir/usr/bin",mode="release",include_dirs = ["/usr/include/python3.9"],libs = ["python3.9"])
    bmake.make()
    bmake.clean(reserve_target=True)
    os.system("mkdir -p deb_dir/usr/lib/python3/dist-packages")
    os.system("cp -r ./pybmake deb_dir/usr/lib/python3/dist-packages")
    os.system("dpkg -b ./deb_dir .")

