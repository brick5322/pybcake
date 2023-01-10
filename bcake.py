import pybcake as pbc
import os


def equal_to_default(target):
    assert isinstance(target, pbc.Target)
    return target.target_dir + target.target_name


python_ver = "3.9"
bcake = pbc.gcc_exe(pbc.find_file(".", ["cpp"]), "bcake", target_dir="./deb_dir/usr/bin", mode="release",
                    include_dirs=["/usr/include/python" + python_ver], libs=["python" + python_ver])


def release():
    bcake.run_command = equal_to_default
    bcake.make()
    bcake.clean(reserve_target=True)
    os.system("mkdir -p deb_dir/usr/lib/python3/dist-packages")
    os.system("cp -r ./pybcake deb_dir/usr/lib/python3/dist-packages")
    os.system("chmod 0755 ./deb_dir/DEBIAN")
    os.system("dpkg -b ./deb_dir .")


def install():
    bcake.make()
    os.system("sudo rm /usr/lib/python3/dist-packages/pybcake/*")
    os.system("sudo cp -r ./pybcake /usr/lib/python3/dist-packages")
    bcake.run()
    bcake.clean(reserve_target=True)


def multi():
    bcake.make(4)
    os.system("sudo rm /usr/lib/python3/dist-packages/pybcake/*")
    os.system("sudo cp -r ./pybcake /usr/lib/python3/dist-packages")
    bcake.run()
    bcake.clean(reserve_target=True)

# before you make and install ,uncommit this to make
# after that, you can commit this to test
# install()
